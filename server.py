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


@mcp.tool()
async def scrape_podcast_categories() -> str:
    """Scrape and return all podcast categories from Radio France website.
    
    Returns:
        JSON string containing podcast categories
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{PODCASTS_BASE_URL}",
                headers={"User-Agent": USER_AGENT},
                follow_redirects=True
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Updated selectors based on current Radio France website structure
            categories = []
            
            # Try different potential selectors
            category_elements = soup.select('.rf-taxonomy-item, .category-item, .theme-item, .podcast-category')
            
            if not category_elements:
                # If no categories found with specific selectors, try more generic approach
                category_elements = soup.select('nav li a, .categories a, .themes a')
            
            for element in category_elements:
                # For anchor elements
                if element.name == 'a':
                    name = element.get_text().strip()
                    url = element['href']
                    
                    if name and url:
                        if not url.startswith('http'):
                            url = f"{WEBSITE_BASE_URL}{url}"
                            
                        categories.append({
                            "name": name,
                            "url": url
                        })
                # For container elements with title and link
                else:
                    name_element = element.select_one('h2, h3, .title, .name')
                    url_element = element.select_one('a')
                    
                    if name_element and url_element and 'href' in url_element.attrs:
                        category_url = url_element['href']
                        if not category_url.startswith('http'):
                            category_url = f"{WEBSITE_BASE_URL}{category_url}"
                            
                        categories.append({
                            "name": name_element.text.strip(),
                            "url": category_url
                        })
            
            # Add debug information if no categories were found
            if not categories:
                # Get some representative HTML to help debugging
                sample_html = str(soup.select('body')[0])[:1000] if soup.select('body') else "No body found"
                return json.dumps({
                    "categories": [],
                    "debug": {
                        "message": "No categories found with current selectors",
                        "sampleHtml": sample_html
                    }
                }, ensure_ascii=False, indent=2)
            
            return json.dumps({"categories": categories}, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Error scraping podcast categories: {str(e)}"})


@mcp.tool()
async def scrape_podcast_details(podcast_url: str) -> str:
    """Scrape detailed information about a podcast from its URL.
    
    Args:
        podcast_url: The URL of the podcast to scrape
        
    Returns:
        JSON string containing detailed podcast information
    """
    try:
        if not podcast_url.startswith('http'):
            podcast_url = f"{WEBSITE_BASE_URL}{podcast_url}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                podcast_url,
                headers={"User-Agent": USER_AGENT},
                follow_redirects=True
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Updated selectors with multiple options for flexibility
            title_element = soup.select_one('.podcast-title, .brand-title, h1, [data-testid="title"]')
            description_element = soup.select_one('.podcast-description, .brand-description, .description, [data-testid="description"]')
            author_element = soup.select_one('.podcast-author, .brand-author, .author, [data-testid="author"]')
            
            episodes = []
            episode_elements = soup.select('.podcast-episode, .episode-item, .diffusion-item, [data-testid="episode"]')
            
            for element in episode_elements:
                episode_title = element.select_one('.episode-title, h3, .title, [data-testid="episode-title"]')
                episode_date = element.select_one('.episode-date, .date, time, [data-testid="episode-date"]')
                episode_duration = element.select_one('.episode-duration, .duration, [data-testid="episode-duration"]')
                episode_url_element = element.select_one('a, [data-testid="episode-link"]')
                
                if episode_title and episode_url_element and 'href' in episode_url_element.attrs:
                    episode_url = episode_url_element['href']
                    if not episode_url.startswith('http'):
                        episode_url = f"{WEBSITE_BASE_URL}{episode_url}"
                        
                    episodes.append({
                        "title": episode_title.text.strip() if episode_title else "",
                        "date": episode_date.text.strip() if episode_date else "",
                        "duration": episode_duration.text.strip() if episode_duration else "",
                        "url": episode_url
                    })
            
            # If no episodes found with specific selectors, try more generic approach
            if not episodes:
                # Look for list items or article elements that might contain episodes
                generic_elements = soup.select('li.episode, article, .card')
                for element in generic_elements:
                    title = element.select_one('h2, h3, h4, .title')
                    link = element.select_one('a[href]')
                    date = element.select_one('time, .date')
                    
                    if title and link and 'href' in link.attrs:
                        episode_url = link['href']
                        if not episode_url.startswith('http'):
                            episode_url = f"{WEBSITE_BASE_URL}{episode_url}"
                            
                        episodes.append({
                            "title": title.text.strip(),
                            "date": date.text.strip() if date else "",
                            "duration": "",  # May not find duration with generic approach
                            "url": episode_url
                        })
            
            result = {
                "title": title_element.text.strip() if title_element else "",
                "description": description_element.text.strip() if description_element else "",
                "author": author_element.text.strip() if author_element else "",
                "url": podcast_url,
                "episodes": episodes
            }
            
            # Add debug information if no content was found
            if not title_element and not episodes:
                sample_html = str(soup.select('body')[0])[:1000] if soup.select('body') else "No body found"
                result["debug"] = {
                    "message": "Limited podcast information found with current selectors",
                    "sampleHtml": sample_html
                }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Error scraping podcast details: {str(e)}"})
