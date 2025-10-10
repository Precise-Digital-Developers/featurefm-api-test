# Feature.fm Marketing API Documentation

## Overview

Feature.fm is a comprehensive music marketing and distribution platform that enables artists, labels, and music industry professionals to create intelligent SmartLinks, manage artist profiles, and track music campaign performance across multiple streaming platforms.

The Feature.fm Marketing API provides programmatic access to:
- Artist profile management and configuration
- SmartLink creation and management (post-release, pre-save, future release)
- Action page management
- Multi-platform music distribution routing
- Advanced analytics and conversion tracking
- Pre-save campaign orchestration

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Authentication](#authentication)
4. [Core Concepts](#core-concepts)
5. [API Endpoints](#api-endpoints)
6. [Testing Strategy](#testing-strategy)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Postman Collection](#postman-collection)

## Prerequisites

### Required Tools

- **Postman**: Version 9.0+ (Desktop or Web)
- **API Key**: Obtained from Feature.fm dashboard
- **Network Access**: HTTPS access to `api.feature.fm`

### Environment Details

| Environment | Base URL | Purpose |
|------------|----------|---------|
| Production | `https://api.feature.fm` | Live music marketing operations |

**Note**: Feature.fm uses a unified production API. Sandbox testing should be performed using test artist profiles and clearly marked test data.

## Quick Start

### 1. Import the Postman Collection

1. Download the `Feature.fm_Marketing_API.postman_collection.json` from the `postman_collections` directory
2. Open Postman and click **Import**
3. Select the JSON file and import
4. The collection appears in your workspace as "Feature.fm Marketing API"

### 2. Configure Environment Variables

Create a new Postman environment named "Feature.fm Production" with these variables:

```json
{
  "baseUrl": "https://api.feature.fm",
  "apiKey": "your_api_key_here",
  "artistId": "",
  "newArtistId": "",
  "smartlinkId": "",
  "searchTerm": "test"
}
```

**Collection Variables (auto-configured):**
- `baseUrl`: `https://api.feature.fm` (pre-set)
- `artistId`: Auto-populated from List Artists request
- `newArtistId`: Auto-populated from Create Artist
- `smartlinkId`: Auto-populated from Create SmartLink
- `searchTerm`: Default search term for testing

**Variables YOU need to set:**
- `apiKey`: Your Feature.fm API key from the dashboard

### 3. Authenticate

1. Select the "Feature.fm Production" environment
2. Navigate to Authentication > Test API Key
3. Click **Send** to verify your API key
4. Successful response indicates authentication is working

### 4. Test the Connection

Run the Test API Key endpoint:
```
GET {{baseUrl}}/manage/v1/artists
```

Expected response:
```json
{
  "data": [
    {
      "id": "artist_123",
      "artistName": "Artist Name",
      "type": "artist",
      "countryCode": "US"
    }
  ]
}
```

## Authentication

Feature.fm uses API key authentication with a simple header-based approach.

### Authentication Method

**Header**: `x-api-key`

**Value**: Your API key from Feature.fm dashboard

### Obtaining API Key

1. Log in to your Feature.fm dashboard
2. Navigate to Settings > API Access
3. Generate or copy your API key
4. Store securely (treat as a password)

### Using the API Key

Include the API key in every request header:

```http
x-api-key: your_api_key_here
```

The Postman collection automatically includes this header using the `{{apiKey}}` variable.

### Security Best Practices

- **Never commit API keys** to version control
- **Use environment variables** in Postman
- **Store in `.env` files** for automated tests
- **Rotate keys periodically** for security
- **Use read-only keys** when possible for testing

## Core Concepts

### Artists

Artists are the core entities in Feature.fm representing musicians, bands, labels, or music brands. Each artist profile includes:

- **Basic Information**: Name, type, country, bio
- **Visual Assets**: Profile images, background images
- **Social Links**: Spotify, Apple Music, Instagram, etc.
- **Configuration**: Default link settings, routing preferences
- **Metadata**: Tags, categories, custom properties

### SmartLinks

SmartLinks are intelligent, multi-platform distribution links that route users to the appropriate music streaming service based on:

- **User Location**: Geographic routing
- **Device Type**: Mobile, desktop, tablet
- **User Preferences**: Previously used services
- **Link Configuration**: Custom routing rules

#### SmartLink Types

1. **Post-Release Links**: For already-released music
2. **Future Release Links**: For upcoming releases with countdown
3. **Pre-Save Links**: Campaign to save music before release

### Action Pages

Action pages are landing pages that can include:
- Music links
- Call-to-action buttons
- Email capture forms
- Social sharing widgets
- Custom branding

### Music Stores

Supported streaming platforms (identified by `storeId`):

| Store ID | Platform | Notes |
|----------|----------|-------|
| `spotify` | Spotify | Most common platform |
| `apple` | Apple Music | Requires valid Apple Music URL |
| `youtube` | YouTube Music | Video or music URL |
| `amazon` | Amazon Music | |
| `deezer` | Deezer | |
| `tidal` | Tidal | |
| `soundcloud` | SoundCloud | |
| `audiomack` | Audiomack | |

## API Endpoints

### Base URL
```
https://api.feature.fm
```

All endpoints are prefixed with `/manage/v1/`

---

### Artists Management

#### 1. List Artists
`GET /manage/v1/artists`

Retrieve all artists associated with your account.

**Query Parameters:**
- None (pagination may be supported)

**Response:**
```json
{
  "data": [
    {
      "id": "artist_123abc",
      "artistName": "The Example Band",
      "type": "artist",
      "countryCode": "US",
      "shortBio": "An amazing band from California",
      "artistImage": "https://cdn.feature.fm/images/artist_123.jpg",
      "tags": ["rock", "indie"]
    }
  ]
}
```

**Postman Auto-Population:**
- Stores first artist's `id` in `{{artistId}}` variable
- Stores artist name in `{{artistName}}` variable

---

#### 2. Search Artists
`GET /manage/v1/artists/search`

Search for artists by name.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `term` | string | Yes | Search term for artist name |

**Example:**
```
GET /manage/v1/artists/search?term=example
```

**Response:**
```json
{
  "data": [
    {
      "id": "artist_456def",
      "artistName": "Example Artist",
      "type": "artist",
      "countryCode": "GB"
    }
  ]
}
```

---

#### 3. Get Artist
`GET /manage/v1/artist/:artistId`

Retrieve detailed information about a specific artist.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `artistId` | string | Yes | Unique artist identifier |

**Example:**
```
GET /manage/v1/artist/artist_123abc
```

**Response:**
```json
{
  "data": {
    "id": "artist_123abc",
    "artistName": "The Example Band",
    "type": "artist",
    "countryCode": "US",
    "shortBio": "Detailed biography...",
    "artistImage": "https://cdn.feature.fm/images/artist_123.jpg",
    "backgroundImage": "https://cdn.feature.fm/images/bg_123.jpg",
    "tags": ["rock", "indie", "alternative"],
    "socialLinks": {
      "spotify": "https://open.spotify.com/artist/...",
      "apple": "https://music.apple.com/artist/...",
      "instagram": "https://instagram.com/example"
    },
    "createdAt": "2024-01-15T10:00:00Z",
    "updatedAt": "2024-10-01T14:30:00Z"
  }
}
```

---

#### 4. Create Artist
`POST /manage/v1/artist`

Create a new artist profile.

**Request Headers:**
```http
Content-Type: application/json
x-api-key: your_api_key_here
```

**Request Body:**
```json
{
  "artistName": "New Artist Name",
  "type": "artist",
  "countryCode": "US",
  "shortBio": "Artist biography and description",
  "artistImage": "https://example.com/artist-image.jpg",
  "tags": ["genre1", "genre2"]
}
```

**Required Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `artistName` | string | Artist or band name |
| `type` | string | Usually "artist" |
| `countryCode` | string | ISO 2-letter country code (e.g., "US", "GB") |

**Optional Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `shortBio` | string | Artist biography |
| `artistImage` | string | URL to artist profile image |
| `backgroundImage` | string | URL to background/header image |
| `tags` | array | Array of genre/category tags |

**Response:**
```json
{
  "data": {
    "id": "artist_789xyz",
    "artistName": "New Artist Name",
    "type": "artist",
    "countryCode": "US",
    "shortBio": "Artist biography and description",
    "artistImage": "https://example.com/artist-image.jpg",
    "tags": ["genre1", "genre2"],
    "createdAt": "2025-10-10T12:00:00Z"
  }
}
```

**Postman Auto-Population:**
- Stores created artist's `id` in `{{newArtistId}}` variable
- Uses `{{$timestamp}}` for unique test artist names

---

#### 5. Update Artist
`PUT /manage/v1/artist/:artistId`

Update an existing artist's information.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `artistId` | string | Yes | Artist ID to update |

**Request Body:**
```json
{
  "artistName": "Updated Artist Name",
  "shortBio": "Updated biography with new information",
  "tags": ["updated", "new-genre"]
}
```

**Notes:**
- Only include fields you want to update
- Partial updates are supported
- Omitted fields remain unchanged

**Response:**
```json
{
  "data": {
    "id": "artist_789xyz",
    "artistName": "Updated Artist Name",
    "shortBio": "Updated biography with new information",
    "tags": ["updated", "new-genre"],
    "updatedAt": "2025-10-10T13:00:00Z"
  }
}
```

---

### SmartLinks Management

#### 1. Get SmartLink
`GET /manage/v1/smartlink/:smartlinkId`

Retrieve details of a specific SmartLink.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `smartlinkId` | string | Yes | Unique SmartLink identifier |

**Example:**
```
GET /manage/v1/smartlink/smartlink_123abc
```

**Response:**
```json
{
  "data": {
    "id": "smartlink_123abc",
    "artistId": "artist_456def",
    "shortId": "my-song",
    "domain": "https://ffm.to",
    "url": "https://ffm.to/my-song",
    "title": "My Awesome Song",
    "image": "https://cdn.feature.fm/images/cover_123.jpg",
    "description": "Check out this new track!",
    "stores": [
      {
        "storeId": "spotify",
        "url": "https://open.spotify.com/track/..."
      },
      {
        "storeId": "apple",
        "url": "https://music.apple.com/us/album/..."
      }
    ],
    "createdAt": "2025-09-15T10:00:00Z"
  }
}
```

---

#### 2. Get SmartLink by ShortId
`GET /manage/v1/smartlink/shortid/:shortId`

Retrieve SmartLink using its short ID and domain.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `shortId` | string | Yes | Short identifier (e.g., "my-song") |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `domain` | string | Yes | Domain (e.g., "ffm.to") |

**Example:**
```
GET /manage/v1/smartlink/shortid/my-song?domain=ffm.to
```

**Response:**
Same format as Get SmartLink endpoint.

---

#### 3. Create SmartLink (Post-Release)
`POST /manage/v1/smartlink`

Create a SmartLink for already-released music.

**Request Headers:**
```http
Content-Type: application/json
x-api-key: your_api_key_here
```

**Request Body:**
```json
{
  "artistId": "artist_123abc",
  "shortId": "my-new-song",
  "domain": "https://ffm.to",
  "title": "My New Song Title",
  "image": "https://example.com/cover.jpg",
  "description": "Official release - listen now!",
  "stores": [
    {
      "storeId": "spotify",
      "url": "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"
    },
    {
      "storeId": "apple",
      "url": "https://music.apple.com/us/album/example/123456789"
    },
    {
      "storeId": "youtube",
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }
  ]
}
```

**Required Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `artistId` | string | Associated artist ID |
| `shortId` | string | Unique short identifier (URL slug) |
| `domain` | string | Full domain URL (e.g., "https://ffm.to") |
| `title` | string | Song/album title |
| `stores` | array | Array of music store objects |

**Store Object Structure:**
```json
{
  "storeId": "spotify",
  "url": "https://open.spotify.com/track/..."
}
```

**Optional Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `image` | string | Cover art URL |
| `description` | string | Link description/meta text |
| `backgroundColor` | string | Hex color for page background |
| `buttonColor` | string | Hex color for buttons |

**Response:**
```json
{
  "data": {
    "id": "smartlink_789new",
    "artistId": "artist_123abc",
    "shortId": "my-new-song",
    "domain": "https://ffm.to",
    "url": "https://ffm.to/my-new-song",
    "title": "My New Song Title",
    "stores": [...],
    "createdAt": "2025-10-10T12:00:00Z"
  }
}
```

**Postman Auto-Population:**
- Stores created SmartLink's `id` in `{{smartlinkId}}` variable
- Uses `{{artistId}}` from List Artists
- Uses `{{$timestamp}}` for unique test links

---

#### 4. Create Pre-Save SmartLink
`POST /manage/v1/smartlink/pre-save`

Create a pre-save campaign for upcoming music releases.

**Request Headers:**
```http
Content-Type: application/json
x-api-key: your_api_key_here
```

**Request Body:**
```json
{
  "artistId": "artist_123abc",
  "shortId": "presave-new-album",
  "domain": "https://ffm.to",
  "title": "Pre-Save Our New Album",
  "image": "https://example.com/album-cover.jpg",
  "releaseDate": "2025-12-31",
  "timezone": "America/New_York",
  "stores": [
    {
      "storeId": "spotify",
      "url": "https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3"
    }
  ],
  "preSaveFollow": [
    {
      "storeId": "spotify",
      "entities": [
        {
          "url": "https://open.spotify.com/artist/0TnOYISbd1XYRBk9myaseg"
        }
      ]
    }
  ]
}
```

**Required Fields for Pre-Save:**
| Field | Type | Description |
|-------|------|-------------|
| `artistId` | string | Associated artist ID |
| `shortId` | string | Unique short identifier |
| `domain` | string | Full domain URL |
| `title` | string | Campaign title |
| `releaseDate` | string | Release date (YYYY-MM-DD) |
| `timezone` | string | Timezone for release (e.g., "America/New_York") |
| `stores` | array | Music store objects (album/track URLs) |

**Pre-Save Specific Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `preSaveFollow` | array | Artist profiles to follow during pre-save |

**preSaveFollow Object Structure:**
```json
{
  "storeId": "spotify",
  "entities": [
    {
      "url": "https://open.spotify.com/artist/..."
    }
  ]
}
```

**Response:**
```json
{
  "data": {
    "id": "smartlink_presave123",
    "artistId": "artist_123abc",
    "shortId": "presave-new-album",
    "url": "https://ffm.to/presave-new-album",
    "title": "Pre-Save Our New Album",
    "releaseDate": "2025-12-31",
    "timezone": "America/New_York",
    "type": "pre-save",
    "createdAt": "2025-10-10T12:00:00Z"
  }
}
```

**Pre-Save Campaign Features:**
- **Countdown Timer**: Displays time until release
- **Auto-Save**: Automatically adds to user's library on release
- **Artist Follow**: Optionally follows artist during pre-save
- **Email Capture**: Collects fan emails for marketing
- **Social Sharing**: Encourages campaign sharing

---

#### 5. Create Future Release SmartLink
`POST /manage/v1/smartlink/future-release`

Create a SmartLink for upcoming releases with countdown functionality.

**Request Body:**
Similar to pre-save, but without the `preSaveFollow` field:

```json
{
  "artistId": "artist_123abc",
  "shortId": "upcoming-single",
  "domain": "https://ffm.to",
  "title": "Coming Soon - New Single",
  "image": "https://example.com/teaser.jpg",
  "releaseDate": "2025-11-15",
  "timezone": "America/Los_Angeles",
  "stores": [...]
}
```

**Difference from Pre-Save:**
- No automatic save functionality
- Countdown to release date
- Links become active on release date
- Used for announcements and teasers

---

### Action Pages Management

#### 1. List Action Pages
`GET /manage/v1/actionpages`

Retrieve all action pages associated with your account.

**Response:**
```json
{
  "data": [
    {
      "id": "actionpage_123",
      "title": "Newsletter Signup",
      "url": "https://ffm.to/newsletter",
      "type": "email-capture",
      "createdAt": "2025-08-01T10:00:00Z"
    }
  ]
}
```

---

#### 2. Search Action Pages
`GET /manage/v1/actionpages/search`

Search for action pages.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `term` | string | Yes | Search term |

**Example:**
```
GET /manage/v1/actionpages/search?term=newsletter
```

---

#### 3. Get Action Page
`GET /manage/v1/actionpage/:actionPageId`

Retrieve details of a specific action page.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `actionPageId` | string | Yes | Action page identifier |

**Example:**
```
GET /manage/v1/actionpage/actionpage_123
```

---

## Testing Strategy

### Test Organization

The Postman collection includes comprehensive test coverage organized into four main categories:

#### 1. Authentication Tests
- API key validation
- Authentication failure handling
- Access verification

#### 2. Artist Tests
- CRUD operations (Create, Read, Update)
- Search functionality
- ID auto-population
- Data validation

#### 3. SmartLink Tests
- Post-release link creation
- Pre-save campaign setup
- Future release configuration
- Store URL validation

#### 4. Action Page Tests
- List and search operations
- Page retrieval
- Content validation

### Automated Testing

#### Pre-request Scripts

The collection includes global pre-request scripts:

```javascript
// Log request for debugging
console.log(`Request: ${pm.request.method} ${pm.request.url.getPath()}`);
```

#### Test Scripts

Each request includes validation tests:

```javascript
// Status code validation
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});

// Response structure validation
pm.test('Response contains data', function () {
    const response = pm.response.json();
    pm.expect(response).to.have.property('data');
});

// Auto-population of variables
if (pm.response.code === 200) {
    const response = pm.response.json();
    if (response.data && response.data.id) {
        pm.environment.set('artistId', response.data.id);
        console.log('Stored artist ID:', response.data.id);
    }
}
```

#### Global Test Scripts

Applied to all requests:

```javascript
// No server errors
pm.test('No server errors (5xx)', function () {
    pm.expect(pm.response.code).to.be.below(500);
});

// Log response time
console.log(`Response time: ${pm.response.responseTime}ms`);

// Handle authentication errors
if (pm.response.code === 401) {
    console.error('Authentication failed - check API key');
}
```

### Test Data Management

**Best Practices:**
1. **Use Dynamic Data**: Utilize `{{$timestamp}}` for unique test data
2. **Clean Test Data**: Regularly clean up test artists/links
3. **Mark Test Data**: Use prefixes like "Test_" or "Postman_"
4. **Avoid Production Data**: Never modify real artist profiles during testing

**Example Test Artist:**
```json
{
  "artistName": "Test Artist {{$timestamp}}",
  "type": "artist",
  "countryCode": "US",
  "shortBio": "Created via Postman API test",
  "tags": ["postman", "test"]
}
```

### Recommended Test Workflow

1. **Start with Authentication**: Run "Test API Key" first
2. **List Artists**: Populates `{{artistId}}` for subsequent tests
3. **Get Artist**: Verify individual artist retrieval
4. **Create Artist**: Test artist creation (optional)
5. **Create SmartLink**: Test SmartLink creation using `{{artistId}}`
6. **Get SmartLink**: Verify SmartLink retrieval
7. **List Action Pages**: Test action page access

### Running Collection Tests

**Newman CLI** (for automated testing):
```bash
newman run Feature.fm_Marketing_API.postman_collection.json \
  --environment Feature_fm_Production.postman_environment.json \
  --reporters cli,json
```

**Postman Collection Runner**:
1. Click "Run" on the collection
2. Select "Feature.fm Production" environment
3. Choose requests to run
4. Click "Run Feature.fm Marketing API"

## Error Handling

### Error Response Format

All errors follow a consistent JSON structure:

```json
{
  "status": 1,
  "message": "Error description here"
}
```

**Success Response:**
```json
{
  "status": 0,
  "data": { ... }
}
```

**Error Indicators:**
- `status: 0` = Success
- `status: 1` (or non-zero) = Error
- `message` field contains error description

### Common HTTP Status Codes

| Status Code | Meaning | Cause | Solution |
|-------------|---------|-------|----------|
| 200 | OK | Request successful | N/A |
| 400 | Bad Request | Invalid parameters or malformed request | Check request body format, field names (camelCase), required fields |
| 401 | Unauthorized | Missing or invalid API key | Verify `x-api-key` header, check API key is active |
| 404 | Not Found | Endpoint or resource doesn't exist | Check endpoint URL, verify singular/plural form, confirm resource ID exists |
| 409 | Conflict | Duplicate resource | `shortId` already exists, use different identifier |
| 422 | Unprocessable Entity | Validation error | Review field requirements, check URL formats for stores |
| 429 | Too Many Requests | Rate limit exceeded | Implement request throttling, retry with exponential backoff |
| 500 | Internal Server Error | Server-side error | Retry request, contact support if persists |

### Common Error Scenarios

#### 1. Authentication Failed (401)

**Error:**
```json
{
  "status": 1,
  "message": "Unauthorized: Invalid API key"
}
```

**Causes:**
- Missing `x-api-key` header
- Incorrect API key value
- API key revoked or expired

**Solutions:**
- Verify API key in Postman environment
- Check Feature.fm dashboard for active API keys
- Ensure header is included in request

---

#### 2. Invalid Parameter (400)

**Error:**
```json
{
  "status": 1,
  "message": "invalid parameter: countryCode"
}
```

**Causes:**
- Missing required field
- Invalid field value
- Wrong data type
- Incorrect field name (e.g., `country_code` instead of `countryCode`)

**Solutions:**
- Verify all required fields are present
- Use camelCase for field names
- Check field value formats (e.g., country codes must be 2-letter ISO)
- Review endpoint documentation for requirements

---

#### 3. Resource Not Found (404)

**Error:**
```json
{
  "status": 1,
  "message": "Artist not found"
}
```

**Causes:**
- Invalid artist/smartlink ID
- Resource deleted
- Wrong endpoint URL

**Solutions:**
- Verify resource ID exists
- Check for typos in ID
- Ensure using correct endpoint

---

#### 4. Duplicate Resource (409)

**Error:**
```json
{
  "status": 1,
  "message": "SmartLink with shortId 'my-song' already exists"
}
```

**Causes:**
- `shortId` already in use
- Attempting to create duplicate resource

**Solutions:**
- Use unique `shortId` for each SmartLink
- Check existing SmartLinks before creating
- Append timestamp for test data: `test-{{$timestamp}}`

---

#### 5. Validation Error (422)

**Error:**
```json
{
  "status": 1,
  "message": "Invalid Spotify URL format"
}
```

**Causes:**
- Invalid URL format for music stores
- Malformed store object
- Invalid `storeId`

**Solutions:**
- Verify music platform URLs are valid
- Use correct `storeId` values (see [Music Stores](#music-stores))
- Test URLs in browser before using in API
- Ensure `domain` field uses full URL: `https://ffm.to`

---

### Error Recovery Strategies

1. **401 Unauthorized**:
   - Check API key configuration
   - Verify key is active in dashboard
   - Regenerate key if needed

2. **400/422 Validation Errors**:
   - Review request body against documentation
   - Validate field names use camelCase
   - Check required vs optional fields

3. **404 Not Found**:
   - Verify resource IDs
   - Check endpoint URL structure
   - Confirm singular vs plural endpoints

4. **409 Conflict**:
   - Use unique identifiers
   - Check for existing resources
   - Implement uniqueness checks

5. **429 Rate Limited**:
   - Implement request throttling
   - Add delays between requests
   - Use exponential backoff

6. **500 Server Errors**:
   - Retry request (may be temporary)
   - Check Feature.fm status page
   - Contact support if persistent

## Best Practices

### API Integration Best Practices

#### 1. Song Promotion Strategies

Feature.fm is designed to help artists gain exposure through strategic promotion placement:

**In-Stream Promotion:**
- Automatically play featured songs after every X number of songs
- Mimics traditional radio discovery model
- Provides seamless user experience
- Monetizes airplay without disruption

**In-Search Promotion:**
- Display featured songs in search results
- Similar to sponsored search results
- Helps artists gain playlist exposure
- Targets users actively searching for music

**In-Discovery Promotion:**
- Feature songs in discovery sections:
  - Music News Feed
  - Popular Songs
  - Music Charts
  - Trending Tracks
  - Genre Playlists

**Key Principle**: The goal is to help artists gain exposure by integrating promoted songs prominently while maintaining a natural user experience.

---

#### 2. SmartLink Best Practices

**Naming Conventions:**
- Use descriptive, URL-friendly `shortId` values
- Keep short IDs lowercase with hyphens
- Include artist/song identifiers
- Avoid special characters

**Examples:**
```
✅ Good: "artist-name-song-title"
✅ Good: "album-name-presave"
✅ Good: "new-single-2025"

❌ Avoid: "link1", "test", "asdf123"
❌ Avoid: "Song Title!!!" (special chars)
❌ Avoid: "This_Is_A_Very_Long_Link_Name"
```

**Store URLs:**
- Always use official platform URLs
- Test URLs in browser before using
- Include all required URL components
- Prefer track/album URLs over artist URLs

**Platform URL Formats:**

| Platform | URL Format | Example |
|----------|------------|---------|
| Spotify Track | `open.spotify.com/track/[ID]` | `https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp` |
| Spotify Album | `open.spotify.com/album/[ID]` | `https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3` |
| Apple Music | `music.apple.com/[region]/album/[name]/[id]` | `https://music.apple.com/us/album/example/123456789` |
| YouTube | `youtube.com/watch?v=[ID]` | `https://www.youtube.com/watch?v=dQw4w9WgXcQ` |

---

#### 3. Pre-Save Campaign Best Practices

**Timing:**
- Launch campaigns 2-4 weeks before release
- Set release date and timezone accurately
- Coordinate with marketing calendar

**Configuration:**
- Always include artist follow in `preSaveFollow`
- Use high-quality cover art (minimum 1000x1000px)
- Write compelling campaign descriptions
- Enable email capture for fan database

**Follow-Up:**
- Send thank you emails after pre-save
- Remind fans on release day
- Share conversion metrics with artists

**Example Pre-Save Campaign:**
```json
{
  "title": "Pre-Save 'Album Name' - Out Nov 15",
  "releaseDate": "2025-11-15",
  "timezone": "America/New_York",
  "description": "Be the first to hear our new album! Pre-save now and get notified when it drops.",
  "preSaveFollow": [
    {
      "storeId": "spotify",
      "entities": [
        {
          "url": "https://open.spotify.com/artist/[ARTIST_ID]"
        }
      ]
    }
  ]
}
```

---

#### 4. Data Management

**Tagging Strategy:**
- Use consistent tag taxonomy
- Include genre tags for categorization
- Add campaign tags (e.g., "fall-2025", "promo")
- Mark test data appropriately

**Example Tagging:**
```json
{
  "tags": [
    "indie-rock",          // Genre
    "fall-2025",           // Campaign/timeframe
    "new-release",         // Category
    "featured"             // Status
  ]
}
```

**Environment Separation:**
- Use different API keys for testing vs production
- Mark test artists clearly (e.g., "TEST - Artist Name")
- Clean up test data regularly
- Never modify production data during tests

---

#### 5. Performance Optimization

**Caching:**
- Cache artist data for frequently accessed profiles
- Store SmartLink data to reduce API calls
- Implement client-side caching where appropriate

**Batch Operations:**
- When creating multiple SmartLinks, do so in sequence
- Implement queuing for bulk operations
- Monitor rate limits during bulk operations

**Error Handling:**
- Implement retry logic for transient errors
- Log all API errors for debugging
- Provide user-friendly error messages
- Monitor error rates and patterns

---

#### 6. Security

**API Key Management:**
- Never expose API keys in client-side code
- Use environment variables for key storage
- Rotate keys periodically
- Revoke unused or compromised keys immediately

**Data Privacy:**
- Don't log sensitive user information
- Follow GDPR guidelines for email collection
- Provide clear privacy policies
- Allow user data deletion requests

---

#### 7. SmartLink Configuration

**Domain Usage:**
- Always use full URL for `domain` field: `https://ffm.to`
- Don't use `ffm.to` without protocol
- Verify domain is available for your account

**Customization:**
- Set custom colors for brand consistency
- Use high-quality images (recommended: 1000x1000px minimum)
- Include descriptive metadata for SEO
- Enable social sharing features

**Analytics:**
- Monitor SmartLink performance
- Track conversion rates
- Analyze geographic distribution
- Identify top-performing platforms

---

### Postman-Specific Best Practices

#### Variable Management

**Use Environment Variables:**
```javascript
// Store frequently used IDs
pm.environment.set('artistId', response.data.id);

// Retrieve in subsequent requests
{{artistId}}
```

**Dynamic Test Data:**
```javascript
// Use Postman dynamic variables
"artistName": "Test Artist {{$timestamp}}"
"shortId": "test-{{$randomInt}}"
"email": "test-{{$guid}}@example.com"
```

#### Request Organization

**Folder Structure:**
```
Feature.fm Marketing API/
├── Authentication/
│   └── Test API Key
├── Artists/
│   ├── List Artists
│   ├── Search Artists
│   ├── Get Artist
│   ├── Create Artist
│   └── Update Artist
├── SmartLinks/
│   ├── Get SmartLink
│   ├── Create SmartLink
│   └── Create Pre-Save
└── Action Pages/
    ├── List Action Pages
    └── Get Action Page
```

#### Test Script Patterns

**Store IDs for Chaining:**
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    if (response.data && response.data.id) {
        pm.environment.set('artistId', response.data.id);
        console.log('✓ Stored artistId:', response.data.id);
    }
}
```

**Validate Response Structure:**
```javascript
pm.test('Response has correct structure', function () {
    const response = pm.response.json();
    pm.expect(response).to.have.property('data');
    pm.expect(response.data).to.have.property('id');
    pm.expect(response.data).to.have.property('artistName');
});
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: 401 Authentication Failed

**Symptom:**
```json
{
  "status": 1,
  "message": "Unauthorized"
}
```

**Troubleshooting Steps:**
1. ✓ Check `apiKey` variable is set in environment
2. ✓ Verify API key is correct (copy from dashboard)
3. ✓ Ensure environment is selected in Postman (top-right dropdown)
4. ✓ Confirm `x-api-key` header is present in request
5. ✓ Check API key status in Feature.fm dashboard
6. ✓ Try regenerating API key if issue persists

**Common Causes:**
- Environment not selected
- Typo in API key
- API key revoked
- Missing header

---

#### Issue: 404 Endpoint Not Found

**Symptom:**
```json
{
  "status": 1,
  "message": "Not found"
}
```

**Troubleshooting Steps:**
1. ✓ Verify endpoint uses correct singular/plural form
   - List: `/artists` (plural)
   - Individual: `/artist/:id` (singular)
2. ✓ Check base URL is `https://api.feature.fm`
3. ✓ Ensure `/manage/v1` prefix is included
4. ✓ Verify path parameters are populated (not `:artistId`)

**Correct Endpoint Patterns:**
```
✅ GET /manage/v1/artists
✅ GET /manage/v1/artist/artist_123
✅ POST /manage/v1/smartlink

❌ GET /manage/v1/artist (missing ID)
❌ GET /manage/v1/artist/:artistId (literal :artistId)
❌ GET /artists (missing prefix)
```

---

#### Issue: 400 Validation Error

**Symptom:**
```json
{
  "status": 1,
  "message": "invalid parameter: countryCode"
}
```

**Troubleshooting Steps:**
1. ✓ Check all field names use **camelCase** (not snake_case)
   - ✅ `artistName`, `countryCode`, `shortId`
   - ❌ `artist_name`, `country_code`, `short_id`
2. ✓ Verify required fields are present
3. ✓ Check field data types match documentation
4. ✓ Validate special field formats:
   - `countryCode`: 2-letter ISO code (e.g., "US", "GB")
   - `domain`: Full URL with protocol (`https://ffm.to`)
   - `storeId`: Valid platform identifier

**Field Naming Reference:**
```json
{
  "artistName": "string",        // ✅ camelCase
  "countryCode": "US",           // ✅ camelCase
  "shortBio": "text",            // ✅ camelCase
  "artist_name": "string"        // ❌ snake_case (WRONG)
}
```

---

#### Issue: SmartLink Creation Fails

**Symptom:**
```json
{
  "status": 1,
  "message": "Invalid store URL"
}
```

**Troubleshooting Steps:**
1. ✓ Test all store URLs in browser
2. ✓ Verify `storeId` matches platform:
   - Spotify: `"storeId": "spotify"`
   - Apple Music: `"storeId": "apple"`
   - YouTube: `"storeId": "youtube"`
3. ✓ Check URL formats are correct (see [Platform URL Formats](#2-smartlink-best-practices))
4. ✓ Ensure `domain` uses full URL: `"domain": "https://ffm.to"`
5. ✓ Verify `shortId` is unique and URL-friendly
6. ✓ Check `artistId` exists and is valid

**Valid Store Object:**
```json
{
  "stores": [
    {
      "storeId": "spotify",
      "url": "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"
    }
  ]
}
```

**Common Mistakes:**
```json
// ❌ Wrong storeId
{
  "storeId": "Spotify",  // Should be lowercase "spotify"
}

// ❌ Invalid URL
{
  "storeId": "spotify",
  "url": "spotify:track:123"  // Should be full HTTPS URL
}

// ❌ Wrong domain format
{
  "domain": "ffm.to"  // Should be "https://ffm.to"
}
```

---

#### Issue: Pre-Save Campaign Not Working

**Symptom:**
Pre-save link created but not functioning as expected.

**Troubleshooting Steps:**
1. ✓ Verify `releaseDate` is in future (YYYY-MM-DD format)
2. ✓ Check `timezone` is valid (e.g., "America/New_York")
3. ✓ Ensure `preSaveFollow` contains valid artist URLs
4. ✓ Confirm Spotify URLs are for albums (not tracks)
5. ✓ Test in browser to see user-facing errors

**Valid Pre-Save Configuration:**
```json
{
  "releaseDate": "2025-12-31",          // Future date
  "timezone": "America/New_York",       // Valid timezone
  "stores": [
    {
      "storeId": "spotify",
      "url": "https://open.spotify.com/album/[ID]"  // Album URL
    }
  ],
  "preSaveFollow": [
    {
      "storeId": "spotify",
      "entities": [
        {
          "url": "https://open.spotify.com/artist/[ID]"  // Artist URL
        }
      ]
    }
  ]
}
```

---

#### Issue: Variables Not Auto-Populating

**Symptom:**
`{{artistId}}` or other variables show as empty in requests.

**Troubleshooting Steps:**
1. ✓ Verify environment is selected (top-right in Postman)
2. ✓ Run "List Artists" request first to populate `artistId`
3. ✓ Check test scripts are executing (view "Test Results" tab)
4. ✓ Look for console logs showing variable storage
5. ✓ Manually verify environment variables (click eye icon)

**Correct Workflow:**
```
1. Select "Feature.fm Production" environment
2. Run "List Artists" → stores {{artistId}}
3. Run "Get Artist" → uses {{artistId}}
4. Run "Create SmartLink" → uses {{artistId}}
```

**Manual Debugging:**
```javascript
// Check if variable is set
console.log('artistId:', pm.environment.get('artistId'));

// Manually set variable
pm.environment.set('artistId', 'artist_123abc');
```

---

#### Issue: Rate Limiting

**Symptom:**
```json
{
  "status": 1,
  "message": "Too many requests"
}
```

**Troubleshooting Steps:**
1. ✓ Reduce request frequency
2. ✓ Implement delays between requests
3. ✓ Use Collection Runner with delays
4. ✓ Avoid rapid repeated requests in short time

**Postman Collection Runner Settings:**
- Set delay between requests: 500ms - 1000ms
- Limit iterations for testing
- Monitor console for rate limit warnings

---

### Debug Mode

Enable detailed logging for troubleshooting:

**Pre-Request Script:**
```javascript
// Enable debug logging
pm.environment.set('debug', 'true');

// Log request details
console.log('--- REQUEST DEBUG ---');
console.log('Method:', pm.request.method);
console.log('URL:', pm.request.url.toString());
console.log('Headers:', pm.request.headers);
console.log('Body:', pm.request.body);
```

**Test Script:**
```javascript
// Log response details
if (pm.environment.get('debug') === 'true') {
    console.log('--- RESPONSE DEBUG ---');
    console.log('Status:', pm.response.code);
    console.log('Response Time:', pm.response.responseTime + 'ms');
    console.log('Body:', pm.response.text());
}
```

---

### Getting Help

**Resources:**
- **Official Documentation**: [https://developers.feature.fm](https://developers.feature.fm)
- **Support Email**: Contact Feature.fm support team
- **API Status**: Check Feature.fm status page for outages
- **Community**: Feature.fm developer community forums

**Before Contacting Support:**
1. ✓ Check this troubleshooting section
2. ✓ Review error message carefully
3. ✓ Test with Postman collection
4. ✓ Verify API key is active
5. ✓ Check Feature.fm status page
6. ✓ Collect request/response details for support ticket

**Information to Include in Support Request:**
- Request method and endpoint
- Full request body (remove sensitive data)
- Complete error message
- API key ID (not the full key)
- Timestamp of issue
- Steps to reproduce

---

## Postman Collection

### Collection Structure

```
Feature.fm Marketing API/
│
├── Authentication/
│   └── Test API Key
│
├── Artists/
│   ├── List Artists
│   ├── Search Artists
│   ├── Get Artist
│   ├── Create Artist
│   └── Update Artist
│
├── SmartLinks/
│   ├── Get SmartLink
│   ├── Get SmartLink by ShortId
│   ├── Create SmartLink
│   └── Create Pre-Save SmartLink
│
└── Action Pages/
    ├── List Action Pages
    ├── Search Action Pages
    └── Get Action Page
```

### Collection Features

#### Auto-Population
The collection automatically stores IDs from responses for use in subsequent requests:

- **List Artists** → stores `{{artistId}}` and `{{artistName}}`
- **Create Artist** → stores `{{newArtistId}}`
- **Create SmartLink** → stores `{{smartlinkId}}`

#### Global Scripts

**Pre-Request (all requests):**
```javascript
// Log request for debugging
console.log(`Request: ${pm.request.method} ${pm.request.url.getPath()}`);
```

**Test (all requests):**
```javascript
// Validate no server errors
pm.test('No server errors (5xx)', function () {
    pm.expect(pm.response.code).to.be.below(500);
});

// Log response time
console.log(`Response time: ${pm.response.responseTime}ms`);

// Handle authentication errors
if (pm.response.code === 401) {
    console.error('Authentication failed - check API key');
}
```

#### Request-Specific Tests

**Example: List Artists**
```javascript
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});

pm.test('Response contains artists array', function () {
    const response = pm.response.json();
    pm.expect(response.data).to.be.an('array');
});

// Store first artist ID
if (pm.response.code === 200) {
    const response = pm.response.json();
    if (response.data && response.data.length > 0) {
        pm.environment.set('artistId', response.data[0].id);
        pm.environment.set('artistName', response.data[0].artistName);
        console.log('Stored artist:', response.data[0].artistName);
    }
}
```

### Environment Setup

Create a Postman environment with these variables:

```json
{
  "name": "Feature.fm Production",
  "values": [
    {
      "key": "baseUrl",
      "value": "https://api.feature.fm",
      "type": "default"
    },
    {
      "key": "apiKey",
      "value": "your_api_key_here",
      "type": "secret"
    },
    {
      "key": "artistId",
      "value": "",
      "type": "default"
    },
    {
      "key": "newArtistId",
      "value": "",
      "type": "default"
    },
    {
      "key": "smartlinkId",
      "value": "",
      "type": "default"
    },
    {
      "key": "searchTerm",
      "value": "test",
      "type": "default"
    }
  ]
}
```

### Running the Collection

#### Individual Requests
1. Select environment
2. Navigate to desired request
3. Click **Send**
4. Review response and test results

#### Collection Runner
1. Click **Run** on collection
2. Select environment
3. Configure options:
   - Iterations: 1 (for standard testing)
   - Delay: 500ms (to avoid rate limits)
   - Save responses: Enable for debugging
4. Click **Run Feature.fm Marketing API**

#### Newman (CLI)
```bash
# Install Newman
npm install -g newman

# Run collection
newman run Feature.fm_Marketing_API.postman_collection.json \
  --environment Feature_fm_Production.postman_environment.json \
  --reporters cli,json \
  --delay-request 500

# Run with JSON output
newman run Feature.fm_Marketing_API.postman_collection.json \
  -e Feature_fm_Production.postman_environment.json \
  -r json \
  --reporter-json-export results.json
```

### Collection Variables

| Variable | Description | Auto-Populated | Example Value |
|----------|-------------|----------------|---------------|
| `baseUrl` | API base URL | No (preset) | `https://api.feature.fm` |
| `apiKey` | Your API key | No (user sets) | `your_key_here` |
| `artistId` | Artist ID for testing | Yes (List Artists) | `artist_123abc` |
| `newArtistId` | Newly created artist ID | Yes (Create Artist) | `artist_789xyz` |
| `smartlinkId` | SmartLink ID | Yes (Create SmartLink) | `smartlink_456def` |
| `searchTerm` | Default search term | No (preset) | `test` |

---

## Additional Resources

### Official Documentation
- **Developer Docs**: [https://developers.feature.fm](https://developers.feature.fm)
- **Dashboard**: [https://app.feature.fm](https://app.feature.fm)
- **Best Practices**: [https://developers.feature.fm/#best-practices-to-consider](https://developers.feature.fm/#best-practices-to-consider)

### Related Files
- **Postman Collection**: [Feature.fm_Marketing_API.postman_collection.json](Feature.fm_Marketing_API.postman_collection.json)
- **README**: [postman_collections/README.md](postman_collections/README.md)
- **Python Tests**: [test_sandbox.py](../test_sandbox.py)

### API Capabilities Summary

| Feature | Endpoint | Create | Read | Update | Delete |
|---------|----------|--------|------|--------|--------|
| Artists | `/manage/v1/artist(s)` | ✅ | ✅ | ✅ | ❌ |
| SmartLinks | `/manage/v1/smartlink` | ✅ | ✅ | ❌ | ❌ |
| Pre-Save | `/manage/v1/smartlink/pre-save` | ✅ | ✅ | ❌ | ❌ |
| Future Release | `/manage/v1/smartlink/future-release` | ✅ | ✅ | ❌ | ❌ |
| Action Pages | `/manage/v1/actionpage(s)` | ❌* | ✅ | ❌ | ❌ |

*Action pages may be created through Feature.fm dashboard

---

## Appendix

### Sample Test Scenarios

#### Scenario 1: Complete Artist & SmartLink Setup

```javascript
// 1. List existing artists
GET /manage/v1/artists
// → Stores {{artistId}}

// 2. Get artist details
GET /manage/v1/artist/{{artistId}}
// → Verify artist information

// 3. Create new SmartLink
POST /manage/v1/smartlink
{
  "artistId": "{{artistId}}",
  "shortId": "new-single-{{$timestamp}}",
  "domain": "https://ffm.to",
  "title": "Check Out My New Single",
  "stores": [...]
}
// → Stores {{smartlinkId}}

// 4. Get SmartLink
GET /manage/v1/smartlink/{{smartlinkId}}
// → Verify SmartLink created correctly
```

#### Scenario 2: Pre-Save Campaign Launch

```javascript
// 1. Create test artist
POST /manage/v1/artist
{
  "artistName": "Test Artist {{$timestamp}}",
  "type": "artist",
  "countryCode": "US"
}
// → Stores {{newArtistId}}

// 2. Create pre-save campaign
POST /manage/v1/smartlink/pre-save
{
  "artistId": "{{newArtistId}}",
  "shortId": "presave-{{$timestamp}}",
  "domain": "https://ffm.to",
  "title": "Pre-Save New Album",
  "releaseDate": "2025-12-31",
  "timezone": "America/New_York",
  "stores": [...],
  "preSaveFollow": [...]
}
// → Campaign ready for testing
```

---

### Field Reference

#### Artist Object Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Auto | Unique identifier |
| `artistName` | string | Yes | Artist/band name |
| `type` | string | Yes | Usually "artist" |
| `countryCode` | string | Yes | ISO 2-letter code |
| `shortBio` | string | No | Artist biography |
| `artistImage` | string | No | Profile image URL |
| `backgroundImage` | string | No | Header/cover image URL |
| `tags` | array | No | Genre/category tags |
| `createdAt` | string | Auto | ISO timestamp |
| `updatedAt` | string | Auto | ISO timestamp |

#### SmartLink Object Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Auto | Unique identifier |
| `artistId` | string | Yes | Associated artist |
| `shortId` | string | Yes | URL slug |
| `domain` | string | Yes | Full domain URL |
| `url` | string | Auto | Complete SmartLink URL |
| `title` | string | Yes | Link title |
| `image` | string | No | Cover art URL |
| `description` | string | No | Link description |
| `stores` | array | Yes | Music platform links |
| `releaseDate` | string | Pre-save only | YYYY-MM-DD format |
| `timezone` | string | Pre-save only | Timezone identifier |
| `preSaveFollow` | array | Pre-save only | Artists to follow |
| `createdAt` | string | Auto | ISO timestamp |

#### Store Object Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `storeId` | string | Yes | Platform identifier |
| `url` | string | Yes | Platform URL |

---

### Country Codes Reference

Common ISO 2-letter country codes:

| Code | Country |
|------|---------|
| `US` | United States |
| `GB` | United Kingdom |
| `CA` | Canada |
| `AU` | Australia |
| `DE` | Germany |
| `FR` | France |
| `ES` | Spain |
| `IT` | Italy |
| `JP` | Japan |
| `BR` | Brazil |
| `MX` | Mexico |

---

### Timezone Reference

Common timezone identifiers for `releaseDate`:

| Timezone | Description |
|----------|-------------|
| `America/New_York` | Eastern Time (US) |
| `America/Los_Angeles` | Pacific Time (US) |
| `America/Chicago` | Central Time (US) |
| `Europe/London` | GMT/BST |
| `Europe/Paris` | Central European Time |
| `Asia/Tokyo` | Japan Standard Time |
| `Australia/Sydney` | Australian Eastern Time |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-10-10 | Complete documentation rewrite aligned with Postman collection |
| 1.0.0 | 2024-XX-XX | Initial documentation |

---

**Last Updated**: October 10, 2025
**Documentation Version**: 2.0.0
**Collection Version**: 2.0.0
**API Version**: v1

---

*This documentation is specifically aligned with the Feature.fm Marketing API Postman collection. For additional API capabilities beyond the Marketing API (Publisher API, Conversion API), refer to the official Feature.fm developer documentation.*
