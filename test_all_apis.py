#!/usr/bin/env python3
"""
Feature.fm Complete API Test Suite
Tests all three API categories: Marketing API, Publisher API, and Conversion API
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


class CompleteAPITester(BaseAPITester):
    """Complete API tester covering all Feature.fm APIs"""

    def __init__(self, config: FeatureFMConfig, *, verbose: bool = True):
        """Initialize complete API tester"""
        super().__init__(config, verbose=verbose)

        # Track which APIs are available/working
        self.api_availability = {
            "marketing_api": None,
            "publisher_api": None,
            "conversion_api": None,
        }

    # ========================================
    # MARKETING API TESTS
    # ========================================

    def test_marketing_list_artists(self) -> bool:
        """Test Marketing API - List Artists"""
        self._print_status("\n[MARKETING API] List Artists", indent=0)

        success, response = self._make_request("/artists")

        if success:
            artists = response["data"]
            if isinstance(artists, list):
                self._print_status(f"Found {len(artists)} artists", TestStatus.PASSED, 1)
                self.api_availability["marketing_api"] = True
            self._record_test("marketing_list_artists", TestStatus.PASSED, response)
        else:
            self._print_status("Failed to list artists", TestStatus.FAILED, 1)
            self.api_availability["marketing_api"] = False
            self._record_test("marketing_list_artists", TestStatus.FAILED, response)

        return success

    def test_marketing_search_artists(self, search_term: str = "test") -> bool:
        """Test Marketing API - Search Artists"""
        self._print_status(f"\n[MARKETING API] Search Artists: '{search_term}'", indent=0)

        success, response = self._make_request(f"/artists/search?term={search_term}")

        if success:
            results = response["data"]
            if isinstance(results, list):
                self._print_status(f"Found {len(results)} matching artists", TestStatus.PASSED, 1)
            self._record_test("marketing_search_artists", TestStatus.PASSED, response)
        else:
            self._print_status("Search failed or not available", TestStatus.WARNING, 1)
            self._record_test("marketing_search_artists", TestStatus.WARNING, response)

        return success

    def test_marketing_list_smartlinks(self) -> bool:
        """Test Marketing API - List SmartLinks"""
        self._print_status("\n[MARKETING API] List SmartLinks", indent=0)

        success, response = self._make_request("/smartlinks")

        if success:
            smartlinks = response["data"]
            if isinstance(smartlinks, list):
                self._print_status(f"Found {len(smartlinks)} smartlinks", TestStatus.PASSED, 1)
            self._record_test("marketing_list_smartlinks", TestStatus.PASSED, response)
        else:
            status_code = response.get("status_code", 0)
            if status_code == 404:
                self._print_status("SmartLinks list endpoint not available", TestStatus.WARNING, 1)
                self._record_test("marketing_list_smartlinks", TestStatus.WARNING, response)
            else:
                self._print_status("Failed to list smartlinks", TestStatus.FAILED, 1)
                self._record_test("marketing_list_smartlinks", TestStatus.FAILED, response)

        return success

    def test_marketing_create_artist(self) -> str | None:
        """Test Marketing API - Create Artist (Write Operation)"""
        self._print_status("\n[MARKETING API] Create Artist (WRITE)", indent=0)

        # Safety check
        if not self.config.can_write():
            self._print_status("Skipped - Write operations disabled", TestStatus.SKIPPED, 1)
            self._record_test("marketing_create_artist", TestStatus.SKIPPED, {"reason": "Write disabled"})
            return None

        self.config.require_write_permission()

        artist_data = {
            "artistName": f'API Test Artist {datetime.now().strftime("%Y%m%d_%H%M%S")}',
            "type": "artist",
            "countryCode": "US",
            "shortBio": "Created by complete API test suite",
            "tags": ["test", "api-testing"],
        }

        success, response = self._make_request("/artist", method="POST", data=artist_data)

        if success:
            artist_id = response["data"].get("id") if response.get("data") else None
            self._print_status(f"Artist created: {artist_id}", TestStatus.PASSED, 1)
            self._record_test("marketing_create_artist", TestStatus.PASSED, response)
            return artist_id
        else:
            self._print_status("Failed to create artist", TestStatus.FAILED, 1)
            self._record_test("marketing_create_artist", TestStatus.FAILED, response)

        return None

    # ========================================
    # PUBLISHER API TESTS
    # ========================================

    def test_publisher_identify_consumer(self) -> bool:
        """Test Publisher API - Identify Consumer"""
        self._print_status("\n[PUBLISHER API] Identify Consumer", indent=0)

        # Publisher API typically uses different base URL and doesn't have /manage/v1
        # It might be at root level or /consumer/ path
        consumer_data = {
            "consumerId": f"test_consumer_{int(time.time())}",
            "platform": "test",
            "timestamp": datetime.now().isoformat(),
        }

        # Try consumer identify endpoint
        url = f"{self.config.base_url}/consumer/identify"

        try:
            response = self.session.post(url, json=consumer_data, timeout=10)
            result = {
                "status_code": response.status_code,
                "data": response.json() if response.ok else response.text,
                "url": url,
            }

            if response.ok:
                self._print_status("Consumer identified successfully", TestStatus.PASSED, 1)
                self.api_availability["publisher_api"] = True
                self._record_test("publisher_identify_consumer", TestStatus.PASSED, result)
                return True
            else:
                self._print_status("Publisher API not available or requires different auth", TestStatus.WARNING, 1)
                self.api_availability["publisher_api"] = False
                self._record_test("publisher_identify_consumer", TestStatus.WARNING, result)
        except Exception as e:
            self._print_status(f"Publisher API test failed: {str(e)}", TestStatus.WARNING, 1)
            self.api_availability["publisher_api"] = False
            self._record_test("publisher_identify_consumer", TestStatus.WARNING, {"error": str(e)})

        return False

    def test_publisher_get_featured_song(self) -> bool:
        """Test Publisher API - Get Featured Song"""
        self._print_status("\n[PUBLISHER API] Get Featured Song", indent=0)

        # Featured song endpoint
        url = f"{self.config.base_url}/featured/song"

        try:
            response = self.session.post(url, json={}, timeout=10)
            result = {
                "status_code": response.status_code,
                "data": response.json() if response.ok else response.text,
                "url": url,
            }

            if response.ok:
                song_data = response.json()
                self._print_status("Featured song retrieved", TestStatus.PASSED, 1)
                if isinstance(song_data, dict):
                    self._print_status(f"Song: {song_data.get('title', 'Unknown')}", indent=2)
                self._record_test("publisher_featured_song", TestStatus.PASSED, result)
                return True
            else:
                self._print_status("Featured song endpoint not available", TestStatus.WARNING, 1)
                self._record_test("publisher_featured_song", TestStatus.WARNING, result)
        except Exception as e:
            self._print_status(f"Featured song test failed: {str(e)}", TestStatus.WARNING, 1)
            self._record_test("publisher_featured_song", TestStatus.WARNING, {"error": str(e)})

        return False

    def test_publisher_track_event(self, event_type: str = "play") -> bool:
        """Test Publisher API - Track Event"""
        self._print_status(f"\n[PUBLISHER API] Track Event: {event_type}", indent=0)

        # Event tracking typically requires a song_play_id
        song_play_id = f"test_play_{int(time.time())}"
        url = f"{self.config.base_url}/event/{song_play_id}/{event_type}"

        event_data = {
            "timestamp": datetime.now().isoformat(),
            "platform": "test",
        }

        try:
            response = self.session.post(url, json=event_data, timeout=10)
            result = {
                "status_code": response.status_code,
                "data": response.json() if response.ok else response.text,
                "url": url,
            }

            if response.ok:
                self._print_status(f"Event '{event_type}' tracked successfully", TestStatus.PASSED, 1)
                self._record_test(f"publisher_track_{event_type}", TestStatus.PASSED, result)
                return True
            else:
                self._print_status(f"Event tracking not available", TestStatus.WARNING, 1)
                self._record_test(f"publisher_track_{event_type}", TestStatus.WARNING, result)
        except Exception as e:
            self._print_status(f"Event tracking failed: {str(e)}", TestStatus.WARNING, 1)
            self._record_test(f"publisher_track_{event_type}", TestStatus.WARNING, {"error": str(e)})

        return False

    # ========================================
    # CONVERSION API TESTS
    # ========================================

    def test_conversion_initialize_session(self) -> str | None:
        """Test Conversion API - Initialize Session"""
        self._print_status("\n[CONVERSION API] Initialize Session", indent=0)

        # Conversion API might be at /conversion/ or /v1/conversion/
        url = f"{self.config.base_url}/conversion/session/init"

        session_data = {
            "sessionId": f"test_session_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "platform": "test",
        }

        try:
            response = self.session.post(url, json=session_data, timeout=10)
            result = {
                "status_code": response.status_code,
                "data": response.json() if response.ok else response.text,
                "url": url,
            }

            if response.ok:
                self._print_status("Conversion session initialized", TestStatus.PASSED, 1)
                self.api_availability["conversion_api"] = True
                self._record_test("conversion_init_session", TestStatus.PASSED, result)
                return session_data["sessionId"]
            else:
                self._print_status("Conversion API not available or requires different setup", TestStatus.WARNING, 1)
                self.api_availability["conversion_api"] = False
                self._record_test("conversion_init_session", TestStatus.WARNING, result)
        except Exception as e:
            self._print_status(f"Conversion API test failed: {str(e)}", TestStatus.WARNING, 1)
            self.api_availability["conversion_api"] = False
            self._record_test("conversion_init_session", TestStatus.WARNING, {"error": str(e)})

        return None

    def test_conversion_report_transaction(self) -> bool:
        """Test Conversion API - Report Transaction"""
        self._print_status("\n[CONVERSION API] Report Transaction", indent=0)

        url = f"{self.config.base_url}/conversion/transaction"

        transaction_data = {
            "transactionId": f"test_txn_{int(time.time())}",
            "amount": 9.99,
            "currency": "USD",
            "timestamp": datetime.now().isoformat(),
        }

        try:
            response = self.session.post(url, json=transaction_data, timeout=10)
            result = {
                "status_code": response.status_code,
                "data": response.json() if response.ok else response.text,
                "url": url,
            }

            if response.ok:
                self._print_status("Transaction reported successfully", TestStatus.PASSED, 1)
                self._record_test("conversion_report_transaction", TestStatus.PASSED, result)
                return True
            else:
                self._print_status("Transaction reporting not available", TestStatus.WARNING, 1)
                self._record_test("conversion_report_transaction", TestStatus.WARNING, result)
        except Exception as e:
            self._print_status(f"Transaction reporting failed: {str(e)}", TestStatus.WARNING, 1)
            self._record_test("conversion_report_transaction", TestStatus.WARNING, {"error": str(e)})

        return False

    # ========================================
    # RUN ALL TESTS
    # ========================================

    def run_all_tests(self) -> bool:
        """Run comprehensive tests across all three APIs"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"Feature.fm Complete API Test Suite")
        print(f"Testing: Marketing API, Publisher API, Conversion API")
        print(f"Environment: {self.config.get_env_name()}")
        print(f"Write operations: {'ENABLED' if self.config.can_write() else 'DISABLED'}")
        print(f"{'='*70}{Style.RESET_ALL}")

        # Authentication
        self._print_header("Authentication Tests")
        self.test_basic_auth()
        self.test_jwt_auth()

        # Marketing API Tests
        self._print_header("Marketing API Tests")
        self.test_marketing_list_artists()
        self.test_marketing_search_artists()
        self.test_marketing_list_smartlinks()

        if self.config.can_write():
            artist_id = self.test_marketing_create_artist()

        # Publisher API Tests
        self._print_header("Publisher API Tests")
        self.test_publisher_identify_consumer()
        self.test_publisher_get_featured_song()
        self.test_publisher_track_event("play")
        self.test_publisher_track_event("like")

        # Conversion API Tests
        self._print_header("Conversion API Tests")
        session_id = self.test_conversion_initialize_session()
        self.test_conversion_report_transaction()

        # Print API availability summary
        self._print_header("API Availability Summary")
        print(f"\n{Fore.CYAN}API Availability:{Style.RESET_ALL}")

        for api_name, available in self.api_availability.items():
            status_symbol = "✅" if available else "⚠️" if available is False else "❓"
            status_text = "Available" if available else "Not Available" if available is False else "Unknown"
            api_display = api_name.replace("_", " ").title()
            print(f"  {status_symbol} {api_display}: {status_text}")

        # Print summary and save results
        self._print_summary()
        self._save_results("complete_api_test_results")

        return bool(self.results["summary"]["failed"] == 0)


def main() -> None:
    """Main entry point for complete API tests"""
    try:
        # Determine environment
        env_choice = input(f"{Fore.CYAN}Select environment (1=Sandbox, 2=Production): {Style.RESET_ALL}").strip()

        if env_choice == "2":
            environment = Environment.PRODUCTION
            print(f"\n{Fore.RED}⚠️  WARNING: Testing against PRODUCTION{Style.RESET_ALL}")
            confirm = input(f"{Fore.YELLOW}Type 'yes' to confirm: {Style.RESET_ALL}").strip()
            if confirm.lower() != 'yes':
                print("Tests cancelled.")
                return 0
        else:
            environment = Environment.SANDBOX

        # Initialize configuration
        config = FeatureFMConfig(environment=environment)

        print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║     Feature.fm Complete API Test Suite                      ║
║                                                              ║
║  Testing all three APIs:                                    ║
║  • Marketing API (Artists, SmartLinks, Campaigns)           ║
║  • Publisher API (Events, Tracking)                         ║
║  • Conversion API (Sessions, Transactions)                  ║
║                                                              ║
║  Environment: {environment.value.upper():15s}                              ║
║  Write Ops: {'ENABLED' if config.can_write() else 'DISABLED':7s}                                       ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """)

        # Run tests
        tester = CompleteAPITester(config, verbose=True)
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
