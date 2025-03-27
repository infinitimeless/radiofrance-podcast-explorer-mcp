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