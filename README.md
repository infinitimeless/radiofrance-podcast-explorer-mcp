# Radio France Podcast Explorer MCP

A Model Control Protocol (MCP) server that allows AI assistants like Claude to search for and explore podcasts, audio replays, and other content from Radio France.

## Features

- Search for podcasts and episodes by topic
- Get program information for specific Radio France stations
- Retrieve detailed podcast and episode information
- Process natural language queries to find relevant content
- Get audio content metadata and stream URLs

## Requirements

- Python 3.7+
- Radio France API Key (obtain from [Radio France Open API](https://www.radiofrance.fr/api))

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/infinitimeless/radiofrance-podcast-explorer-mcp.git
   cd radiofrance-podcast-explorer-mcp
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Radio France API key:
   ```
   RADIOFRANCE_API_KEY=your_api_key_here
   ```

## Testing

Before running the server, you can verify your installation and API key by running the tests:

```bash
python run_tests.py
```

This will run basic tests to ensure that the server can connect to the Radio France API and retrieve data.

## Running the Server

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

## Development Testing

You can test the server using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python server.py
```

This will open a web interface where you can test each of the server's tools individually.

## Documentation

For more detailed information, see:

- [Usage Guide](docs/usage.md) - Detailed instructions on using the server
- [API Information](docs/api_info.md) - Information about the Radio France API

## Example Queries for Claude

Here are some example queries you can ask Claude when using this MCP server:

1. "Find me podcasts about French history"
2. "What's currently playing on France Inter?"
3. "Search for podcast episodes about European politics"
4. "What are the different podcast categories on Radio France?"
5. "Get me information about the audio content at this URL"

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
