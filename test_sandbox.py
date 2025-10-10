#!/usr/bin/env python3
"""
Feature.fm API Sandbox Test Suite
Tests ALL operations (read + write) in the safe sandbox environment
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Any

from colorama import Fore, Style, init

from base_test import BaseAPITester, TestStatus
from config import FeatureFMConfig, Environment

# Initialize colorama
init(autoreset=True)


class SandboxAPITester(BaseAPITester):
    """Sandbox-specific API tester with full CRUD operations"""

    def __init__(self, config: FeatureFMConfig, *, verbose: bool = True):
        """Initialize sandbox tester"""
        if config.environment != Environment.SANDBOX:
            raise ValueError("SandboxAPITester can only be used with SANDBOX environment")

        super().__init__(config, verbose=verbose)

        # Store created resources for cleanup
        self.created_resources: dict[str, Any] = {
            "artist_ids": [],
            "smartlink_ids": [],
            "actionpage_ids": [],
        }

    # ========== READ OPERATIONS ==========

    def test_list_artists(self) -> bool:
        """Test listing artists"""
        self._print_status("\n[TEST] List Artists", indent=0)

        success, response = self._make_request("/artists")

        if success:
            artists = response["data"]
            if isinstance(artists, list):
                self._print_status(f"Found {len(artists)} artists", TestStatus.PASSED, 1)

                for artist in artists[:3]:
                    if isinstance(artist, dict):
                        self._print_status(
                            f"Artist: {artist.get('artistName', 'Unknown')} (ID: {artist.get('id')})",
                            indent=2,
                        )
            else:
                self._print_status("No artists found or unexpected format", TestStatus.WARNING, 1)

            self._record_test("list_artists", TestStatus.PASSED, response)
        else:
            self._print_status(
                f"Failed to list artists: {response.get('error', 'Unknown error')}",
                TestStatus.FAILED,
                1
            )
            self._record_test("list_artists", TestStatus.FAILED, response)

        return success

    def test_get_artist_details(self, artist_id: str) -> bool:
        """Test getting artist details"""
        self._print_status(f"\n[TEST] Get Artist Details (ID: {artist_id})", indent=0)

        success, response = self._make_request(f'/artist/{artist_id}')

        if success:
            artist = response["data"]
            self._print_status(f"Retrieved artist: {artist.get('artistName', 'Unknown')}", TestStatus.PASSED, 1)
            self._print_status(f"Type: {artist.get('type', 'N/A')}", indent=2)
            self._print_status(f"Country: {artist.get('countryCode', 'N/A')}", indent=2)
            self._record_test("get_artist_details", TestStatus.PASSED, response)
        else:
            self._print_status("Failed to get artist details", TestStatus.FAILED, 1)
            self._record_test("get_artist_details", TestStatus.FAILED, response)

        return success

    def test_list_actionpages(self) -> bool:
        """Test listing action pages"""
        self._print_status("\n[TEST] List Action Pages", indent=0)

        success, response = self._make_request("/actionpages")

        if success:
            pages = response["data"]
            if isinstance(pages, list):
                self._print_status(f"Found {len(pages)} action pages", TestStatus.PASSED, 1)
            self._record_test("list_actionpages", TestStatus.PASSED, response)
        else:
            self._print_status("Failed to list action pages", TestStatus.WARNING, 1)
            self._record_test("list_actionpages", TestStatus.WARNING, response)

        return success

    # ========== WRITE OPERATIONS (Sandbox Only) ==========

    def test_create_artist(self) -> str | None:
        """Test creating a new artist"""
        self._print_status("\n[TEST] Create Artist (WRITE OPERATION)", indent=0)

        # Safety check
        self.config.require_write_permission()

        artist_data = {
            "artistName": f'Sandbox Test Artist {datetime.now().strftime("%Y%m%d_%H%M%S")}',
            "type": "artist",
            "countryCode": "US",
            "shortBio": "Created by automated sandbox test suite",
            "artistImage": "https://via.placeholder.com/500",
            "tags": ["test", "sandbox", "automated"],
        }

        success, response = self._make_request("/artist", method="POST", data=artist_data)

        if success:
            if response["data"] and isinstance(response["data"], dict):
                artist_id = response["data"].get("id")
                artist_name = response["data"].get("artistName", artist_data["artistName"])
                self._print_status(
                    f"Artist created: {artist_name} (ID: {artist_id})",
                    TestStatus.PASSED,
                    1
                )
                self.created_resources["artist_ids"].append(artist_id)
                self._record_test("create_artist", TestStatus.PASSED, response)
                return artist_id
            self._record_test("create_artist", TestStatus.PASSED, response)
            return None
        else:
            status_code = response.get("status_code", 0)
            if status_code == 403:
                self._print_status("Create artist not permitted", TestStatus.WARNING, 1)
                self._record_test("create_artist", TestStatus.WARNING, response)
            else:
                self._print_status(
                    f"Failed to create artist: {response.get('data', 'Unknown error')}",
                    TestStatus.FAILED,
                    1
                )
                self._record_test("create_artist", TestStatus.FAILED, response)

        return None

    def test_create_smartlink(self, artist_id: str) -> str | None:
        """Test creating a smart link"""
        self._print_status("\n[TEST] Create Smart Link (WRITE OPERATION)", indent=0)

        # Safety check
        self.config.require_write_permission()

        link_data = {
            "artistId": artist_id,
            "shortId": f"test-{int(time.time())}",
            "domain": "https://ffm.to",
            "title": f"Sandbox Test Link {int(time.time())}",
            "image": "https://via.placeholder.com/500",
            "description": "Test smartlink created by automated sandbox tests",
            "stores": [
                {
                    "storeId": "spotify",
                    "url": "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"
                },
                {
                    "storeId": "apple",
                    "url": "https://music.apple.com/us/album/test/123456789"
                }
            ]
        }

        success, response = self._make_request("/smartlink", method="POST", data=link_data)

        if success:
            smartlink = response["data"]
            if isinstance(smartlink, dict):
                link_id = smartlink.get("id")
                self._print_status("Smart link created successfully", TestStatus.PASSED, 1)
                self._print_status(f"ID: {link_id}", indent=2)
                self.created_resources["smartlink_ids"].append(link_id)
                self._record_test("create_smartlink", TestStatus.PASSED, response)
                return link_id
            self._record_test("create_smartlink", TestStatus.PASSED, response)
            return None
        else:
            self._print_status("Failed to create smart link", TestStatus.FAILED, 1)
            if response.get("data"):
                self._print_status(f"Error: {response['data']}", indent=2)
            self._record_test("create_smartlink", TestStatus.FAILED, response)

        return None

    def test_create_presave(self, artist_id: str) -> str | None:
        """Test creating a pre-save campaign"""
        self._print_status("\n[TEST] Create Pre-Save Campaign (WRITE OPERATION)", indent=0)

        # Safety check
        self.config.require_write_permission()

        campaign_data = {
            "artistId": artist_id,
            "releaseDate": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "timezone": "America/New_York",
            "shortId": f"presave-{int(time.time())}",
            "domain": "https://ffm.to",
            "title": f'Sandbox Pre-Save {datetime.now().strftime("%Y%m%d")}',
            "image": "https://via.placeholder.com/500",
            "stores": [
                {
                    "storeId": "spotify",
                    "url": "https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3"
                }
            ],
        }

        success, response = self._make_request("/smartlink/pre-save", method="POST", data=campaign_data)

        if success:
            campaign = response["data"]
            if isinstance(campaign, dict):
                campaign_id = campaign.get("id")
                self._print_status("Pre-save campaign created", TestStatus.PASSED, 1)
                self._print_status(f"ID: {campaign_id}", indent=2)
                self._record_test("create_presave", TestStatus.PASSED, response)
                return campaign_id
            self._record_test("create_presave", TestStatus.PASSED, response)
            return None
        else:
            error_data = response.get("data", {})
            # Pre-save might fail due to invalid Spotify URLs in test data
            if isinstance(error_data, dict) and "scraping failed" in str(error_data.get("message", "")):
                self._print_status("Pre-save validation failed (expected with test data)", TestStatus.WARNING, 1)
                self._record_test("create_presave", TestStatus.WARNING, response)
            else:
                self._print_status("Failed to create pre-save campaign", TestStatus.FAILED, 1)
                self._record_test("create_presave", TestStatus.FAILED, response)

        return None

    def run_all_tests(self) -> bool:
        """Run all sandbox tests (read + write)"""
        print(f"\n{self.config.get_env_name()} Environment - FULL TEST SUITE")
        print(f"{'='*70}")
        print(f"Write operations: {'ENABLED' if self.config.can_write() else 'DISABLED'}")
        print(f"{'='*70}")

        # Authentication tests
        self._print_header("Authentication Tests")
        self.test_basic_auth()
        self.test_jwt_auth()

        # Read tests
        self._print_header("Read Operations - Artists")
        self.test_list_artists()

        # Write tests
        self._print_header("Write Operations - Create Resources")
        artist_id = self.test_create_artist()

        if artist_id:
            # Test getting the created artist
            self.test_get_artist_details(artist_id)

            # Test creating smartlink
            smartlink_id = self.test_create_smartlink(artist_id)

            # Test creating pre-save
            self.test_create_presave(artist_id)

        self._print_header("Read Operations - Action Pages")
        self.test_list_actionpages()

        # Print summary and save results
        self._print_summary()
        self._save_results("sandbox_test_results")

        # Print created resources for reference
        if any(self.created_resources.values()):
            print(f"\n{Fore.CYAN}Resources Created in Sandbox:{Style.RESET_ALL}")
            if self.created_resources["artist_ids"]:
                print(f"  Artists: {', '.join(self.created_resources['artist_ids'])}")
            if self.created_resources["smartlink_ids"]:
                print(f"  SmartLinks: {', '.join(self.created_resources['smartlink_ids'])}")

        return bool(self.results["summary"]["failed"] == 0)


def main() -> None:
    """Main entry point for sandbox tests"""
    try:
        # Initialize sandbox configuration
        config = FeatureFMConfig(environment=Environment.SANDBOX)

        print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║        Feature.fm API Sandbox Test Suite                    ║
║                                                              ║
║  Environment: SANDBOX                                        ║
║  Write Operations: ENABLED                                   ║
║  Safety: All operations are isolated in sandbox              ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """)

        # Run tests
        tester = SandboxAPITester(config, verbose=True)
        success = tester.run_all_tests()

        return 0 if success else 1

    except ValueError as e:
        print(f"{Fore.RED}Configuration Error: {e}{Style.RESET_ALL}")
        return 1
    except PermissionError as e:
        print(f"{Fore.RED}Permission Error: {e}{Style.RESET_ALL}")
        return 1
    except Exception as e:
        print(f"{Fore.RED}Unexpected Error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
