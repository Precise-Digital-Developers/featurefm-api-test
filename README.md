# Feature.fm API Test Suite

A comprehensive test suite for the Feature.fm API with built-in safety features to protect production data.

## Overview

This test suite provides testing for **all three Feature.fm APIs** with two distinct environment modes:

- **Sandbox Mode**: Full CRUD operations for safe testing
- **Production Mode**: READ-ONLY operations to prevent accidental data modification

### Feature.fm APIs Covered

1. **Marketing API** - Manage artists, smartlinks, campaigns, and action pages
2. **Publisher API** - Track user engagement and content consumption
3. **Conversion API** - Monitor conversions and transactions

## Project Structure

```text
FeatureFM_API_Tests/
├── config.py                      # Environment configuration & safety controls
├── base_test.py                   # Base test class with common functionality
├── test_sandbox.py                # Sandbox tests (Marketing API)
├── test_production.py             # Production tests (READ-ONLY)
├── test_all_apis.py               # Complete test suite (all 3 APIs)
├── featurefm_api_tests.py         # Legacy test file (deprecated)
├── app.py                         # Flask dashboard (optional)
├── postman_collections/           # Postman collections for API testing
│   ├── Feature.fm_Marketing_API.postman_collection.json
│   └── README.md                  # Postman usage guide
├── templates/
│   └── dashboard.html             # Web dashboard UI
├── .env                           # Your credentials (NOT in git)
├── .env.example                   # Template for credentials
├── README.md                      # This file
├── REORGANIZATION_SUMMARY.md      # Change log and migration guide
└── requirements.txt               # Python dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
# Sandbox (safe for testing)
FEATUREFM_SANDBOX_API_KEY=your_sandbox_key
FEATUREFM_SANDBOX_SECRET_KEY=your_sandbox_secret
FEATUREFM_SANDBOX_ISS=sandbox-precise.digital

# Production (if needed - read-only)
FEATUREFM_PROD_API_KEY=your_prod_key
FEATUREFM_PROD_SECRET_KEY=your_prod_secret
FEATUREFM_PROD_ISS=your_prod_iss
```

### 3. Run Tests

**Marketing API Tests (Recommended for sandbox):**

```bash
python test_sandbox.py
```

**All Three APIs (Comprehensive test):**

```bash
python test_all_apis.py
```

**Production Tests (READ-ONLY - requires confirmation):**

```bash
python test_production.py
```

## Feature.fm APIs

### Marketing API

**Status:** ✅ Available in Sandbox
**Base URL:** `https://api.feature.fm/manage/v1/`
**Purpose:** Manage marketing resources

**Available Operations:**

- Artists: Create, Read, Update, Search
- SmartLinks: Create, Read, Update, Archive
- Pre-Save Campaigns: Create, Update
- Action Pages: Create, Read, Update, Archive
- Analytics: Query campaign performance

**Example:**

```python
from config import FeatureFMConfig, Environment
from test_sandbox import SandboxAPITester

config = FeatureFMConfig(environment=Environment.SANDBOX)
tester = SandboxAPITester(config)
artist_id = tester.test_create_artist()
```

### Publisher API

**Status:** ⚠️ Not Available in Sandbox (requires production/special access)
**Base URL:** `https://api.feature.fm/`
**Purpose:** Track user engagement and content consumption

**Endpoints:**

- Consumer Identification
- Get Featured Song
- Event Tracking: play, skip, like, favorite, follow, download, share

**Use Case:** When embedding Feature.fm content in your platform/app and tracking user interactions

### Conversion API

**Status:** ⚠️ Not Available in Sandbox (requires production/special access)
**Base URL:** `https://api.feature.fm/conversion/`
**Purpose:** Track conversions and transactions

**Endpoints:**

- Initialize tracking session
- Report transactions
- Periodic conversion reports

**Use Case:** E-commerce integrations, tracking revenue from Feature.fm campaigns

## Safety Features

### Production Protection

The test suite has **5 layers of protection** for production:

1. **Environment Separation** - Sandbox and production use separate configurations
2. **Write Protection** - Production mode BLOCKS all write/update/delete operations
3. **Explicit Confirmation** - Production tests require typing "yes" to run
4. **Read-Only Enforcement** - Any write attempt raises `PermissionError`
5. **Audit Trail** - All tests logged with timestamps and results

**Example Safety Check:**

```python
# This will raise PermissionError in production:
config = FeatureFMConfig(environment=Environment.PRODUCTION)
config.require_write_permission()  # Raises error!
```

## Test Categories

### Marketing API Tests (Sandbox - Full Access)

**Read Operations:**

- ✅ List artists
- ✅ Get artist details
- ✅ Search artists
- ✅ List action pages
- ✅ Search action pages
- ✅ Get SmartLink details

**Write Operations:**

- ✅ Create artist
- ✅ Update artist
- ✅ Create SmartLink
- ✅ Create pre-save campaign
- ✅ Create action page
- ✅ Archive/restore resources

**Success Rate:** 87.5% (7/8 tests passing)

### Publisher API Tests

**Read Operations:**

- Identify consumer
- Get featured song
- Track events (play, like, skip, etc.)

**Status:** ⚠️ Not available in sandbox - requires production access

### Conversion API Tests

**Operations:**

- Initialize session
- Report transactions
- Periodic reports

**Status:** ⚠️ Not available in sandbox - requires production access

### Production Tests (Read-Only)

- ✅ List artists
- ✅ Search artists
- ✅ Get artist details
- ✅ List action pages
- ✅ Search action pages
- ✅ Get SmartLink details
- ❌ Create operations (BLOCKED)
- ❌ Update operations (BLOCKED)
- ❌ Delete operations (BLOCKED)

## Advanced Usage

### Custom Test Configuration

```python
from config import FeatureFMConfig, Environment
from test_sandbox import SandboxAPITester

# Create sandbox config
config = FeatureFMConfig(environment=Environment.SANDBOX)

# Initialize tester
tester = SandboxAPITester(config, verbose=True)

# Run specific test
artist_id = tester.test_create_artist()
smartlink_id = tester.test_create_smartlink(artist_id)
```

### Accessing Endpoint Catalog

```python
from config import get_all_read_endpoints, get_all_write_endpoints

# Get all safe read-only endpoints
read_endpoints = get_all_read_endpoints()

# Get all write endpoints (sandbox only)
write_endpoints = get_all_write_endpoints()
```

### Testing All Three APIs

```python
from config import FeatureFMConfig, Environment
from test_all_apis import CompleteAPITester

config = FeatureFMConfig(environment=Environment.SANDBOX)
tester = CompleteAPITester(config)
tester.run_all_tests()
```

## Test Results

All test runs generate JSON result files:

- Sandbox (Marketing): `sandbox_test_results_YYYYMMDD_HHMMSS.json`
- Production: `production_test_results_YYYYMMDD_HHMMSS.json`
- Complete (All APIs): `complete_api_test_results_YYYYMMDD_HHMMSS.json`

**Example result structure:**

```json
{
  "timestamp": "2025-10-10T08:30:00",
  "environment": "sandbox",
  "summary": {
    "total": 10,
    "passed": 8,
    "failed": 1,
    "warnings": 1
  },
  "tests": { }
}
```

## Postman Collections

Pre-configured Postman collections are available in `postman_collections/`:

### Marketing API Collection

Import `postman_collections/Feature.fm_Marketing_API.postman_collection.json` into Postman for interactive API testing.

**Includes:**

- 15+ pre-configured requests
- Auto-population of IDs from responses
- Test scripts for validation
- Organized by category (Artists, SmartLinks, Action Pages)

**Quick setup:**

1. Import collection into Postman
2. Set `apiKey` variable to your API key
3. Run "List Artists" to populate IDs
4. Test other endpoints

See [Postman Collections README](postman_collections/README.md) for detailed instructions.

## Web Dashboard (Optional)

Run the Flask dashboard for a visual interface:

```bash
python app.py
```

Then open: <http://localhost:5000>

## Environment Notes

### Sandbox Environment

- **Purpose:** Safe testing environment
- **Data:** Isolated from production
- **APIs Available:** Marketing API only
- **Operations:** All CRUD operations allowed
- **Safety:** Changes don't affect live data

### Production Environment

- **Purpose:** Monitoring and read-only checks
- **Data:** LIVE production data
- **APIs Available:** Marketing, Publisher, Conversion (with proper credentials)
- **Operations:** READ-ONLY (enforced)
- **Safety:** Multiple safeguards prevent writes

## API Endpoint Patterns

Feature.fm uses specific endpoint patterns:

### List Operations (Plural)

- `GET /manage/v1/artists`
- `GET /manage/v1/actionpages`
- `GET /manage/v1/smartlinks` (endpoint may not exist, but pattern is consistent)

### Individual Operations (Singular)

- `GET /manage/v1/artist/{id}`
- `POST /manage/v1/artist`
- `PUT /manage/v1/artist/{id}`
- `POST /manage/v1/smartlink`
- `POST /manage/v1/actionpage`

### Field Naming Convention

Feature.fm uses **camelCase** for all field names:

**Correct:**

```python
{
  "artistName": "Test Artist",
  "countryCode": "US",
  "releaseDate": "2025-12-31",
  "storeId": "spotify"
}
```

**Wrong:**

```python
{
  "artist_name": "Test Artist",  # Wrong - don't use snake_case
  "country_code": "US",
  "release_date": "2025-12-31",
  "store_id": "spotify"
}
```

## Troubleshooting

### Authentication Errors (401)

Check your `.env` file has the correct credentials:

```bash
FEATUREFM_SANDBOX_API_KEY=correct_key_here
FEATUREFM_SANDBOX_SECRET_KEY=correct_secret_here
```

### Endpoint Not Found (404)

Verify you're using the correct endpoint pattern:

- ✅ `/manage/v1/artist` (singular for POST/PUT)
- ✅ `/manage/v1/artists` (plural for GET list)

### Validation Errors

Check your request data uses camelCase:

```python
# Correct:
{"artistName": "Test", "countryCode": "US"}

# Wrong:
{"artist_name": "Test", "country_code": "US"}
```

### API Not Available

Some APIs are only available in production:

- Marketing API: ✅ Available in sandbox
- Publisher API: ⚠️ Production/special access only
- Conversion API: ⚠️ Production/special access only

## API Documentation

Official Feature.fm API Documentation:
<https://developers.feature.fm/>

## Contributing

When adding new tests:

1. Add endpoint info to `config.py` ENDPOINTS catalog
2. Implement read operations in `BaseAPITester`
3. Implement write operations ONLY in `SandboxAPITester`
4. Never add write operations to `ProductionAPITester`

## License

This project is for internal use by Precise Digital for testing Feature.fm API integration.

## Environment Variables Reference

| Variable | Required | Environment | Description |
|----------|----------|-------------|-------------|
| `FEATUREFM_SANDBOX_API_KEY` | Yes | Sandbox | Your sandbox API key |
| `FEATUREFM_SANDBOX_SECRET_KEY` | Yes | Sandbox | Your sandbox secret |
| `FEATUREFM_SANDBOX_ISS` | Yes | Sandbox | Sandbox issuer (usually `sandbox-precise.digital`) |
| `FEATUREFM_PROD_API_KEY` | Optional | Production | Production API key |
| `FEATUREFM_PROD_SECRET_KEY` | Optional | Production | Production secret |
| `FEATUREFM_PROD_ISS` | Optional | Production | Production issuer |

## Examples

### Running Sandbox Tests

```bash
$ python test_sandbox.py

╔══════════════════════════════════════════════════════════════╗
║        Feature.fm API Sandbox Test Suite                    ║
║                                                              ║
║  Environment: SANDBOX                                        ║
║  Write Operations: ENABLED                                   ║
║  Safety: All operations are isolated in sandbox              ║
╚══════════════════════════════════════════════════════════════╝

━━━ Authentication Tests ━━━
✓ API key authentication successful
✓ JWT authentication successful

━━━ Write Operations - Create Resources ━━━
✓ Artist created: Sandbox Test Artist 20251010_082759

Test Summary - Sandbox Environment
Total Tests: 8
✓ Passed: 7
✗ Failed: 0
⚠ Warnings: 1
Success Rate: 87.5%
```

### Running Complete API Tests

```bash
$ python test_all_apis.py

Select environment (1=Sandbox, 2=Production): 1

╔══════════════════════════════════════════════════════════════╗
║     Feature.fm Complete API Test Suite                      ║
║                                                              ║
║  Testing all three APIs:                                    ║
║  • Marketing API (Artists, SmartLinks, Campaigns)           ║
║  • Publisher API (Events, Tracking)                         ║
║  • Conversion API (Sessions, Transactions)                  ║
╚══════════════════════════════════════════════════════════════╝

API Availability:
  ✅ Marketing Api: Available
  ⚠️ Publisher Api: Not Available
  ⚠️ Conversion Api: Not Available
```

### Running Production Tests

```bash
$ python test_production.py

╔══════════════════════════════════════════════════════════════╗
║     Feature.fm API Production Test Suite (READ-ONLY)        ║
║                                                              ║
║  ⚠️  PRODUCTION ENVIRONMENT - EXTREME CAUTION  ⚠️            ║
║                                                              ║
║  Write Operations: DISABLED                                  ║
║  Only read operations will be executed                       ║
╚══════════════════════════════════════════════════════════════╝

Are you sure you want to run tests against PRODUCTION? (type 'yes' to confirm): yes

━━━ Authentication Tests ━━━
✓ API key authentication successful

━━━ Read Operations - Artists ━━━
✓ Found 145 production artists
✓ Found 3 matching artists
```

## Security Best Practices

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Use sandbox for development** - Test all features safely
3. **Limit production access** - Only use when necessary
4. **Review test output** - Check for sensitive data before sharing logs
5. **Rotate credentials** - Update keys periodically

## Additional Resources

- [Reorganization Summary](REORGANIZATION_SUMMARY.md) - Details about v2.0 changes
- [Feature.fm Developer Portal](https://developers.feature.fm/)
- [Best Practices Guide](https://developers.feature.fm/#best-practices-to-consider)

---

**Last Updated:** October 10, 2025
**Version:** 2.0
**Maintained by:** Precise Digital
