# Feature.fm API Test Suite - Project Overview

## Executive Summary

This project provides comprehensive testing infrastructure for **two separate Feature.fm API products**:

1. **Marketing API** - Music marketing and distribution platform
2. **Sandbox/Precise API** - Feature management and targeting platform

## Understanding the Two APIs

### API 1: Marketing API (Music Industry)

**Purpose:** Music marketing, artist management, and SmartLink distribution

**Base URL:** `https://api.feature.fm`

**Authentication:** API Key (simple `x-api-key` header)

**Use Cases:**
- Managing music artist profiles
- Creating SmartLinks for music distribution
- Running pre-save campaigns for upcoming releases
- Tracking campaign performance

**Key Entities:**
- Artists (musicians, bands, labels)
- SmartLinks (intelligent music distribution links)
- Action Pages (landing pages for campaigns)
- Pre-Save Campaigns

---

### API 2: Sandbox/Precise API (Feature Management)

**Purpose:** Feature flags, audience targeting, and A/B testing

**Base URL:** `https://api.sandbox-precise.digital`

**Authentication:** JWT (API Key + Secret Key → Bearer token)

**Use Cases:**
- Managing feature flags for applications
- Creating audience segments for targeted rollouts
- Tracking feature usage analytics
- Webhook integration for real-time events

**Key Entities:**
- Features (feature flags/toggles)
- Audiences (user segments)
- Analytics (usage metrics)
- Webhooks (event notifications)

---

## Project Structure

```
FeatureFM_API_Tests/
│
├── docs/
│   ├── Feature_FM_Marketing_API_Documentation.md      # Marketing API docs
│   ├── Feature_FM_Sandbox_API_Documentation.md        # Sandbox/Precise API docs (original knowledge repo)
│   └── PROJECT_OVERVIEW.md                             # This file
│
├── postman_collections/
│   ├── Feature.fm_Marketing_API.postman_collection.json           # Music marketing tests
│   ├── Feature_FM_Sandbox_Precise_API.postman_collection.json     # Feature management tests
│   └── README.md                                                   # Postman usage guide
│
├── Python Test Files/
│   ├── config.py                  # Environment configuration
│   ├── base_test.py              # Base test class
│   ├── test_sandbox.py           # Sandbox tests (Marketing API)
│   ├── test_production.py        # Production tests (READ-ONLY)
│   └── test_all_apis.py          # Complete test suite
│
├── .env                          # Credentials (NOT in git)
├── .env.example                  # Template for credentials
├── README.md                     # Main project documentation
└── requirements.txt              # Python dependencies
```

## API Comparison Matrix

| Feature | Marketing API | Sandbox/Precise API |
|---------|---------------|---------------------|
| **Industry** | Music | Software Development |
| **Primary Use** | Artist promotion, music distribution | Feature flags, A/B testing |
| **Base URL** | `api.feature.fm` | `api.sandbox-precise.digital` |
| **Auth Method** | API Key (header) | JWT (Bearer token) |
| **Auth Complexity** | Simple | Moderate (token refresh) |
| **Main Entities** | Artists, SmartLinks, Campaigns | Features, Audiences, Analytics |
| **Write Operations** | ✅ Available | ✅ Available (Sandbox only) |
| **Sandbox Environment** | ❌ No separate sandbox | ✅ Dedicated sandbox |
| **Production Access** | ✅ Yes (with care) | Unknown (sandbox credentials provided) |

## Testing Infrastructure

### Postman Collections

#### Marketing API Collection
- **File:** `Feature.fm_Marketing_API.postman_collection.json`
- **Endpoints:** 15+ organized requests
- **Auto-Variables:** `artistId`, `smartlinkId`
- **Authentication:** Pre-configured API key header
- **Best For:** Interactive testing, manual verification

#### Sandbox/Precise API Collection
- **File:** `Feature_FM_Sandbox_Precise_API.postman_collection.json`
- **Endpoints:** 20+ organized requests
- **Auto-Variables:** `accessToken`, `featureId`, `audienceId`
- **Authentication:** JWT with auto-refresh warnings
- **Best For:** Feature management testing, webhook testing

### Python Test Suites

#### test_sandbox.py
- **API:** Marketing API
- **Environment:** Sandbox/Testing
- **Operations:** Full CRUD operations
- **Safety:** Isolated environment

#### test_production.py
- **API:** Marketing API
- **Environment:** Production
- **Operations:** READ-ONLY (enforced)
- **Safety:** 5 layers of protection

#### test_all_apis.py
- **APIs:** Marketing, Publisher, Conversion
- **Scope:** Comprehensive testing
- **Note:** Some APIs unavailable in sandbox

## Credentials Management

### Marketing API Credentials

**Location:** `.env` file

```bash
# Marketing API (Production)
FEATUREFM_PROD_API_KEY=your_marketing_api_key_here
```

**Obtain From:** Feature.fm dashboard

---

### Sandbox/Precise API Credentials

**Location:** `.env` file or Postman collection variables

```bash
# Sandbox/Precise API
FEATUREFM_SANDBOX_API_KEY=3890d422-882b-486d-9de6-c106d9951094
FEATUREFM_SANDBOX_SECRET_KEY=mf1x4y13dgnqmcm3v9x7t9fucg7nozil
FEATUREFM_SANDBOX_ISS=sandbox-precise.digital
```

**Provided By:** Michael Sherman (VP of Business Development) via email

**Credentials Status:** ✅ Pre-configured in Postman collection

---

## Quick Start Guides

### Testing Marketing API (Music)

**With Postman:**
1. Import `Feature.fm_Marketing_API.postman_collection.json`
2. Set `apiKey` variable in collection or environment
3. Run "Test API Key" to verify
4. Run "List Artists" to populate IDs
5. Test other endpoints (Create SmartLink, etc.)

**With Python:**
```bash
# Setup
cp .env.example .env
# Add your Marketing API key to .env

# Run tests
python test_sandbox.py
```

---

### Testing Sandbox/Precise API (Feature Flags)

**With Postman:**
1. Import `Feature_FM_Sandbox_Precise_API.postman_collection.json`
2. Credentials are already set! (from email)
3. Run "Get Access Token" first
4. Run "List Features" to populate IDs
5. Test CRUD operations, audiences, analytics

**With Python:**
```bash
# Setup
cp .env.example .env
# Add Sandbox API credentials to .env

# Run tests (if Python tests are created for Sandbox API)
python test_sandbox_precise.py  # (To be created)
```

---

## Documentation Resources

### Marketing API (Music)
- **Project Docs:** [docs/Feature_FM_Marketing_API_Documentation.md](Feature_FM_Marketing_API_Documentation.md)
- **Official Docs:** [https://developers.feature.fm](https://developers.feature.fm)
- **Postman Guide:** [postman_collections/README.md](../postman_collections/README.md)

### Sandbox/Precise API (Feature Flags)
- **Project Docs:** [docs/Feature_FM_Sandbox_API_Documentation.md](Feature_FM_Sandbox_API_Documentation.md) *(from knowledge repo)*
- **Postman Guide:** [postman_collections/README.md](../postman_collections/README.md)
- **Email Reference:** RE: Feature.fm General Check In (Michael Sherman, 2025-10-03)

---

## Common Workflows

### Workflow 1: Create Music SmartLink (Marketing API)

```
1. List Artists → Get artistId
2. Create SmartLink → Provide:
   - artistId
   - shortId (URL slug)
   - title
   - music store URLs (Spotify, Apple, etc.)
3. Verify SmartLink created
4. Test public URL: https://ffm.to/{shortId}
```

### Workflow 2: Create Pre-Save Campaign (Marketing API)

```
1. Get Artist ID
2. Create Pre-Save SmartLink → Provide:
   - artistId
   - releaseDate (future date)
   - timezone
   - Album URL (Spotify)
   - Artist follow URLs
3. Campaign goes live
4. Users can pre-save before release
```

### Workflow 3: Gradual Feature Rollout (Sandbox/Precise API)

```
1. Authenticate → Get JWT
2. Create Feature → Set:
   - enabled: false
   - rolloutPercentage: 0
3. Create Audience → Define targeting rules
4. Update Feature → Associate audience
5. Toggle Feature → enabled: true
6. Update rolloutPercentage: 10, 25, 50, 100
7. Monitor Analytics → Track usage
```

### Workflow 4: A/B Testing (Sandbox/Precise API)

```
1. Create Feature A (variant A configuration)
2. Create Feature B (variant B configuration)
3. Create Audience "Group A" (50% split)
4. Create Audience "Group B" (50% split)
5. Enable both features
6. Track analytics for both
7. Compare conversion metrics
8. Winner rollout to 100%
```

---

## Environment Safety

### Marketing API
- **Production:** ⚠️ Live data - be careful with writes
- **No Sandbox:** Test carefully or use test artist profiles

### Sandbox/Precise API
- **Sandbox:** ✅ Fully isolated - safe for all operations
- **Production:** Unknown - only sandbox credentials provided

---

## Testing Best Practices

### For Marketing API

1. **Use Test Data:** Create artists with "Test_" prefix
2. **Clean Up:** Delete test SmartLinks and artists after testing
3. **Verify URLs:** Test all music store URLs before creating SmartLinks
4. **Production Caution:** Never delete real artist data

### For Sandbox/Precise API

1. **Token Management:** Refresh tokens before expiration (monitor warnings)
2. **Feature Naming:** Use clear prefixes (`test_`, `experiment_`, `kill_`)
3. **Gradual Rollouts:** Always start at 0%, increase incrementally
4. **Webhook Testing:** Use webhook testing tools (webhook.site, ngrok)
5. **Analytics Lag:** Allow 5-10 minutes for analytics data processing

---

## Integration Scenarios

### Scenario 1: Music Artist Using Both APIs

**Marketing API:** Manage artist profile, create SmartLinks
**Sandbox API:** Feature flag for "New Album Pre-Save Button" on artist website

```
1. Create artist via Marketing API
2. Create SmartLink for upcoming album
3. Create feature flag "show_presave_button"
4. Gradual rollout: 10% → 50% → 100%
5. Monitor conversion analytics
```

### Scenario 2: Music Platform Using Sandbox API

**Use Case:** Streaming app implementing new playlist feature

```
1. Create feature "new_playlist_ui"
2. Create audience "premium_users"
3. Enable for premium users first
4. Monitor engagement analytics
5. Rollout to free users if successful
```

---

## Troubleshooting

### Marketing API Issues

| Problem | Solution |
|---------|----------|
| 401 Authentication Failed | Check API key in `.env` or Postman variables |
| 404 Endpoint Not Found | Verify singular/plural endpoint pattern |
| 400 Validation Error | Ensure fields use camelCase, not snake_case |
| SmartLink creation fails | Verify music store URLs are valid |

### Sandbox/Precise API Issues

| Problem | Solution |
|---------|----------|
| Token expired | Run "Get Access Token" again |
| 401 Unauthorized | Token may be expired - check expiration warning |
| Feature not appearing | Check status filter, verify creation succeeded |
| Analytics data missing | Allow 5-10 minutes for data processing |

---

## Next Steps

### Immediate Actions
1. ✅ Import both Postman collections
2. ✅ Configure credentials in `.env` file
3. ✅ Test Marketing API with "List Artists"
4. ✅ Test Sandbox API with "Get Access Token"

### Development Tasks
- [ ] Create Python test suite for Sandbox/Precise API
- [ ] Set up automated test runs (CI/CD)
- [ ] Create webhook receiver for testing
- [ ] Build dashboard for analytics visualization

### Documentation Tasks
- [ ] Add example workflows with screenshots
- [ ] Create video tutorials for common operations
- [ ] Document error codes and resolutions
- [ ] Create API changelog tracking

---

## Support & Resources

### Marketing API Support
- **Official Docs:** https://developers.feature.fm
- **Support:** Feature.fm support team
- **Community:** Feature.fm developer forums

### Sandbox/Precise API Support
- **Contact:** Michael Sherman <michaels@feature.fm>
- **Email Reference:** RE: Feature.fm General Check In
- **Documentation:** See knowledge repository docs
- **Slack Channel:** (Available upon request)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-10 | Initial project overview document |

---

**Last Updated:** October 10, 2025
**Project Version:** 2.0
**Maintained by:** Precise Digital
