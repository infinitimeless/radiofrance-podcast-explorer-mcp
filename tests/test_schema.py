#!/usr/bin/env python3
"""
GraphQL Schema Test for Radio France MCP Server
This script verifies the actual structure of the Radio France GraphQL API
"""

import os
import sys
import json
import asyncio
from dotenv import load_dotenv
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

# Add parent directory to path to import server module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
API_KEY = os.getenv("RADIOFRANCE_API_KEY")
if not API_KEY:
    print("ERROR: RADIOFRANCE_API_KEY environment variable not set.")
    print("This test requires an API key to run.")
    sys.exit(1)

# Setup GQL client for Radio France API
API_ENDPOINT = "https://openapi.radiofrance.fr/v1/graphql"
USER_AGENT = "RadioFranceMCPTester/1.0"

transport = AIOHTTPTransport(
    url=API_ENDPOINT,
    headers={"x-token": API_KEY, "User-Agent": USER_AGENT}
)

gql_client = Client(transport=transport, fetch_schema_from_transport=True)

async def test_get_schema():
    """Retrieve and analyze the GraphQL schema"""
    
    try:
        # Introspection query to get the schema
        query = gql("""
        query {
          __schema {
            queryType {
              fields {
                name
                description
                args {
                  name
                  description
                  type {
                    name
                    kind
                  }
                }
                type {
                  name
                  kind
                }
              }
            }
          }
        }
        """)
        
        result = await gql_client.execute_async(query)
        
        # Extract root query fields
        query_fields = result["__schema"]["queryType"]["fields"]
        field_names = [field["name"] for field in query_fields]
        
        print("Available root query fields in the Radio France API:")
        for name in field_names:
            print(f"- {name}")
        
        # Check if our expected fields exist
        expected_fields = ["taxonomies", "taxonomy", "grid", "brand"]
        for field in expected_fields:
            if field in field_names:
                print(f"✅ Field '{field}' exists in schema")
            else:
                print(f"❌ Field '{field}' NOT found in schema")
                
        # Check if previously used fields exist
        old_fields = ["search", "station"]
        for field in old_fields:
            if field in field_names:
                print(f"ℹ️ Field '{field}' exists in schema (was expected to be missing)")
            else:
                print(f"ℹ️ Field '{field}' NOT found in schema (as expected)")
                
        print("\nSchema analysis complete!")
        
    except Exception as e:
        print(f"Error analyzing schema: {str(e)}")

async def test_taxonomies_query():
    """Test the taxonomies query"""
    
    try:
        # Test query for taxonomies
        query = gql("""
        query GetTaxonomies($limit: Int!, $keyword: String) {
          taxonomies(limit: $limit, keyword: $keyword) {
            id
            title
            type
            url
            description
          }
        }
        """)
        
        result = await gql_client.execute_async(
            query,
            variable_values={"limit": 5, "keyword": "histoire"}
        )
        
        taxonomies = result.get("taxonomies", [])
        
        print("\nTaxonomies Query Test:")
        print(f"Found {len(taxonomies)} taxonomies for keyword 'histoire'")
        
        if taxonomies:
            print("First taxonomy:")
            print(f"- Title: {taxonomies[0]['title']}")
            print(f"- Type: {taxonomies[0]['type']}")
            print(f"- ID: {taxonomies[0]['id']}")
            print("✅ Taxonomies query works!")
        else:
            print("❌ No taxonomies returned")
            
    except Exception as e:
        print(f"Error testing taxonomies query: {str(e)}")

async def test_diffusions_query():
    """Test the diffusions query via taxonomy"""
    
    try:
        # First get a taxonomy ID
        taxonomy_query = gql("""
        query GetTaxonomies($limit: Int!, $keyword: String) {
          taxonomies(limit: $limit, keyword: $keyword) {
            id
            title
          }
        }
        """)
        
        taxonomy_result = await gql_client.execute_async(
            taxonomy_query,
            variable_values={"limit": 1, "keyword": "histoire"}
        )
        
        taxonomies = taxonomy_result.get("taxonomies", [])
        
        if not taxonomies:
            print("\nDiffusions Query Test:")
            print("❌ No taxonomy ID available to test diffusions")
            return
            
        taxonomy_id = taxonomies[0]["id"]
        
        # Now test diffusions query
        diffusion_query = gql("""
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
        """)
        
        diffusion_result = await gql_client.execute_async(
            diffusion_query,
            variable_values={"taxonomyId": taxonomy_id, "limit": 5}
        )
        
        taxonomy = diffusion_result.get("taxonomy", {})
        diffusions = taxonomy.get("diffusions", [])
        
        print("\nDiffusions Query Test:")
        print(f"Testing with taxonomy ID: {taxonomy_id}")
        print(f"Taxonomy title: {taxonomy.get('title', 'Unknown')}")
        print(f"Found {len(diffusions)} diffusions")
        
        if diffusions:
            print("First diffusion:")
            print(f"- Title: {diffusions[0]['title']}")
            print(f"- Brand: {diffusions[0]['brand']['title'] if diffusions[0]['brand'] else 'Unknown'}")
            print(f"- Station: {diffusions[0]['brand']['station']['name'] if diffusions[0]['brand'] and diffusions[0]['brand']['station'] else 'Unknown'}")
            print("✅ Diffusions query works!")
        else:
            print("❌ No diffusions returned")
            
    except Exception as e:
        print(f"Error testing diffusions query: {str(e)}")

async def test_grid_query():
    """Test the grid query for station programming"""
    
    try:
        # Test query for grid
        query = gql("""
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
        """)
        
        result = await gql_client.execute_async(
            query,
            variable_values={"stationCode": "franceculture"}
        )
        
        grid = result.get("grid", {})
        steps = grid.get("steps", [])
        
        print("\nGrid Query Test:")
        print(f"Station: {grid.get('station', {}).get('name', 'Unknown')}")
        print(f"Found {len(steps)} program steps")
        
        if steps:
            print("First program:")
            print(f"- Time: {steps[0]['startTime']} - {steps[0]['endTime']}")
            if steps[0].get('diffusion'):
                print(f"- Title: {steps[0]['diffusion']['title']}")
                print(f"- Brand: {steps[0]['diffusion']['brand']['title'] if steps[0]['diffusion']['brand'] else 'Unknown'}")
            print("✅ Grid query works!")
        else:
            print("❌ No program steps returned")
            
    except Exception as e:
        print(f"Error testing grid query: {str(e)}")

async def run_tests():
    """Run all schema tests"""
    
    print("Radio France GraphQL Schema Test")
    print("=" * 50)
    
    await test_get_schema()
    await test_taxonomies_query()
    await test_diffusions_query()
    await test_grid_query()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    # Run async tests
    asyncio.run(run_tests())
