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
            # These will need to be adjusted based on actual DOM inspection
            categories = []
            
            # Try different potential selectors
            category_elements = soup.select('.rf-taxonomy-item, .category-item, .theme-item, .podcast-category')
            
            if not category_elements:
                # If no categories found with specific selectors, try more generic approach
                # Look for list items within navigation or category sections
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
            
            # Check for JSON-LD metadata which often contains media info
            json_ld = None
            json_ld_script = soup.select_one('script[type="application/ld+json"]')
            if json_ld_script:
                try:
                    json_ld = json.loads(json_ld_script.string)
                except:
                    pass
            
            # Look for audio player and stream URLs with multiple selector options
            audio_element = soup.select_one('[data-audio-src], [data-media-src], audio source, [data-testid="audio-player"] source')
            
            # Try to find audio URL from various attributes
            audio_url = None
            if audio_element:
                for attr in ['data-audio-src', 'data-media-src', 'data-src', 'src']:
                    if attr in audio_element.attrs:
                        audio_url = audio_element[attr]
                        break
            
            # If no direct audio element found, look for it in JSON-LD
            if not audio_url and json_ld:
                if isinstance(json_ld, dict):
                    audio_url = json_ld.get('contentUrl', None)
                elif isinstance(json_ld, list) and len(json_ld) > 0:
                    for item in json_ld:
                        if isinstance(item, dict) and 'contentUrl' in item:
                            audio_url = item['contentUrl']
                            break
            
            # If still no audio URL, look for it in other script tags
            if not audio_url:
                for script in soup.select('script'):
                    script_text = script.string
                    if script_text and ('audioURL' in script_text or 'audioUrl' in script_text or 'mp3' in script_text):
                        # Simple regex-like approach to find URLs in script
                        for line in script_text.split('\n'):
                            if ('audioURL' in line or 'audioUrl' in line or 'mp3' in line) and ('http' in line):
                                # Extract URL between quotes
                                start_quote = line.find('"', line.find('http'))
                                if start_quote != -1:
                                    end_quote = line.find('"', start_quote + 1)
                                    if end_quote != -1:
                                        audio_url = line[start_quote + 1:end_quote]
                                        break
            
            # Extract basic metadata with multiple selector options
            title_element = soup.select_one('.episode-title, h1, h2, .title, [data-testid="title"]')
            description_element = soup.select_one('.episode-description, .description, [data-testid="description"]')
            duration_element = soup.select_one('.duration, .episode-duration, time, [data-testid="duration"]')
            
            # If metadata not found in DOM, try JSON-LD
            title = title_element.text.strip() if title_element else ""
            description = description_element.text.strip() if description_element else ""
            duration = duration_element.text.strip() if duration_element else ""
            
            if (not title or not description) and json_ld:
                if isinstance(json_ld, dict):
                    title = title or json_ld.get('name', '')
                    description = description or json_ld.get('description', '')
                    duration = duration or json_ld.get('duration', '')
                elif isinstance(json_ld, list) and len(json_ld) > 0:
                    for item in json_ld:
                        if isinstance(item, dict):
                            title = title or item.get('name', '')
                            description = description or item.get('description', '')
                            duration = duration or item.get('duration', '')
                            if title and description:
                                break
            
            result = {
                "title": title,
                "description": description,
                "duration": duration,
                "pageUrl": url,
                "audioUrl": audio_url,
                "streamFormat": "mp3" if audio_url and '.mp3' in audio_url else "Unknown"
            }
            
            # Add debug information if no audio URL was found
            if not audio_url:
                # Get a sample of potential player elements
                player_elements = soup.select('.player, [data-testid="player"], audio, .rf-player')
                player_html = [str(el)[:200] for el in player_elements[:2]]
                
                result["debug"] = {
                    "message": "No audio URL found with current selectors",
                    "playerElements": player_html,
                    "hasJsonLd": json_ld is not None
                }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Error getting audio content information: {str(e)}"})


@mcp.tool()
async def search_podcasts(query: str, limit: int = 10) -> str:
    """Search for podcasts based on a query string.
    
    This tool first searches for relevant taxonomies, then retrieves diffusions for those taxonomies.
    
    Args:
        query: The search term to find podcasts
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        JSON string containing podcast information
    """
    if not API_KEY:
        return json.dumps({"error": "API key not set. Please configure RADIOFRANCE_API_KEY in your .env file."})
        
    try:
        # Step 1: Get taxonomies related to the query
        taxonomies_result = await get_taxonomies(query, limit=5)  # Get 5 most relevant taxonomies
        taxonomies_data = json.loads(taxonomies_result)
        
        # Check if we got taxonomies or an error
        if isinstance(taxonomies_data, dict) and "error" in taxonomies_data:
            return taxonomies_result
            
        # Step 2: Get diffusions for each taxonomy
        all_diffusions = []
        
        for taxonomy in taxonomies_data:
            taxonomy_id = taxonomy.get("id", "")
            if taxonomy_id:
                diffusions_result = await get_diffusions(taxonomy_id, limit=limit//len(taxonomies_data) + 1)
                diffusions_data = json.loads(diffusions_result)
                
                if isinstance(diffusions_data, dict) and "diffusions" in diffusions_data:
                    for diffusion in diffusions_data["diffusions"]:
                        # Add taxonomy info to diffusion
                        diffusion["taxonomyTitle"] = taxonomy.get("title", "")
                        diffusion["taxonomyType"] = taxonomy.get("type", "")
                        all_diffusions.append(diffusion)
        
        # Sort and limit results
        all_diffusions = sorted(all_diffusions, key=lambda x: x.get("brand", ""))
        all_diffusions = all_diffusions[:limit]
        
        return json.dumps({
            "query": query,
            "results": all_diffusions
        }, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Error searching podcasts: {str(e)}"})


@mcp.tool()
async def get_station_programs(station_name: str) -> str:
    """Get current and upcoming programs for a specific Radio France station.
    
    This tool maps station names to their codes and queries the station grid.
    
    Args:
        station_name: Name of the station (e.g., "France Inter", "France Culture")
        
    Returns:
        JSON string containing program information
    """
    if not API_KEY:
        return json.dumps({"error": "API key not set. Please configure RADIOFRANCE_API_KEY in your .env file."})
        
    try:
        # Map station names to station codes
        station_mapping = {
            "France Inter": "franceinter",
            "France Info": "franceinfo",
            "France Culture": "franceculture",
            "France Musique": "francemusique",
            "France Bleu": "francebleu",
            "FIP": "fip",
            "Mouv": "mouv"
        }
        
        # Get the station code
        station_code = station_mapping.get(station_name, None)
        if not station_code:
            # Try case-insensitive matching
            for name, code in station_mapping.items():
                if name.lower() == station_name.lower():
                    station_code = code
                    break
            
            # If still not found, try to use the input directly as a code
            if not station_code:
                station_code = station_name.lower().replace(" ", "")
        
        # Get the station grid
        grid_result = await get_station_grid(station_code)
        grid_data = json.loads(grid_result)
        
        # Check if we got grid or an error
        if isinstance(grid_data, dict) and "error" in grid_data:
            return grid_result
            
        # Format as station programs
        formatted_result = {
            "stationName": grid_data.get("stationName", station_name),
            "currentProgram": None,
            "upcomingPrograms": []
        }
        
        # Get current and upcoming programs
        now = None  # Would get current time here
        
        # For now, we'll just take the first program as current and the rest as upcoming
        programs = grid_data.get("programs", [])
        if programs:
            formatted_result["currentProgram"] = {
                "title": programs[0].get("title", ""),
                "description": programs[0].get("description", ""),
                "startTime": programs[0].get("startTime", ""),
                "endTime": programs[0].get("endTime", ""),
                "url": programs[0].get("url", "")
            }
            
            formatted_result["upcomingPrograms"] = [
                {
                    "title": program.get("title", ""),
                    "description": program.get("description", ""),
                    "startTime": program.get("startTime", ""),
                    "endTime": program.get("endTime", ""),
                    "url": program.get("url", "")
                }
                for program in programs[1:6]  # Next 5 programs
            ]
        
        return json.dumps(formatted_result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Error getting station programs: {str(e)}"})


@mcp.tool()
async def search_episodes(topic: str, limit: int = 10) -> str:
    """Search for podcast episodes based on a specific topic.
    
    This tool first searches for relevant taxonomies, then retrieves diffusions for those taxonomies.
    
    Args:
        topic: The topic to search for in episodes
        limit: Maximum number of results to return (default: 10)
        
    Returns:
        JSON string containing episode information
    """
    if not API_KEY:
        return json.dumps({"error": "API key not set. Please configure RADIOFRANCE_API_KEY in your .env file."})
        
    try:
        # Reuse the search_podcasts function as it already implements the two-step process
        search_result = await search_podcasts(topic, limit)
        search_data = json.loads(search_result)
        
        # Check if we got results or an error
        if isinstance(search_data, dict) and "error" in search_data:
            return search_result
            
        # Format specifically as episodes
        episodes = []
        
        if "results" in search_data:
            for diffusion in search_data["results"]:
                episode = {
                    "title": diffusion.get("title", ""),
                    "description": diffusion.get("description", ""),
                    "url": diffusion.get("url", ""),
                    "publishedDate": diffusion.get("diffusionDate", ""),
                    "duration": "",  # Duration may not be available
                    "show": {
                        "title": diffusion.get("brand", ""),
                        "url": ""  # URL may not be available
                    },
                    "station": diffusion.get("station", ""),
                    "taxonomyTitle": diffusion.get("taxonomyTitle", "")
                }
                episodes.append(episode)
                
        return json.dumps(episodes, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Error searching episodes: {str(e)}"})


@mcp.tool()
async def natural_language_search(query: str, max_results: int = 10) -> str:
    """Process a natural language query to find relevant Radio France content.
    
    This tool analyzes the query and determines the most appropriate search approach.
    
    Args:
        query: Natural language query describing what content to find
        max_results: Maximum number of results to return (default: 10)
        
    Returns:
        JSON string containing the most relevant content
    """
    if not API_KEY:
        return json.dumps({"error": "API key not set. Please configure RADIOFRANCE_API_KEY in your .env file."})
        
    try:
        # First, check if the query mentions a specific station
        station_names = ["France Inter", "France Info", "France Culture", 
                        "France Musique", "France Bleu", "FIP", "Mouv"]
        
        for station_name in station_names:
            if station_name.lower() in query.lower():
                station_result = await get_station_programs(station_name)
                station_data = json.loads(station_result)
                
                # Check if we got station info or an error
                if isinstance(station_data, dict) and "error" not in station_data:
                    return json.dumps({
                        "queryType": "station",
                        "searchTerm": station_name,
                        "results": station_data
                    }, ensure_ascii=False, indent=2)
        
        # If no station is mentioned, search for episodes first as they are most specific
        episodes_result = await search_episodes(query, max_results)
        episodes_data = json.loads(episodes_result)
        
        # Check if we got episodes or an error
        if isinstance(episodes_data, list) and len(episodes_data) > 0:
            return json.dumps({
                "queryType": "episodes",
                "searchTerm": query,
                "results": episodes_data
            }, ensure_ascii=False, indent=2)
        
        # If no episodes found, get taxonomies directly to offer categories
        taxonomies_result = await get_taxonomies(query, limit=max_results)
        taxonomies_data = json.loads(taxonomies_result)
        
        # Check if we got taxonomies or an error
        if isinstance(taxonomies_data, list) and len(taxonomies_data) > 0:
            return json.dumps({
                "queryType": "taxonomies",
                "searchTerm": query,
                "results": taxonomies_data
            }, ensure_ascii=False, indent=2)
        
        # If no specific content was found, return a message
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
