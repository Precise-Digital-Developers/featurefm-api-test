# Feature.fm Postman Collections

Postman collections for testing Feature.fm APIs interactively.

## Available Collections

### Marketing API Collection

**File:** `Feature.fm_Marketing_API.postman_collection.json`

**Covers:**

- Authentication testing
- Artist management (List, Search, Get, Create, Update)
- SmartLink operations (Get, Create, Pre-Save)
- Action Pages (List, Search, Get)

**Endpoints:** 15+ requests organized by category

## Quick Start

### 1. Import Collection

1. Open Postman
2. Click **Import** button
3. Select `Feature.fm_Marketing_API.postman_collection.json`
4. Collection will appear in your sidebar

### 2. Configure Variables

The collection uses variables that need to be set:

**Collection Variables (auto-configured):**

- `baseUrl`: `https://api.feature.fm` (already set)
- `artistId`: Auto-populated from List Artists request
- `smartlinkId`: Auto-populated from Create SmartLink
- `searchTerm`: Default search term

**Variables YOU need to set:**

1. Click on the collection name
2. Go to **Variables** tab
3. Set `apiKey` to your Feature.fm API key

**OR** create a Postman environment:

```json
{
  "name": "Feature.fm Sandbox",
  "values": [
    {
      "key": "baseUrl",
      "value": "https://api.feature.fm",
      "enabled": true
    },
    {
      "key": "apiKey",
      "value": "your_sandbox_api_key_here",
      "enabled": true
    }
  ]
}
```

### 3. Run Requests

**Recommended order:**

1. **Authentication** → Test API Key
2. **Artists** → List Artists (populates `artistId`)
3. **Artists** → Get Artist
4. **SmartLinks** → Create SmartLink (requires `artistId`)

## Request Categories

### Authentication

- **Test API Key** - Verifies API authentication by listing artists

### Artists

- **List Artists** - Get all artists (stores first artist ID)
- **Search Artists** - Search by artist name
- **Get Artist** - Get specific artist details
- **Create Artist** - Create new artist (Sandbox only)
- **Update Artist** - Update artist info (Sandbox only)

### SmartLinks

- **Get SmartLink** - Get SmartLink by ID
- **Get SmartLink by ShortId** - Get by short ID and domain
- **Create SmartLink** - Create post-release link (Sandbox only)
- **Create Pre-Save SmartLink** - Create pre-save campaign (Sandbox only)

### Action Pages

- **List Action Pages** - Get all action pages
- **Search Action Pages** - Search action pages
- **Get Action Page** - Get specific action page

## Environment Setup

### Sandbox Environment

```json
{
  "name": "Feature.fm Sandbox",
  "values": [
    {
      "key": "baseUrl",
      "value": "https://api.feature.fm",
      "enabled": true
    },
    {
      "key": "apiKey",
      "value": "your_sandbox_api_key",
      "enabled": true
    }
  ]
}
```

### Production Environment (Read-Only Recommended)

```json
{
  "name": "Feature.fm Production",
  "values": [
    {
      "key": "baseUrl",
      "value": "https://api.feature.fm",
      "enabled": true
    },
    {
      "key": "apiKey",
      "value": "your_production_api_key",
      "enabled": true
    }
  ]
}
```

**⚠️ Warning:** Disable write operations (Create, Update, Delete requests) in production environment.

## Features

### Auto-Population

The collection automatically stores IDs from responses:

- Create/List Artists → stores `artistId` and `newArtistId`
- Create SmartLink → stores `smartlinkId`

Use `{{artistId}}` in subsequent requests.

### Test Scripts

All requests include test scripts that:

- Validate response status codes
- Check response structure
- Store relevant IDs for next requests
- Log helpful debugging information

### Example Test Output

```text
✓ Status code is 200
✓ Response contains artists array
Stored artist: Test Artist 1234567890
Response time: 245ms
```

## Usage Examples

### Creating an Artist

1. Ensure `apiKey` is set in variables
2. Go to **Artists** → **Create Artist**
3. The request body uses dynamic timestamp: `Test Artist {{$timestamp}}`
4. Click **Send**
5. New artist ID is stored in `newArtistId`

### Creating a SmartLink

1. First run **List Artists** to populate `artistId`
2. Go to **SmartLinks** → **Create SmartLink**
3. Request automatically uses `{{artistId}}`
4. Click **Send**
5. SmartLink ID is stored in `smartlinkId`

### Creating a Pre-Save Campaign

1. Ensure you have a valid `artistId`
2. Go to **SmartLinks** → **Create Pre-Save SmartLink**
3. Modify `releaseDate` to a future date
4. Update Spotify URLs to valid artist/album URLs
5. Click **Send**

## API Endpoint Pattern Reference

Feature.fm uses specific patterns:

### List Operations (Plural)

- `GET /manage/v1/artists`
- `GET /manage/v1/actionpages`

### Individual Operations (Singular)

- `GET /manage/v1/artist/:artistId`
- `POST /manage/v1/artist`
- `POST /manage/v1/smartlink`

### Field Naming

All fields use **camelCase**:

- `artistName` (not `artist_name`)
- `countryCode` (not `country_code`)
- `storeId` (not `store_id`)

## Troubleshooting

### 401 Authentication Failed

- Check `apiKey` variable is set correctly
- Verify API key is active in Feature.fm dashboard
- Ensure you're using the correct environment (sandbox vs production)

### 404 Endpoint Not Found

- Verify endpoint uses correct singular/plural form
- Check base URL is `https://api.feature.fm`
- Ensure `/manage/v1` prefix is included

### 400 Validation Error

- Check request body uses camelCase field names
- Verify required fields are present
- For SmartLinks: domain must be full URI (`https://ffm.to`)
- For stores: use `storeId` not `service`

## Collection Organization

The collection is organized into folders:

```text
Feature.fm Marketing API
├── Authentication
│   └── Test API Key
├── Artists
│   ├── List Artists
│   ├── Search Artists
│   ├── Get Artist
│   ├── Create Artist
│   └── Update Artist
├── SmartLinks
│   ├── Get SmartLink
│   ├── Get SmartLink by ShortId
│   ├── Create SmartLink
│   └── Create Pre-Save SmartLink
└── Action Pages
    ├── List Action Pages
    ├── Search Action Pages
    └── Get Action Page
```

## Best Practices

1. **Always start with List Artists** - This populates necessary IDs
2. **Use Sandbox for testing** - Don't test write operations in production
3. **Check test results** - Review test output after each request
4. **Save successful responses** - Use Postman's save response feature
5. **Create environments** - Separate sandbox and production credentials

## Additional Resources

- [Feature.fm API Documentation](https://developers.feature.fm/)
- [Main Project README](../README.md)
- [Python Test Suite](../test_sandbox.py)

---

**Last Updated:** October 10, 2025
**Version:** 2.0
