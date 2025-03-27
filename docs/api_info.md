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

1. **Taxonomies**: Categories, tags, and themes that organize content
2. **Diffusions**: Content items (episodes, programs) associated with taxonomies
3. **Brands**: Shows and podcast series
4. **Grid**: Program schedules for stations
5. **Stations**: Radio France broadcast channels (France Inter, France Culture, etc.)
6. **Persons**: Contributors, hosts, guests

## Content Organization

Radio France's API follows a taxonomy-driven approach to content organization:

1. Content is primarily organized through taxonomies (themes, categories, tags)
2. Accessing content requires a two-step process:
   - First get taxonomy IDs related to your search
   - Then query diffusions using those taxonomy IDs
3. Stations have program grids that provide scheduling information
4. Brands (shows) have associated diffusions (episodes)

## Common GraphQL Queries

### Get Taxonomies

This query retrieves taxonomies (categories, themes, tags):

```graphql
query GetTaxonomies($limit: Int!, $keyword: String) {
  taxonomies(limit: $limit, keyword: $keyword) {
    id
    title
    type
    url
    description
  }
}
```

### Get Diffusions by Taxonomy

This query retrieves content items for a specific taxonomy:

```graphql
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
```

### Get Station Grid

This query retrieves current and upcoming programs for a station:

```graphql
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
```

### Get Brand Information

This query retrieves information about a specific brand (show/program):

```graphql
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
