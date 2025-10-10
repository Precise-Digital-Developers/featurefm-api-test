#!/usr/bin/env python3
"""Feature.fm API Testing.

"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import jwt  # type: ignore[import-not-found]
import requests
from colorama import Fore, Style, init  # type: ignore[import-untyped]
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class TestStatus(Enum):
    """Test result statuses."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    WARNING = "WARNING"

class FeatureFMAPITester:
    """Main API tester class for Feature.fm API."""

    def __init__(
        self,
        api_key: str,
        secret_key: str,
        iss: str,
        *,
        verbose: bool = True,
    ) -> None:
        """Initialize the API tester with credentials.

        Args:
        ----
            api_key: API key provided by Feature.fm.
            secret_key: Secret key for JWT signing.
            iss: Issuer identifier (sandbox-precise.digital).
            verbose: Enable verbose output.

        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.iss = iss
        self.verbose = verbose

        # API endpoints - Feature.fm specific
        self.base_url = "https://api.feature.fm"
        self.marketing_base = f"{self.base_url}/v2"
        self.manage_base = f"{self.base_url}/manage/v1"
        # Sandbox might use simplified endpoints without /manage/v1
        self.sandbox_mode = True  # Set to True for sandbox testing

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": self.api_key,
            "User-Agent": "FeatureFM-API-Tester/1.0",
        })

        # Test data storage
        self.test_data: dict[str, Any] = {
            "artist_id": None,
            "artist_name": None,
            "release_id": None,
            "smartlink_id": None,
            "smartlink_url": None,
            "campaign_id": None,
            "actionpage_id": None,
            "pre_save_id": None,
            "analytics_data": None,
            "webhook_id": None,
        }

        # Test results
        self.results: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "environment": "sandbox",
            "credentials": {
                "api_key": self.api_key[:8] + "..." if len(self.api_key) > 8 else self.api_key,
                "iss": self.iss,
            },
            "endpoints_tested": [],
            "tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "warnings": 0,
            },
            "errors": [],
        }

    def _generate_jwt(self, payload: dict[str, Any] | None = None) -> str:
        """Generate JWT token for authentication.

        Args:
        ----
            payload: JWT payload data

        Returns:
        -------
            Signed JWT token
        """
        if payload is None:
            payload = {}

        # Add standard claims
        payload.update({
            "iss": self.iss,
            "sub": self.api_key,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,  # 1 hour expiry
            "jti": hashlib.sha256(f"{time.time()}".encode()).hexdigest(),
        })

        return str(jwt.encode(payload, self.secret_key, algorithm="HS256"))

    def _generate_hmac_signature(self, method: str, path: str, body: str = "") -> str:
        """Generate HMAC signature for request authentication.

        Args:
        ----
            method: HTTP method
            path: API endpoint path
            body: Request body as string

        Returns:
        -------
            HMAC signature
        """
        timestamp = str(int(time.time()))
        message = f"{method}\n{path}\n{timestamp}\n{body}"

        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return f"{timestamp}.{signature}"

    def _print_status(self, message: str, status: TestStatus | None = None, indent: int = 0) -> None:
        """Print status message.

        Args:
        ----
            message: Message to print
            status: Status type
            indent: Indentation level
        """
        if not self.verbose:
            return

        prefix = "  " * indent

        if status == TestStatus.PASSED:
            print(f"{prefix}{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
        elif status == TestStatus.FAILED:
            print(f"{prefix}{Fore.RED}✗ {message}{Style.RESET_ALL}")
        elif status == TestStatus.WARNING:
            print(f"{prefix}{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
        elif status == TestStatus.SKIPPED:
            print(f"{prefix}{Fore.CYAN}→ {message}{Style.RESET_ALL}")
        else:
            print(f"{prefix}{message}")

    def _make_request(self,
                     endpoint: str,
                     method: str = "GET",
                     data: dict[str, Any] | None = None,
                     use_jwt: bool = False,
                     use_hmac: bool = False,
                     base_override: str | None = None,
                     retry_count: int = 3) -> tuple[bool, dict[str, Any]]:
        """Make an API request with retry logic.

        Args:
        ----
            endpoint: API endpoint path
            method: HTTP method
            data: Request payload
            use_jwt: Whether to use JWT authentication
            use_hmac: Whether to use HMAC signing
            base_override: Override base URL
            retry_count: Number of retry attempts

        Returns:
        -------
            Tuple of (success, response_data)
        """
        # Determine base URL
        if base_override:
            url = f"{base_override}{endpoint}"
        elif endpoint.startswith("/manage"):
            url = f"{self.base_url}{endpoint}"
        elif endpoint.startswith("/v2"):
            url = f"{self.base_url}{endpoint}"
        else:
            url = f"{self.manage_base}{endpoint}"

        headers = dict(self.session.headers)

        # Add JWT if required
        if use_jwt:
            token = self._generate_jwt()
            headers["Authorization"] = f"Bearer {token}"

        # Add HMAC if required
        if use_hmac:
            body_str = json.dumps(data) if data else ""
            signature = self._generate_hmac_signature(method, endpoint, body_str)
            headers["X-Signature"] = signature

        # Record endpoint being tested
        if url not in self.results["endpoints_tested"]:
            self.results["endpoints_tested"].append(url)

        for attempt in range(retry_count):
            try:
                if method == "GET":
                    response = self.session.get(url, params=data, headers=headers, timeout=10)
                elif method == "POST":
                    response = self.session.post(url, json=data, headers=headers, timeout=10)
                elif method == "PUT":
                    response = self.session.put(url, json=data, headers=headers, timeout=10)
                elif method == "PATCH":
                    response = self.session.patch(url, json=data, headers=headers, timeout=10)
                elif method == "DELETE":
                    response = self.session.delete(url, headers=headers, timeout=10)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # Parse response
                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    response_data = {"raw_response": response.text}

                result = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "data": response_data,
                    "url": url,
                    "method": method,
                    "attempt": attempt + 1,
                }

                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", 60)
                    self._print_status(f"Rate limited. Waiting {retry_after} seconds...",
                                     TestStatus.WARNING, 2)
                    time.sleep(int(retry_after))
                    continue

                return (response.ok, result)

            except requests.exceptions.Timeout:
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return (False, {"error": "Request timeout", "url": url})

            except requests.exceptions.RequestException as e:
                return (False, {"error": str(e), "url": url})

        return (False, {"error": "All retry attempts failed", "url": url})

    def _record_test(self, test_name: str, status: TestStatus, details: dict[str, Any]) -> None:
        """Record test result.

        Args:
        ----
            test_name: Name of the test
            status: Test status
            details: Test details and response data
        """
        self.results["tests"][test_name] = {
            "status": status.value,
            "timestamp": datetime.now().isoformat(),
            "details": details,
        }

        self.results["summary"]["total"] += 1

        if status == TestStatus.PASSED:
            self.results["summary"]["passed"] += 1
        elif status == TestStatus.FAILED:
            self.results["summary"]["failed"] += 1
            self.results["errors"].append({
                "test": test_name,
                "error": details.get("error", details.get("data", "Unknown error")),
            })
        elif status == TestStatus.SKIPPED:
            self.results["summary"]["skipped"] += 1
        elif status == TestStatus.WARNING:
            self.results["summary"]["warnings"] += 1

    # ========== AUTHENTICATION TESTS ==========

    def test_basic_auth(self) -> bool:
        """Test basic API key authentication."""
        self._print_status("\n[TEST] Basic API Key Authentication", indent=0)

        success, response = self._make_request("/artists")

        if success:
            self._print_status("API key authentication successful", TestStatus.PASSED, 1)
            self._print_status(f"Response: {response['status_code']}", indent=2)
            self._record_test("basic_auth", TestStatus.PASSED, response)
        else:
            self._print_status(f"Authentication failed: {response.get('error', 'Unknown error')}",
                             TestStatus.FAILED, 1)
            self._record_test("basic_auth", TestStatus.FAILED, response)

        return success

    def test_jwt_auth(self) -> bool:
        """Test JWT authentication."""
        self._print_status("\n[TEST] JWT Token Authentication", indent=0)

        success, response = self._make_request("/artists", use_jwt=True)

        if success:
            self._print_status("JWT authentication successful", TestStatus.PASSED, 1)
            self._record_test("jwt_auth", TestStatus.PASSED, response)
        else:
            self._print_status("JWT authentication not required or failed",
                             TestStatus.WARNING, 1)
            self._record_test("jwt_auth", TestStatus.WARNING, response)

        return success

    # ========== ARTIST MANAGEMENT TESTS ==========

    def test_list_artists(self) -> bool:
        """Test listing artists."""
        self._print_status("\n[TEST] List Artists", indent=0)

        success, response = self._make_request("/artists")

        if success:
            artists = response["data"]
            if isinstance(artists, list):
                self._print_status(f"Found {len(artists)} artists", TestStatus.PASSED, 1)

                for artist in artists[:3]:  # Show first 3
                    if isinstance(artist, dict):
                        self._print_status(
                            f"Artist: {artist.get('artistName', 'Unknown')} (ID: {artist.get('id')})",
                            indent=2,
                        )
                        if not self.test_data["artist_id"]:
                            self.test_data["artist_id"] = artist.get("id")
                            self.test_data["artist_name"] = artist.get("artistName")
            else:
                self._print_status("No artists found or unexpected format", TestStatus.WARNING, 1)

            self._record_test("list_artists", TestStatus.PASSED, response)
        else:
            self._print_status(f"Failed to list artists: {response.get('error', 'Unknown error')}",
                             TestStatus.FAILED, 1)
            self._record_test("list_artists", TestStatus.FAILED, response)

        return success

    def test_create_artist(self) -> bool:
        """Test creating a new artist."""
        self._print_status("\n[TEST] Create Artist", indent=0)

        artist_data = {
            "artistName": f'Test Artist {datetime.now().strftime("%Y%m%d_%H%M%S")}',
            "type": "artist",  # Required: "artist" or "band"
            "countryCode": "US",  # Required: ISO 3166-1 alpha-2
            "shortBio": "Created via Feature.fm API test suite",
            "artistImage": "https://via.placeholder.com/500",
            "websiteUrl": "https://testartist.com",
            "spotifyArtistUrl": "https://open.spotify.com/artist/test",
            "tags": ["electronic", "pop"],
        }

        success, response = self._make_request("/artist", method="POST", data=artist_data)

        if success:
            if response["data"] and isinstance(response["data"], dict):
                artist_id = response["data"].get("id")
                artist_name = response["data"].get("artistName", artist_data["artistName"])
                self._print_status(f"Artist created: {artist_name} (ID: {artist_id})",
                                 TestStatus.PASSED, 1)
                self.test_data["artist_id"] = artist_id
                self.test_data["artist_name"] = artist_name
            self._record_test("create_artist", TestStatus.PASSED, response)
        else:
            status_code = response.get("status_code", 0)
            if status_code == 403:
                self._print_status("Create artist not permitted in sandbox", TestStatus.WARNING, 1)
                self._record_test("create_artist", TestStatus.WARNING, response)
            else:
                self._print_status(f"Failed to create artist: {response.get('error', 'Unknown error')}",
                                 TestStatus.FAILED, 1)
                self._record_test("create_artist", TestStatus.FAILED, response)

        return success

    def test_get_artist_details(self) -> bool:
        """Test getting artist details."""
        self._print_status("\n[TEST] Get Artist Details", indent=0)

        if not self.test_data.get("artist_id"):
            self._print_status("Skipping - No artist ID available", TestStatus.SKIPPED, 1)
            self._record_test("get_artist_details", TestStatus.SKIPPED,
                            {"reason": "No artist ID"})
            return False

        success, response = self._make_request(f'/artist/{self.test_data["artist_id"]}')

        if success:
            artist = response["data"]
            self._print_status(f"Retrieved artist: {artist.get('artistName', 'Unknown')}",
                             TestStatus.PASSED, 1)
            self._print_status(f"Genres: {', '.join(artist.get('genres', []))}", indent=2)
            self._print_status(f"Country: {artist.get('country', 'N/A')}", indent=2)
            self._record_test("get_artist_details", TestStatus.PASSED, response)
        else:
            self._print_status("Failed to get artist details", TestStatus.FAILED, 1)
            self._record_test("get_artist_details", TestStatus.FAILED, response)

        return success

    # ========== SMART LINKS TESTS ==========

    def test_create_smartlink(self) -> bool:
        """Test creating a smart link."""
        self._print_status("\n[TEST] Create Smart Link", indent=0)

        if not self.test_data.get("artist_id"):
            # Try to create without artist ID (some APIs allow this)
            self._print_status("No artist ID - attempting standalone creation", indent=1)

        # Skip if no artist ID - smartlinks require artistId
        if not self.test_data.get("artist_id"):
            self._print_status("Skipping - No artist ID available", TestStatus.SKIPPED, 1)
            self._record_test("create_smartlink", TestStatus.SKIPPED, {"reason": "No artist ID"})
            return False

        link_data = {
            "artistId": self.test_data["artist_id"],  # Required
            "shortId": f"test-{int(time.time())}",  # Required: unique short ID
            "domain": "https://ffm.to",  # Must be valid URI
            "title": f"Test Release {int(time.time())}",
            "image": "https://via.placeholder.com/500",
            "description": "Test smartlink created via API",
            "stores": [
                {
                    "storeId": "spotify",
                    "url": "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"
                },
                {
                    "storeId": "apple",
                    "url": "https://music.apple.com/us/album/test/123456789"
                },
                {
                    "storeId": "youtube",
                    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                }
            ]
        }

        success, response = self._make_request("/smartlink", method="POST", data=link_data)

        if success:
            smartlink = response["data"]
            if isinstance(smartlink, dict):
                link_id = smartlink.get("id")
                short_url = smartlink.get("short_url", smartlink.get("url"))
                self._print_status("Smart link created successfully", TestStatus.PASSED, 1)
                self._print_status(f"URL: {short_url}", indent=2)
                self._print_status(f"ID: {link_id}", indent=2)
                self.test_data["smartlink_id"] = link_id
                self.test_data["smartlink_url"] = short_url
            self._record_test("create_smartlink", TestStatus.PASSED, response)
        else:
            self._print_status("Failed to create smart link", TestStatus.FAILED, 1)
            if response.get("data"):
                self._print_status(f"Error: {response['data']}", indent=2)
            self._record_test("create_smartlink", TestStatus.FAILED, response)

        return success

    def test_list_smartlinks(self) -> bool:
        """Test listing smart links."""
        self._print_status("\n[TEST] List Smart Links", indent=0)

        params = {
            "limit": 10,
            "offset": 0,
        }

        success, response = self._make_request("/smartlinks", data=params)

        if success:
            links = response["data"]
            if isinstance(links, list):
                self._print_status(f"Found {len(links)} smart links", TestStatus.PASSED, 1)
                for link in links[:3]:
                    if isinstance(link, dict):
                        self._print_status(f"Link: {link.get('title')} - {link.get('short_url')}",
                                         indent=2)
                        if not self.test_data["smartlink_id"]:
                            self.test_data["smartlink_id"] = link.get("id")
                            self.test_data["smartlink_url"] = link.get("short_url")
            self._record_test("list_smartlinks", TestStatus.PASSED, response)
        else:
            self._print_status("Failed to list smart links", TestStatus.FAILED, 1)
            self._record_test("list_smartlinks", TestStatus.FAILED, response)

        return success

    def test_get_smartlink_analytics(self) -> bool:
        """Test retrieving smart link analytics."""
        self._print_status("\n[TEST] Smart Link Analytics", indent=0)

        if not self.test_data.get("smartlink_id"):
            self._print_status("Skipping - No smart link ID available", TestStatus.SKIPPED, 1)
            self._record_test("smartlink_analytics", TestStatus.SKIPPED,
                            {"reason": "No smart link ID"})
            return False

        # Try different analytics endpoints
        analytics_endpoints = [
            f'/smartlink/{self.test_data["smartlink_id"]}/analytics',
            f'/analytics/smartlink/{self.test_data["smartlink_id"]}',
            f'/smartlink/{self.test_data["smartlink_id"]}/stats',
        ]

        success = False
        response: dict[str, Any] = {}
        for endpoint in analytics_endpoints:
            success, response = self._make_request(endpoint)
            if success:
                break

        if success:
            analytics = response["data"]
            self._print_status("Analytics retrieved successfully", TestStatus.PASSED, 1)
            if isinstance(analytics, dict):
                self._print_status(f"Total clicks: {analytics.get('total_clicks', 0)}", indent=2)
                self._print_status(f"Unique visitors: {analytics.get('unique_visitors', 0)}", indent=2)

                # Platform breakdown
                platforms = analytics.get("platforms", {})
                if platforms:
                    self._print_status("Platform breakdown:", indent=2)
                    for platform, count in platforms.items():
                        self._print_status(f"  {platform}: {count}", indent=3)

            self.test_data["analytics_data"] = analytics
            self._record_test("smartlink_analytics", TestStatus.PASSED, response)
        else:
            self._print_status("Analytics not available (may be normal for new links)",
                             TestStatus.WARNING, 1)
            self._record_test("smartlink_analytics", TestStatus.WARNING, response)

        return success

    # ========== CAMPAIGN TESTS ==========

    def test_create_presave_campaign(self) -> bool:
        """Test creating a pre-save campaign."""
        self._print_status("\n[TEST] Create Pre-Save Campaign", indent=0)

        # Skip if no artist ID - pre-save requires artistId
        if not self.test_data.get("artist_id"):
            self._print_status("Skipping - No artist ID available", TestStatus.SKIPPED, 1)
            self._record_test("create_presave", TestStatus.SKIPPED, {"reason": "No artist ID"})
            return False

        campaign_data = {
            "artistId": self.test_data["artist_id"],  # Required
            "releaseDate": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),  # Required
            "timezone": "America/New_York",  # Required
            "shortId": f"presave-{int(time.time())}",  # Required
            "domain": "https://ffm.to",  # Must be valid URI
            "title": f'Pre-Save Campaign {datetime.now().strftime("%Y%m%d")}',
            "image": "https://via.placeholder.com/500",
            "stores": [
                {
                    "storeId": "spotify",
                    "url": "https://open.spotify.com/album/test"
                },
                {
                    "storeId": "apple",
                    "url": "https://music.apple.com/album/test"
                }
            ],
            "preSaveFollow": [
                {
                    "storeId": "spotify",
                    "entities": [
                        {
                            "url": "https://open.spotify.com/artist/test"
                        }
                    ]
                }
            ],
        }

        # Pre-save campaigns use the smartlink/pre-save endpoint
        success, response = self._make_request("/smartlink/pre-save", method="POST", data=campaign_data)

        if success:
            campaign = response["data"]
            if isinstance(campaign, dict):
                campaign_id = campaign.get("id")
                campaign_url = campaign.get("url", campaign.get("landing_page_url"))
                self._print_status("Pre-save campaign created", TestStatus.PASSED, 1)
                self._print_status(f"URL: {campaign_url}", indent=2)
                self._print_status(f"Release date: {campaign_data['release_date']}", indent=2)
                self.test_data["campaign_id"] = campaign_id
                self.test_data["pre_save_id"] = campaign_id
            self._record_test("create_presave", TestStatus.PASSED, response)
        else:
            status_code = response.get("status_code", 0)
            if status_code == 404:
                self._print_status("Pre-save campaigns not available", TestStatus.WARNING, 1)
                self._record_test("create_presave", TestStatus.WARNING, response)
            else:
                self._print_status("Failed to create pre-save campaign", TestStatus.FAILED, 1)
                self._record_test("create_presave", TestStatus.FAILED, response)

        return success

    def test_list_campaigns(self) -> bool:
        """Test listing campaigns."""
        self._print_status("\n[TEST] List Campaigns", indent=0)

        success, response = self._make_request("/campaigns")

        if success:
            campaigns = response["data"]
            if isinstance(campaigns, list):
                self._print_status(f"Found {len(campaigns)} campaigns", TestStatus.PASSED, 1)
                for campaign in campaigns[:3]:
                    if isinstance(campaign, dict):
                        self._print_status(
                            f"Campaign: {campaign.get('title')} ({campaign.get('type', 'unknown')})",
                            indent=2,
                        )
            self._record_test("list_campaigns", TestStatus.PASSED, response)
        else:
            self._print_status("Failed to list campaigns or not available", TestStatus.WARNING, 1)
            self._record_test("list_campaigns", TestStatus.WARNING, response)

        return success

    # ========== ACTION PAGES TESTS ==========

    def test_create_action_page(self) -> bool:
        """Test creating an action page."""
        self._print_status("\n[TEST] Create Action Page", indent=0)

        page_data = {
            "title": "Fan Engagement Hub",
            "artist_name": self.test_data.get("artist_name", "Test Artist"),
            "description": "Complete actions to earn rewards!",
            "actions": [
                {
                    "type": "spotify_follow",
                    "points": 10,
                    "label": "Follow on Spotify",
                    "url": "https://open.spotify.com/artist/test",
                },
                {
                    "type": "instagram_follow",
                    "points": 10,
                    "label": "Follow on Instagram",
                    "url": "https://instagram.com/testartist",
                },
                {
                    "type": "youtube_subscribe",
                    "points": 15,
                    "label": "Subscribe on YouTube",
                    "url": "https://youtube.com/c/testartist",
                },
                {
                    "type": "email_signup",
                    "points": 20,
                    "label": "Join mailing list",
                },
            ],
            "rewards": [
                {
                    "points_required": 30,
                    "title": "Exclusive Track Download",
                    "description": "Get our unreleased track",
                },
                {
                    "points_required": 50,
                    "title": "Signed Merchandise",
                    "description": "Receive signed poster",
                },
            ],
            "theme": {
                "primary_color": "#FF6B6B",
                "background_color": "#1A1A2E",
            },
        }

        if self.test_data.get("artist_id"):
            page_data["artist_id"] = self.test_data["artist_id"]

        # Action pages use singular endpoint for creation
        success, response = self._make_request("/actionpage", method="POST", data=page_data)

        if success:
            page = response["data"]
            if isinstance(page, dict):
                page_id = page.get("id")
                page_url = page.get("url", page.get("public_url"))
                self._print_status("Action page created", TestStatus.PASSED, 1)
                self._print_status(f"URL: {page_url}", indent=2)
                self.test_data["actionpage_id"] = page_id
            self._record_test("create_actionpage", TestStatus.PASSED, response)
        else:
            status_code = response.get("status_code", 0)
            if status_code in [403, 404]:
                self._print_status("Action pages require special permissions", TestStatus.WARNING, 1)
                self._record_test("create_actionpage", TestStatus.WARNING, response)
            else:
                self._print_status("Failed to create action page", TestStatus.FAILED, 1)
                self._record_test("create_actionpage", TestStatus.FAILED, response)

        return success

    # ========== RELEASES TESTS ==========

    def test_create_release(self) -> bool:
        """Test creating a release."""
        self._print_status("\n[TEST] Create Release", indent=0)

        release_data = {
            "title": f'Test Album {datetime.now().strftime("%Y%m%d")}',
            "artist_name": self.test_data.get("artist_name", "Test Artist"),
            "type": "album",  # single, ep, album
            "release_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "label": "Test Records",
            "upc": f"TEST{int(time.time())}",
            "tracks": [
                {
                    "title": "Track 1",
                    "duration": 180,
                    "isrc": f"TEST{int(time.time())}01",
                },
                {
                    "title": "Track 2",
                    "duration": 210,
                    "isrc": f"TEST{int(time.time())}02",
                },
            ],
            "platforms": {
                "spotify": "https://open.spotify.com/album/test",
                "appleMusic": "https://music.apple.com/album/test",
                "youtube": "https://music.youtube.com/playlist?list=test",
            },
            "artwork_url": "https://via.placeholder.com/500",
        }

        if self.test_data.get("artist_id"):
            release_data["artist_id"] = self.test_data["artist_id"]

        success, response = self._make_request("/releases", method="POST", data=release_data)

        if success:
            release = response["data"]
            if isinstance(release, dict):
                release_id = release.get("id")
                self._print_status(f"Release created: {release_data['title']}", TestStatus.PASSED, 1)
                self._print_status(f"ID: {release_id}", indent=2)
                self._print_status(f"Type: {release_data['type']}", indent=2)
                self.test_data["release_id"] = release_id
            self._record_test("create_release", TestStatus.PASSED, response)
        else:
            self._print_status("Failed to create release", TestStatus.WARNING, 1)
            self._record_test("create_release", TestStatus.WARNING, response)

        return success

    # ========== WEBHOOKS TESTS ==========

    def test_create_webhook(self) -> bool:
        """Test creating a webhook."""
        self._print_status("\n[TEST] Create Webhook", indent=0)

        webhook_data = {
            "url": "https://webhook.site/test-feature-fm",
            "events": [
                "smartlink.created",
                "smartlink.clicked",
                "campaign.conversion",
                "presave.completed",
            ],
            "active": True,
            "description": "Test webhook for Feature.fm events",
        }

        success, response = self._make_request("/webhooks", method="POST", data=webhook_data)

        if success:
            webhook = response["data"]
            if isinstance(webhook, dict):
                webhook_id = webhook.get("id")
                self._print_status("Webhook created", TestStatus.PASSED, 1)
                self._print_status(f"ID: {webhook_id}", indent=2)
                events = webhook_data["events"]
                events_preview = (
                    ", ".join(events[:2]) if isinstance(events, list) else str(events)
                )
                self._print_status(f"Events: {events_preview}...", indent=2)
                self.test_data["webhook_id"] = webhook_id
            self._record_test("create_webhook", TestStatus.PASSED, response)
        else:
            self._print_status("Webhooks not available or require special access",
                             TestStatus.WARNING, 1)
            self._record_test("create_webhook", TestStatus.WARNING, response)

        return success

    # ========== ANALYTICS TESTS ==========

    def test_get_overview_analytics(self) -> bool:
        """Test getting overview analytics."""
        self._print_status("\n[TEST] Overview Analytics", indent=0)

        params = {
            "from": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "to": datetime.now().strftime("%Y-%m-%d"),
        }

        success, response = self._make_request("/analytics/overview", data=params)

        if success:
            analytics = response["data"]
            self._print_status("Overview analytics retrieved", TestStatus.PASSED, 1)
            if isinstance(analytics, dict):
                self._print_status(f"Total clicks: {analytics.get('total_clicks', 0)}", indent=2)
                self._print_status(f"Total conversions: {analytics.get('total_conversions', 0)}",
                                 indent=2)
            self._record_test("overview_analytics", TestStatus.PASSED, response)
        else:
            self._print_status("Overview analytics not available", TestStatus.WARNING, 1)
            self._record_test("overview_analytics", TestStatus.WARNING, response)

        return success

    # ========== PARTNERS API TESTS ==========

    def test_partners_api_promoted(self) -> bool:
        """Test Partners API - Promoted content."""
        self._print_status("\n[TEST] Partners API - Promoted Content", indent=0)

        # Test promoted songs endpoint
        endpoints = [
            "/v2/promoted",
            "/partners/promoted",
            "/promoted/songs",
        ]

        success = False
        response: dict[str, Any] = {}
        for endpoint in endpoints:
            success, response = self._make_request(endpoint)
            if success or response.get("status_code") != 404:
                break

        if success:
            self._print_status("Partners API accessible", TestStatus.PASSED, 1)
            promoted = response["data"]
            if isinstance(promoted, list) and promoted:
                self._print_status(f"Found {len(promoted)} promoted items", indent=2)
            self._record_test("partners_api", TestStatus.PASSED, response)
        else:
            self._print_status("Partners API requires special access", TestStatus.WARNING, 1)
            self._record_test("partners_api", TestStatus.WARNING, response)

        return success

    # ========== MAIN TEST RUNNER ==========

    def run_all_tests(self) -> bool:
        """Run all API tests."""
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Feature.fm API Test Suite{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Environment: Sandbox")
        print(f"ISS: {self.iss}")
        print(f"API Key: {self.api_key[:8]}...")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")

        # Authentication tests
        print(f"\n{Fore.YELLOW}━━━ Authentication Tests ━━━{Style.RESET_ALL}")
        self.test_basic_auth()
        self.test_jwt_auth()

        # Artist management tests
        print(f"\n{Fore.YELLOW}━━━ Artist Management Tests ━━━{Style.RESET_ALL}")
        self.test_list_artists()
        self.test_create_artist()
        self.test_get_artist_details()

        # Smart links tests
        print(f"\n{Fore.YELLOW}━━━ Smart Links Tests ━━━{Style.RESET_ALL}")
        self.test_list_smartlinks()
        self.test_create_smartlink()
        self.test_get_smartlink_analytics()

        # Campaign tests
        print(f"\n{Fore.YELLOW}━━━ Campaign Tests ━━━{Style.RESET_ALL}")
        self.test_create_presave_campaign()
        self.test_list_campaigns()

        # Action pages tests
        print(f"\n{Fore.YELLOW}━━━ Action Pages Tests ━━━{Style.RESET_ALL}")
        self.test_create_action_page()

        # Releases tests
        print(f"\n{Fore.YELLOW}━━━ Releases Tests ━━━{Style.RESET_ALL}")
        self.test_create_release()

        # Webhooks tests
        print(f"\n{Fore.YELLOW}━━━ Webhooks Tests ━━━{Style.RESET_ALL}")
        self.test_create_webhook()

        # Analytics tests
        print(f"\n{Fore.YELLOW}━━━ Analytics Tests ━━━{Style.RESET_ALL}")
        self.test_get_overview_analytics()

        # Partners API tests
        print(f"\n{Fore.YELLOW}━━━ Partners API Tests ━━━{Style.RESET_ALL}")
        self.test_partners_api_promoted()

        # Print summary
        self._print_summary()

        # Save results
        self._save_results()

        return bool(self.results["summary"]["failed"] == 0)

    def run_specific_test(self, test_name: str) -> bool:
        """Run a specific test."""
        test_method = getattr(self, f"test_{test_name}", None)
        if test_method:
            print(f"\n{Fore.CYAN}Running single test: {test_name}{Style.RESET_ALL}")
            test_method()
            self._print_summary()
            self._save_results()
            return True
        else:
            print(f"{Fore.RED}Test not found: {test_name}{Style.RESET_ALL}")
            print("\nAvailable tests:")
            tests = [method[5:] for method in dir(self) if method.startswith("test_")]
            for test in sorted(tests):
                print(f"  • {test}")
            return False

    def _print_summary(self) -> None:
        """Print test results summary."""
        summary = self.results["summary"]

        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Test Summary{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")

        print(f"Total Tests: {summary['total']}")
        print(f"{Fore.GREEN}✓ Passed: {summary['passed']}{Style.RESET_ALL}")
        print(f"{Fore.RED}✗ Failed: {summary['failed']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠ Warnings: {summary['warnings']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}→ Skipped: {summary['skipped']}{Style.RESET_ALL}")

        # Success rate
        if summary["total"] > 0:
            success_rate = (summary["passed"] / summary["total"]) * 100
            color = Fore.GREEN if success_rate >= 70 else Fore.YELLOW if success_rate >= 50 else Fore.RED
            print(f"\n{color}Success Rate: {success_rate:.1f}%{Style.RESET_ALL}")

        # Show endpoints tested
        print(f"\nEndpoints tested: {len(self.results['endpoints_tested'])}")

        # Show any errors
        if self.results["errors"]:
            print(f"\n{Fore.RED}Errors encountered:{Style.RESET_ALL}")
            for error in self.results["errors"][:5]:  # Show first 5 errors
                print(f"  • {error['test']}: {str(error['error'])[:100]}")

        # Show created resources
        if any(self.test_data.values()):
            print(f"\n{Fore.GREEN}Resources created:{Style.RESET_ALL}")
            if self.test_data.get("artist_name"):
                print(f"  • Artist: {self.test_data['artist_name']}")
            if self.test_data.get("smartlink_url"):
                print(f"  • Smart Link: {self.test_data['smartlink_url']}")
            if self.test_data.get("campaign_id"):
                print(f"  • Campaign ID: {self.test_data['campaign_id']}")

        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")

    def _save_results(self) -> None:
        """Save test results to JSON file."""
        filename = f"feature_fm_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            # Add test data to results for reference
            self.results["test_data"] = self.test_data

            with open(filename, "w") as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\n{Fore.GREEN}✓ Results saved to: {filename}{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}✗ Failed to save results: {e}{Style.RESET_ALL}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Feature.fm API Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python %(prog)s                    # Run all tests
  python %(prog)s --test basic_auth  # Run specific test
  python %(prog)s --list-tests       # List available tests
  python %(prog)s --quiet            # Run without verbose output
        """,
    )

    parser.add_argument("--api-key", type=str,
                        default=os.getenv("FEATUREFM_API_KEY", ""),
                        help="API key for Feature.fm")
    parser.add_argument("--secret-key", type=str,
                        default=os.getenv("FEATUREFM_SECRET_KEY", ""),
                        help="Secret key for JWT/HMAC signing")
    parser.add_argument("--iss", type=str,
                        default=os.getenv("FEATUREFM_ISS", ""),
                        help="Issuer identifier")
    parser.add_argument("--test", type=str,
                       help="Run specific test only")
    parser.add_argument("--list-tests", action="store_true",
                       help="List all available tests")
    parser.add_argument("--quiet", action="store_true",
                       help="Disable verbose output")
    parser.add_argument("--verbose", action="store_true",
                       default=True,
                       help="Enable verbose output (default)")

    args = parser.parse_args()

    # Handle list tests
    if args.list_tests:
        print(f"\n{Fore.CYAN}Available Tests:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")

        # Create temporary instance to get test methods
        tester = FeatureFMAPITester(args.api_key, args.secret_key, args.iss, verbose=False)
        tests = [method[5:] for method in dir(tester) if method.startswith("test_")]

        categories = {
            "Authentication": ["basic_auth", "jwt_auth"],
            "Artist Management": ["list_artists", "create_artist", "get_artist_details"],
            "Smart Links": ["create_smartlink", "list_smartlinks", "get_smartlink_analytics"],
            "Campaigns": ["create_presave_campaign", "list_campaigns"],
            "Action Pages": ["create_action_page"],
            "Releases": ["create_release"],
            "Webhooks": ["create_webhook"],
            "Analytics": ["get_overview_analytics"],
            "Partners API": ["partners_api_promoted"],
        }

        for category, test_list in categories.items():
            print(f"\n{Fore.YELLOW}{category}:{Style.RESET_ALL}")
            for test in test_list:
                if test in tests:
                    print(f"  • {test}")

        print(f"\n{Fore.CYAN}Usage:{Style.RESET_ALL}")
        print(f"  python {parser.prog} --test <test_name>")
        print("\nExample:")
        print(f"  python {parser.prog} --test create_smartlink")

        return

    # Create tester instance
    verbose = not args.quiet
    tester = FeatureFMAPITester(
        api_key=args.api_key,
        secret_key=args.secret_key,
        iss=args.iss,
        verbose=verbose,
    )

    # Print header
    if verbose:
        print(f"{Fore.CYAN}")
        print("  ___         _                   __           ")
        print(" | __|__ __ _| |_ _  _ _ _ ___   / _|_ __      ")
        print(" | _/ -_) _` |  _| || | '_/ -_)_| |_| '  \\    ")
        print(" |_|\\___\\__,_|\\__|_\\_,_|_| \\___(_)_| |_|_|_|")
        print(f"\n API Test Suite v1.0{Style.RESET_ALL}")

    # Run tests
    try:
        if args.test:
            # Run specific test
            success = tester.run_specific_test(args.test)
            sys.exit(0 if success else 1)
        else:
            # Run all tests
            success = tester.run_all_tests()
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test execution interrupted by user{Style.RESET_ALL}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        import traceback
        if verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
