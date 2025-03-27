#!/usr/bin/env python3
# server.py
import os
import json
import asyncio
from typing import Optional, Dict, List, Any
import httpx
from bs4 import BeautifulSoup
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("radiofrance-server")

# Constants
API_ENDPOINT = "https://openapi.radiofrance.fr/v1/graphql"
WEBSITE_BASE_URL = "https://www.radiofrance.fr"
PODCASTS_BASE_URL = "https://www.radiofrance.fr/podcasts"
USER_AGENT = "RadioFranceMCPClient/1.0"

# Get API key from environment variables
API_KEY = os.getenv("RADIOFRANCE_API_KEY")
if not API_KEY:
    print("WARNING: RADIOFRANCE_API_KEY environment variable not set. API functionality will be limited.")

# Setup GQL client for Radio France API
transport = AIOHTTPTransport(
    url=API_ENDPOINT,
    headers={"x-token": API_KEY, "User-Agent": USER_AGENT} if API_KEY else {"User-Agent": USER_AGENT}
)

gql_client = Client(transport=transport, fetch_schema_from_transport=True)


@mcp.tool()
async def get_taxonomies(keyword: str = None, limit: int = 10) -> str:
    """Get taxonomies (categories/tags) from Radio France API.
    
    Args:
        keyword: Optional keyword to filter taxonomies (default: None)
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        JSON string containing taxonomy information
    """
    if not API_KEY:
        return json.dumps({"error": "API key not set. Please configure RADIOFRANCE_API_KEY in your .env file."})
        
    try:
        # Define the GraphQL query for taxonomies
        query_str = """
        query GetTaxonomies($limit: Int!, $keyword: String) {
          taxonomies(limit: $limit, keyword: $keyword) {
            id
            title
            type
            url
            description
          }
        }
        """
        
        # Execute the query
        result = await gql_client.execute_async(
            gql(query_str),
            variable_values={"limit": limit, "keyword": keyword}
        )
        
        # Format and return the results
        if "taxonomies" in result:
            return json.dumps(result["taxonomies"], ensure_ascii=False, indent=2)
        else:
            return json.dumps([], ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Error getting taxonomies: {str(e)}"})


@mcp.tool()
async def get_diffusions(taxonomy_id: str, limit: int = 10) -> str:
    """Get diffusions (content) related to a specific taxonomy.
    
    Args:
        taxonomy_id: ID of the taxonomy to get diffusions for
        limit: Maximum number of results to return (default: 10)
        
    Returns:
        JSON string containing diffusion information
    """
    if not API_KEY:
        return json.dumps({"error": "API key not set. Please configure RADIOFRANCE_API_KEY in your .env file."})
        
    try:
        # Define the GraphQL query for diffusions by taxonomy
        query_str = """
        query GetDiffusions($taxonomyId: ID!, $limit: Int!) {
          taxonomy(id: $taxonomyId) {
            id
            title
            diffusions(limit: $limit) {
              id
              title
              url
              standFirst
              brand {
                title
                station {
                  name
                }
              }
              diffusionDate
              podcastEpisode {
                url
              }
            }
          }
        }
        """
        
        # Execute the query
        result = await gql_client.execute_async(
            gql(query_str),
            variable_values={"taxonomyId": taxonomy_id, "limit": limit}
        )
        
        # Format and return the results
        if "taxonomy" in result and "diffusions" in result["taxonomy"]:
            taxonomy = result["taxonomy"]
            formatted_result = {
                "taxonomyId": taxonomy.get("id", ""),
                "taxonomyTitle": taxonomy.get("title", ""),
                "diffusions": []
            }
            
            for diffusion in taxonomy["diffusions"]:
                formatted_diffusion = {
                    "id": diffusion.get("id", ""),
                    "title": diffusion.get("title", ""),
                    "url": diffusion.get("url", ""),
                    "description": diffusion.get("standFirst", ""),
                    "diffusionDate": diffusion.get("diffusionDate", ""),
                    "podcastUrl": diffusion.get("podcastEpisode", {}).get("url", ""),
                    "brand": diffusion.get("brand", {}).get("title", ""),
                    "station": diffusion.get("brand", {}).get("station", {}).get("name", "")
                }
                formatted_result["diffusions"].append(formatted_diffusion)
            
            return json.dumps(formatted_result, ensure_ascii=False, indent=2)
        else:
            return json.dumps({"error": f"No diffusions found for taxonomy ID: {taxonomy_id}"})
    
    except Exception as e:
        return json.dumps({"error": f"Error getting diffusions: {str(e)}"})


@mcp.tool()
async def get_brand(brand_id: str) -> str:
    """Get information about a specific brand (program/show).
    
    Args:
        brand_id: ID of the brand to get information for
        
    Returns:
        JSON string containing brand information
    """
    if not API_KEY:
        return json.dumps({"error": "API key not set. Please configure RADIOFRANCE_API_KEY in your .env file."})
        
    try:
        # Define the GraphQL query for brand information
        query_str = """
        query GetBrand($brandId: ID!) {
          brand(id: $brandId) {
            id
            title
            description
            url
            station {
              name
            }
            concepts {
              id
              title
            }
            latestDiffusions(limit: 5) {
              id
              title
              url
              standFirst
              diffusionDate
            }
          }
        }
        """
        
        # Execute the query
        result = await gql_client.execute_async(
            gql(query_str),
            variable_values={"brandId": brand_id}
        )
        
        # Format and return the results
        if "brand" in result:
            brand = result["brand"]
            formatted_result = {
                "id": brand.get("id", ""),
                "title": brand.get("title", ""),
                "description": brand.get("description", ""),
                "url": brand.get("url", ""),
                "station": brand.get("station", {}).get("name", ""),
                "concepts": [],
                "latestDiffusions": []
            }
            
            if "concepts" in brand:
                for concept in brand["concepts"]:
                    formatted_result["concepts"].append({
                        "id": concept.get("id", ""),
                        "title": concept.get("title", "")
                    })
            
            if "latestDiffusions" in brand:
                for diffusion in brand["latestDiffusions"]:
                    formatted_result["latestDiffusions"].append({
                        "id": diffusion.get("id", ""),
                        "title": diffusion.get("title", ""),
                        "url": diffusion.get("url", ""),
                        "description": diffusion.get("standFirst", ""),
                        "diffusionDate": diffusion.get("diffusionDate", "")
                    })
            
            return json.dumps(formatted_result, ensure_ascii=False, indent=2)
        else:
            return json.dumps({"error": f"No brand found with ID: {brand_id}"})
    
    except Exception as e:
        return json.dumps({"error": f"Error getting brand information: {str(e)}"})


@mcp.tool()
async def get_station_grid(station_code: str) -> str:
    """Get the program grid for a specific Radio France station.
    
    Args:
        station_code: Code of the station (e.g., "franceinter", "franceculture")
        
    Returns:
        JSON string containing program grid information
    """
    if not API_KEY:
        return json.dumps({"error": "API key not set. Please configure RADIOFRANCE_API_KEY in your .env file."})
        
    try:
        # Define the GraphQL query for station grid
        query_str = """
        query GetStationGrid($stationCode: String!) {
          grid(station: $stationCode) {
            station {
              id
              name
            }
            steps {
              startTime
              endTime
              diffusion {
                id
                title
                standFirst
                url
                brand {
                  title
                }
              }
            }
          }
        }
        """
        
        # Execute the query
        result = await gql_client.execute_async(
            gql(query_str),
            variable_values={"stationCode": station_code}
        )
        
        # Format and return the results
        if "grid" in result:
            grid = result["grid"]
            formatted_result = {
                "stationName": grid.get("station", {}).get("name", ""),
                "stationId": grid.get("station", {}).get("id", ""),
                "programs": []
            }
            
            if "steps" in grid:
                for step in grid["steps"]:
                    if "diffusion" in step:
                        diffusion = step["diffusion"]
                        formatted_result["programs"].append({
                            "startTime": step.get("startTime", ""),
                            "endTime": step.get("endTime", ""),
                            "id": diffusion.get("id", ""),
                            "title": diffusion.get("title", ""),
                            "description": diffusion.get("standFirst", ""),
                            "url": diffusion.get("url", ""),
                            "brand": diffusion.get("brand", {}).get("title", "")
                        })
            
            return json.dumps(formatted_result, ensure_ascii=False, indent=2)
        else:
            return json.dumps({"error": f"No grid found for station: {station_code}"})
    
    except Exception as e:
        return json.dumps({"error": f"Error getting station grid: {str(e)}"})
