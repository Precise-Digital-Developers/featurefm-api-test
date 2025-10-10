# Feature.fm Postman Collections

Postman collections for testing Feature.fm APIs interactively.

## Available Collections

### 1. Marketing API Collection

**File:** `Feature.fm_Marketing_API.postman_collection.json`

**API Type:** Music Marketing & Distribution
**Base URL:** `https://api.feature.fm`
**Authentication:** API Key (`x-api-key` header)

**Covers:**

- Authentication testing
- Artist management (List, Search, Get, Create, Update)
- SmartLink operations (Get, Create, Pre-Save)
- Action Pages (List, Search, Get)

**Endpoints:** 15+ requests organized by category

### 2. Sandbox/Precise API Collection

**File:** `Feature_FM_Sandbox_Precise_API.postman_collection.json`

**API Type:** Feature Management & Targeting
**Base URL:** `https://api.sandbox-precise.digital`
**Authentication:** JWT (Bearer token)

**Covers:**

- JWT authentication (Get Token, Refresh Token)
- Feature flag management (CRUD operations, Toggle)
- Audience targeting and segmentation
- Analytics and usage tracking
- Webhook management
- Health monitoring

**Endpoints:** 20+ requests organized by category

## Quick Start

### Marketing API Setup

#### 1. Import Collection

1. Open Postman
2. Click **Import** button
3. Select `Feature.fm_Marketing_API.postman_collection.json`
4. Collection will appear in your sidebar

#### 2. Configure Variables

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
  "name": "Feature.fm Production",
  "values": [
    {
      "key": "baseUrl",
      "value": "https://api.feature.fm",
      "enabled": true
    },
    {
      "key": "apiKey",
      "value": "your_api_key_here",
      "enabled": true
    }
  ]
}
```

#### 3. Run Requests

**Recommended order:**

1. **Authentication** → Test API Key
2. **Artists** → List Artists (populates `artistId`)
3. **Artists** → Get Artist
4. **SmartLinks** → Create SmartLink (requires `artistId`)

---

### Sandbox/Precise API Setup

#### 1. Import Collection

1. Open Postman
2. Click **Import** button
3. Select `Feature_FM_Sandbox_Precise_API.postman_collection.json`
4. Collection will appear in your sidebar

#### 2. Configure Variables (Already Set!)

The sandbox collection comes pre-configured with credentials from your email:

```json
{
  "baseUrl": "https://api.sandbox-precise.digital",
  "apiKey": "3890d422-882b-486d-9de6-c106d9951094",
  "secretKey": "mf1x4y13dgnqmcm3v9x7t9fucg7nozil",
  "issuer": "sandbox-precise.digital"
}
```

**Note:** `accessToken` and other IDs are auto-populated after authentication.

#### 3. Run Requests

**Recommended order:**

1. **Authentication** → Get Access Token (stores JWT automatically)
2. **Features** → List Features (populates `featureId`)
3. **Features** → Create Feature
4. **Audiences** → Create Audience
5. **Analytics** → Feature Usage Analytics

## Request Categories

### Marketing API Categories

#### Authentication

- **Test API Key** - Verifies API authentication by listing artists

#### Artists

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

#### Action Pages

- **List Action Pages** - Get all action pages
- **Search Action Pages** - Search action pages
- **Get Action Page** - Get specific action page

---

### Sandbox/Precise API Categories

#### Authentication

- **Get Access Token** - Obtain JWT using API key and secret
- **Refresh Token** - Refresh JWT before expiration

#### Features

- **List Features** - Get all features with pagination
- **Get Feature** - Get specific feature details
- **Create Feature** - Create new feature flag
- **Update Feature** - Update feature configuration
- **Toggle Feature** - Quick enable/disable
- **Delete Feature** - Remove feature

#### Audiences

- **List Audiences** - Get all audience segments
- **Get Audience** - Get audience details
- **Create Audience** - Create targeting rules
- **Update Audience** - Modify audience rules
- **Delete Audience** - Remove audience

#### Analytics

- **Feature Usage Analytics** - Get usage metrics for features
- **Export Analytics** - Export data as CSV/JSON

#### Webhooks

- **List Webhooks** - Get all registered webhooks
- **Register Webhook** - Create new webhook
- **Get Webhook** - Get webhook details
- **Update Webhook** - Modify webhook configuration
- **Delete Webhook** - Remove webhook

#### Health Check

- **Health Check** - API status (no auth required)

## Environment Setup

### Marketing API Environment

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

**⚠️ Warning:** Be careful with write operations (Create, Update, Delete requests) in production.

### Sandbox/Precise API Environment

```json
{
  "name": "Feature FM Sandbox",
  "values": [
    {
      "key": "baseUrl",
      "value": "https://api.sandbox-precise.digital",
      "enabled": true
    },
    {
      "key": "apiKey",
      "value": "3890d422-882b-486d-9de6-c106d9951094",
      "enabled": true
    },
    {
      "key": "secretKey",
      "value": "mf1x4y13dgnqmcm3v9x7t9fucg7nozil",
      "enabled": true
    },
    {
      "key": "issuer",
      "value": "sandbox-precise.digital",
      "enabled": true
    },
    {
      "key": "accessToken",
      "value": "",
      "enabled": true
    }
  ]
}
```

**✅ Safe Testing:** Sandbox environment is isolated and safe for all operations.

## Collection Features

### Auto-Population

Both collections automatically store IDs from responses:

**Marketing API:**
- Create/List Artists → stores `artistId` and `newArtistId`
- Create SmartLink → stores `smartlinkId`

**Sandbox/Precise API:**
- Authentication → stores `accessToken` and `tokenExpirationTime`
- List/Create Features → stores `featureId` and `newFeatureId`
- List/Create Audiences → stores `audienceId` and `newAudienceId`
- Create Webhook → stores `webhookId`

Use variables like `{{artistId}}` or `{{featureId}}` in subsequent requests.

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
