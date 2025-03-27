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

## Running the Server

```bash
python server.py
```

When using with Claude Desktop, update your Claude Desktop configuration:

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

## Testing

You can test the server using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python server.py
```

## License

MIT
