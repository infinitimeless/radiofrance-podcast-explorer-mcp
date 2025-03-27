# Radio France API Information

This document provides details about the Radio France API used in this project.

## API Overview

The Radio France API is a GraphQL API that allows access to various content from Radio France including podcasts, episodes, live streams, and program information. It requires an API key for authentication.

## API Endpoint

```
https://openapi.radiofrance.fr/v1/graphql
```

## Authentication

Authentication is performed by including your API key in the request headers:

```
x-token: YOUR_API_KEY
```

## Main Entity Types

The API provides access to several entity types:

1. **Stations**: Radio France broadcast channels (France Inter, France Culture, etc.)
2. **Shows**: Regular radio programs
3. **Episodes**: Individual podcast episodes
4. **Persons**: Contributors, hosts, guests
5. **Topics**: Subject categories and tags

## Common GraphQL Queries

### Search

This query searches across multiple entity types:

```graphql
query Search($query: String!, $limit: Int!) {
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
    }
    episodes {
      title
      description
      url
      publishedDate
      duration
    }
  }
}
```

### Station Programs

This query retrieves current and upcoming programs for a station:

```graphql
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
```

### Show Details

This query gets detailed information about a specific show:

```graphql
query ShowDetails($showId: ID!) {
  show(id: $showId) {
    title
    description
    url
    podcast {
      url
    }
    station {
      name
    }
    latestEpisodes(first: 10) {
      title
      description
      url
      publishedDate
      duration
    }
    persons {
      name
      role
    }
  }
}
```

## Web Scraping Supplement

Because the API may not provide all the information we need, this project also implements web scraping to extract additional data from the Radio France website. This includes:

- Podcast categories
- Detailed episode information
- Audio stream URLs
- Additional metadata

The selectors used in the web scraping code may need to be updated if the Radio France website structure changes.

## API Limitations

- Rate limits may apply (consult the API documentation for current limits)
- Not all content may be accessible via the API
- Some newer features may not be available
- The API structure could change over time

## Best Practices

1. Cache results when possible to minimize API calls
2. Implement proper error handling for API failures
3. Consider fallback options when the API is unavailable
4. Keep selectors updated for web scraping
5. Follow Radio France's terms of service

## Further Information

For more detailed information on the Radio France API, visit the [Radio France API Portal](https://www.radiofrance.fr/api).
