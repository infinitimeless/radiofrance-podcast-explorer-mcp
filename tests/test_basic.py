#!/usr/bin/env python3
"""
Basic test script for Radio France MCP Server
This script tests the connectivity and basic functionality of the server
"""

import os
import sys
import json
import asyncio
from dotenv import load_dotenv

# Add parent directory to path to import server module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server import (
    search_podcasts,
    get_station_programs,
    search_episodes,
    scrape_podcast_categories,
    natural_language_search
)

# Load environment variables from .env file
load_dotenv()

# Check if API key is set
API_KEY = os.getenv("RADIOFRANCE_API_KEY")
if not API_KEY:
    print("WARNING: RADIOFRANCE_API_KEY environment variable not set.")
    print("Some tests may fail or return limited results.")
    print("Please set the API key in your .env file.")
    print("")

async def run_tests():
    """Run basic tests for the MCP server functions"""
    
    print("Testing Radio France MCP Server...")
    print("-" * 40)
    
    # Test 1: Search Podcasts
    print("Test 1: Search Podcasts - 'histoire'")
    try:
        result = await search_podcasts("histoire", 2)
        data = json.loads(result)
        if isinstance(data, dict) and "error" in data:
            print(f"Error: {data['error']}")
        else:
            print(f"Found {len(data)} podcasts")
            if len(data) > 0:
                print(f"First podcast: {data[0].get('title', 'Unknown')}")
        print("Test 1: PASSED" if not (isinstance(data, dict) and "error" in data) else "Test 1: FAILED")
    except Exception as e:
        print(f"Test 1: FAILED - Exception: {str(e)}")
    print("-" * 40)
    
    # Test 2: Get Station Programs
    print("Test 2: Get Station Programs - 'France Culture'")
    try:
        result = await get_station_programs("France Culture")
        data = json.loads(result)
        if isinstance(data, dict) and "error" in data:
            print(f"Error: {data['error']}")
        else:
            print(f"Station: {data.get('stationName', 'Unknown')}")
            if data.get('currentProgram'):
                print(f"Current program: {data['currentProgram'].get('title', 'Unknown')}")
            print(f"Upcoming programs: {len(data.get('upcomingPrograms', []))}")
        print("Test 2: PASSED" if not (isinstance(data, dict) and "error" in data) else "Test 2: FAILED")
    except Exception as e:
        print(f"Test 2: FAILED - Exception: {str(e)}")
    print("-" * 40)
    
    # Test 3: Search Episodes
    print("Test 3: Search Episodes - 'politique'")
    try:
        result = await search_episodes("politique", 2)
        data = json.loads(result)
        if isinstance(data, dict) and "error" in data:
            print(f"Error: {data['error']}")
        else:
            print(f"Found {len(data)} episodes")
            if len(data) > 0:
                print(f"First episode: {data[0].get('title', 'Unknown')}")
        print("Test 3: PASSED" if not (isinstance(data, dict) and "error" in data) else "Test 3: FAILED")
    except Exception as e:
        print(f"Test 3: FAILED - Exception: {str(e)}")
    print("-" * 40)
    
    # Test 4: Scrape Podcast Categories
    print("Test 4: Scrape Podcast Categories")
    try:
        result = await scrape_podcast_categories()
        data = json.loads(result)
        if isinstance(data, dict) and "error" in data:
            print(f"Error: {data['error']}")
        elif "categories" in data:
            print(f"Found {len(data['categories'])} podcast categories")
        else:
            print("No categories found or unexpected response structure")
        print("Test 4: PASSED" if not (isinstance(data, dict) and "error" in data) else "Test 4: FAILED")
    except Exception as e:
        print(f"Test 4: FAILED - Exception: {str(e)}")
    print("-" * 40)
    
    # Test 5: Natural Language Search
    print("Test 5: Natural Language Search - 'podcasts sur l'histoire de France'")
    try:
        result = await natural_language_search("podcasts sur l'histoire de France", 2)
        data = json.loads(result)
        if isinstance(data, dict) and "error" in data:
            print(f"Error: {data['error']}")
        else:
            print(f"Query type: {data.get('queryType', 'Unknown')}")
            print(f"Search term: {data.get('searchTerm', 'Unknown')}")
            if "results" in data and isinstance(data["results"], list):
                print(f"Found {len(data['results'])} results")
            elif "results" in data and isinstance(data["results"], dict):
                print("Found results in dict format")
            else:
                print(f"Message: {data.get('message', 'No message')}")
        print("Test 5: PASSED" if not (isinstance(data, dict) and "error" in data) else "Test 5: FAILED")
    except Exception as e:
        print(f"Test 5: FAILED - Exception: {str(e)}")
    print("-" * 40)
    
    print("All tests completed!")

if __name__ == "__main__":
    # Run async tests
    asyncio.run(run_tests())
