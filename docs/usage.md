# Radio France Podcast Explorer MCP - Usage Guide

This guide explains how to use the Radio France Podcast Explorer MCP server with AI assistants like Claude.

## Setup and Configuration

1. Make sure you have installed all the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your Radio France API key:
   ```
   RADIOFRANCE_API_KEY=your_api_key_here
   ```

3. Start the server:
   ```bash
   python server.py
   ```

## Using with Claude Desktop

To use this server with Claude Desktop:

1. Open the file at the following location:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add or update the server configuration:
   ```json
   {
     "mcpServers": {
       "radiofrance": {
         "command": "python",
         "args": ["/absolute/path/to/radiofrance-podcast-explorer-mcp/server.py"],
         "env": {
           "RADIOFRANCE_API_KEY": "your_api_key_here"
         }
       }
     }
   }
   ```

3. Save the file and restart Claude Desktop

## Available Tools

The server provides the following tools:

### search_podcasts(query, limit=10)

Searches for podcasts matching the query string.

Example:
```
search_podcasts("histoire de france", 5)
```

### search_episodes(topic, limit=10)

Searches for specific episodes on a given topic.

Example:
```
search_episodes("politique européenne", 5)
```

### get_station_programs(station_name)

Gets current and upcoming programs for a specific Radio France station.

Example:
```
get_station_programs("France Culture")
```

### scrape_podcast_categories()

Scrapes and returns all podcast categories from the Radio France website.

Example:
```
scrape_podcast_categories()
```

### scrape_podcast_details(podcast_url)

Gets detailed information about a podcast from its URL.

Example:
```
scrape_podcast_details("https://www.radiofrance.fr/franceculture/podcasts/le-cours-de-l-histoire")
```

### get_audio_content_info(url)

Gets detailed information about audio content from its URL, including stream URLs if available.

Example:
```
get_audio_content_info("https://www.radiofrance.fr/franceculture/podcasts/le-cours-de-l-histoire/episode-123")
```

### natural_language_search(query, max_results=10)

Processes a natural language query to find the most relevant content.

Example:
```
natural_language_search("Je cherche des podcasts sur la littérature française contemporaine")
```

## Example Interactions with Claude

Here are some example queries you can ask Claude when using this MCP server:

1. "Trouve-moi des podcasts de France Culture sur l'histoire romaine"
2. "Quelles sont les émissions en cours et à venir sur France Inter aujourd'hui?"
3. "Je suis intéressé par les podcasts sur l'économie, peux-tu m'en recommander quelques-uns?"
4. "Recherche des épisodes récents qui parlent de la politique européenne"
5. "Je voudrais écouter un podcast sur la philosophie, quelles sont mes options?"
6. "Peux-tu me donner plus d'informations sur l'émission 'La Terre au carré'?"
7. "Quelles sont les catégories de podcasts disponibles sur Radio France?"
8. "Comment puis-je accéder au flux audio de cette émission?"

## Troubleshooting

If you encounter issues:

1. Make sure your API key is valid and properly set in the `.env` file
2. Check your network connection to ensure you can reach the Radio France servers
3. If the web scraping features aren't working as expected, the Radio France website structure may have changed
4. For more detailed errors, check the server output in your terminal
5. The API might have rate limits, so consider implementing caching for frequent queries

## API Key Acquisition

To get a Radio France API key:

1. Visit the [Radio France API Portal](https://www.radiofrance.fr/api)
2. Create an account or sign in
3. Navigate to the developer section
4. Create a new application
5. Copy the generated API key

## Extending the Server

If you want to extend the server with additional functionality:

1. Add new tool methods to `server.py` using the `@mcp.tool()` decorator
2. Make sure to include proper error handling
3. Document the new tools in this usage guide
4. Consider contributing your improvements back to the repository

## Best Practices for Podcast Search

When searching for podcasts, consider these tips for better results:

1. Be specific with your search terms
2. Include the station name if you know it (e.g., "France Culture")
3. Use French language search terms for better matching
4. Try multiple variations of your search query if you don't get good results initially
5. Start with the `natural_language_search` tool which will automatically try different approaches

## Privacy and Usage Notes

- This tool accesses content from Radio France which is subject to their terms of service
- No user data is collected or stored by this MCP server
- API usage may be subject to rate limits from Radio France
- Consider caching frequent queries to reduce API load
