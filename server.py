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
async def search_podcasts(query: str, limit: int = 10) -> str:
    """Search for podcasts based on a query string.
    
    Args:
        query: The search term to find podcasts
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        JSON string containing podcast information
    """
    if not API_KEY:
        return json.dumps({"error": "API key not set. Please configure RADIOFRANCE_API_KEY in your .env file."})
        
    try:
        # Define the GraphQL query
        query_str = """
        query SearchPodcasts($query: String!, $limit: Int!) {
          search(query: $query, limit: $limit) {
            shows {
              title
              description
              url
              podcast {
                url
              }
              station {
                name
              }
              latestEpisodes {
                title
                url
                publishedDate
                duration
              }
            }
          }
        }
        """
        
        # Execute the query
        result = await gql_client.execute_async(
            gql(query_str),
            variable_values={"query": query, "limit": limit}
        )
        
        # Format and return the results
        formatted_results = []
        if "search" in result and "shows" in result["search"]:
            for show in result["search"]["shows"]:
                episodes = []
                if "latestEpisodes" in show:
                    for episode in show["latestEpisodes"]:
                        episodes.append({
                            "title": episode.get("title", ""),
                            "url": episode.get("url", ""),
                            "publishedDate": episode.get("publishedDate", ""),
                            "duration": episode.get("duration", "")
                        })
                
                formatted_results.append({
                    "title": show.get("title", ""),
                    "description": show.get("description", ""),
                    "url": show.get("url", ""),
                    "podcastUrl": show.get("podcast", {}).get("url", ""),
                    "station": show.get("station", {}).get("name", ""),
                    "episodes": episodes
                })
        
        return json.dumps(formatted_results, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Error searching podcasts: {str(e)}"})


@mcp.tool()
async def get_station_programs(station_name: str) -> str:
    """Get current and upcoming programs for a specific Radio France station.
    
    Args:
        station_name: Name of the station (e.g., "France Inter", "France Culture")
        
    Returns:
        JSON string containing program information
    """
    if not API_KEY:
        return json.dumps({"error": "API key not set. Please configure RADIOFRANCE_API_KEY in your .env file."})
        
    try:
        # Define the GraphQL query
        query_str = """
        query StationPrograms($name: String!) {
          station(name: $name) {
            name
            currentProgram {
              title
              description
              startTime
              endTime
              url
            }
            nextPrograms(first: 5) {
              title
              description
              startTime
              endTime
              url
            }
          }
        }
        """
        
        # Execute the query
        result = await gql_client.execute_async(
            gql(query_str),
            variable_values={"name": station_name}
        )
        
        # Format and return the results
        if "station" in result:
            station = result["station"]
            formatted_result = {
                "stationName": station.get("name", ""),
                "currentProgram": None,
                "upcomingPrograms": []
            }
            
            if "currentProgram" in station and station["currentProgram"]:
                current = station["currentProgram"]
                formatted_result["currentProgram"] = {
                    "title": current.get("title", ""),
                    "description": current.get("description", ""),
                    "startTime": current.get("startTime", ""),
                    "endTime": current.get("endTime", ""),
                    "url": current.get("url", "")
                }
            
            if "nextPrograms" in station:
                for program in station["nextPrograms"]:
                    formatted_result["upcomingPrograms"].append({
                        "title": program.get("title", ""),
                        "description": program.get("description", ""),
                        "startTime": program.get("startTime", ""),
                        "endTime": program.get("endTime", ""),
                        "url": program.get("url", "")
                    })
            
            return json.dumps(formatted_result, ensure_ascii=False, indent=2)
        else:
            return json.dumps({"error": f"No information found for station: {station_name}"})
    
    except Exception as e:
        return json.dumps({"error": f"Error getting station programs: {str(e)}"})


@mcp.tool()
async def search_episodes(topic: str, limit: int = 10) -> str:
    """Search for podcast episodes based on a specific topic.
    
    Args:
        topic: The topic to search for in episodes
        limit: Maximum number of results to return (default: 10)
        
    Returns:
        JSON string containing episode information
    """
    if not API_KEY:
        return json.dumps({"error": "API key not set. Please configure RADIOFRANCE_API_KEY in your .env file."})
        
    try:
        # Define the GraphQL query
        query_str = """
        query SearchEpisodes($query: String!, $limit: Int!) {
          search(query: $query, limit: $limit) {
            episodes {
              title
              description
              url
              publishedDate
              duration
              show {
                title
                url
              }
              station {
                name
              }
            }
          }
        }
        """
        
        # Execute the query
        result = await gql_client.execute_async(
            gql(query_str),
            variable_values={"query": topic, "limit": limit}
        )
        
        # Format and return the results
        formatted_results = []
        if "search" in result and "episodes" in result["search"]:
            for episode in result["search"]["episodes"]:
                formatted_results.append({
                    "title": episode.get("title", ""),
                    "description": episode.get("description", ""),
                    "url": episode.get("url", ""),
                    "publishedDate": episode.get("publishedDate", ""),
                    "duration": episode.get("duration", ""),
                    "show": {
                        "title": episode.get("show", {}).get("title", ""),
                        "url": episode.get("show", {}).get("url", "")
                    },
                    "station": episode.get("station", {}).get("name", "")
                })
        
        return json.dumps(formatted_results, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Error searching episodes: {str(e)}"})


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
            
            # Find the categories container (actual selectors will depend on website structure)
            categories = []
            category_elements = soup.select('.podcast-category-item')  # Adjust selector as needed
            
            for element in category_elements:
                name_element = element.select_one('.category-name')
                url_element = element.select_one('a')
                
                if name_element and url_element and 'href' in url_element.attrs:
                    category_url = url_element['href']
                    if not category_url.startswith('http'):
                        category_url = f"{WEBSITE_BASE_URL}{category_url}"
                        
                    categories.append({
                        "name": name_element.text.strip(),
                        "url": category_url
                    })
            
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
            
            # Extract podcast information (adjust selectors based on actual website structure)
            title_element = soup.select_one('.podcast-title, h1')
            description_element = soup.select_one('.podcast-description, .description')
            author_element = soup.select_one('.podcast-author, .author')
            
            episodes = []
            episode_elements = soup.select('.podcast-episode, .episode-item')
            
            for element in episode_elements:
                episode_title = element.select_one('.episode-title, h3')
                episode_date = element.select_one('.episode-date, .date')
                episode_duration = element.select_one('.episode-duration, .duration')
                episode_url_element = element.select_one('a.episode-link, a')
                
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
            
            result = {
                "title": title_element.text.strip() if title_element else "",
                "description": description_element.text.strip() if description_element else "",
                "author": author_element.text.strip() if author_element else "",
                "url": podcast_url,
                "episodes": episodes
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Error scraping podcast details: {str(e)}"})


@mcp.tool()
async def get_audio_content_info(url: str) -> str:
    """Get detailed information about audio content from its URL.
    
    Args:
        url: The URL of the audio content (episode, podcast)
        
    Returns:
        JSON string containing audio information including stream URLs if available
    """
    try:
        if not url.startswith('http'):
            url = f"{WEBSITE_BASE_URL}{url}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"User-Agent": USER_AGENT},
                follow_redirects=True
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for audio player and stream URLs
            # This will depend on how Radio France's website structures their audio players
            audio_element = soup.select_one('[data-audio-src], audio source')  # Adjust selector as needed
            audio_url = audio_element['data-audio-src'] if audio_element and 'data-audio-src' in audio_element.attrs else None
            if not audio_url and audio_element and 'src' in audio_element.attrs:
                audio_url = audio_element['src']
            
            # Extract basic metadata
            title_element = soup.select_one('.episode-title, h1, h2, .title')  # Adjust selector as needed
            description_element = soup.select_one('.episode-description, .description')  # Adjust selector as needed
            duration_element = soup.select_one('.duration, .episode-duration')  # Adjust selector as needed
            
            result = {
                "title": title_element.text.strip() if title_element else "",
                "description": description_element.text.strip() if description_element else "",
                "duration": duration_element.text.strip() if duration_element else "",
                "pageUrl": url,
                "audioUrl": audio_url,
                "streamFormat": "Unknown"  # Would need inspection of actual pages to determine
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Error getting audio content information: {str(e)}"})


@mcp.tool()
async def natural_language_search(query: str, max_results: int = 10) -> str:
    """Process a natural language query to find relevant Radio France content.
    
    This tool analyzes the query and determines whether to search for podcasts,
    episodes, or stations to find the most relevant content.
    
    Args:
        query: Natural language query describing what content to find
        max_results: Maximum number of results to return (default: 10)
        
    Returns:
        JSON string containing the most relevant content
    """
    if not API_KEY:
        return json.dumps({"error": "API key not set. Please configure RADIOFRANCE_API_KEY in your .env file."})
        
    try:
        # First, try to search for episodes as they are most specific
        episodes_result = await search_episodes(query, max_results)
        episodes_data = json.loads(episodes_result)
        
        # Check if we got episodes or an error
        if isinstance(episodes_data, dict) and "error" in episodes_data:
            return episodes_result
            
        # If we found episodes, return them
        if episodes_data and isinstance(episodes_data, list) and len(episodes_data) > 0:
            return json.dumps({
                "queryType": "episodes",
                "searchTerm": query,
                "results": episodes_data
            }, ensure_ascii=False, indent=2)
        
        # If no episodes found, try podcasts
        podcasts_result = await search_podcasts(query, max_results)
        podcasts_data = json.loads(podcasts_result)
        
        # Check if we got podcasts or an error
        if isinstance(podcasts_data, dict) and "error" in podcasts_data:
            return podcasts_result
            
        # If we found podcasts, return them
        if podcasts_data and isinstance(podcasts_data, list) and len(podcasts_data) > 0:
            return json.dumps({
                "queryType": "podcasts",
                "searchTerm": query,
                "results": podcasts_data
            }, ensure_ascii=False, indent=2)
        
        # If we're looking for a specific station
        station_names = ["France Inter", "France Info", "France Culture", 
                         "France Musique", "France Bleu", "Fip", "Mouv"]
        
        for station_name in station_names:
            if station_name.lower() in query.lower():
                station_result = await get_station_programs(station_name)
                station_data = json.loads(station_result)
                
                # Check if we got station info or an error
                if isinstance(station_data, dict) and "error" in station_data:
                    return station_result
                    
                if station_data and "stationName" in station_data:
                    return json.dumps({
                        "queryType": "station",
                        "searchTerm": station_name,
                        "results": station_data
                    }, ensure_ascii=False, indent=2)
        
        # If nothing specific was found, return a message
        return json.dumps({
            "queryType": "general",
            "searchTerm": query,
            "message": "No specific content found for your query. Try a more specific search term related to a podcast, episode, or Radio France station."
        }, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Error processing natural language search: {str(e)}"})


if __name__ == "__main__":
    print("Starting Radio France MCP Server...")
    mcp.run(transport='stdio')
