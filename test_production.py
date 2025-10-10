#!/usr/bin/env python3
"""
Feature.fm API Production Test Suite
Tests ONLY READ operations to safely monitor production API
**WRITE OPERATIONS ARE STRICTLY DISABLED**
"""

from __future__ import annotations

from colorama import Fore, Style

from base_test import BaseAPITester, TestStatus
from config import FeatureFMConfig, Environment


class ProductionAPITester(BaseAPITester):
    """Production-specific API tester with READ-ONLY operations"""

    def __init__(self, config: FeatureFMConfig, *, verbose: bool = True):
        """Initialize production tester"""
        if config.environment != Environment.PRODUCTION:
            raise ValueError("ProductionAPITester can only be used with PRODUCTION environment")

        if config.can_write():
            raise PermissionError(
                "CRITICAL SAFETY ERROR: Write operations must be disabled for production environment"
            )

        super().__init__(config, verbose=verbose)

    # ========== READ-ONLY OPERATIONS ==========

    def test_list_artists(self) -> bool:
        """Test listing artists (READ-ONLY)"""
        self._print_status("\n[TEST] List Artists (READ-ONLY)", indent=0)

        success, response = self._make_request("/artists")

        if success:
            artists = response["data"]
            if isinstance(artists, list):
                self._print_status(f"Found {len(artists)} production artists", TestStatus.PASSED, 1)

                # Show summary only, don't expose detailed production data
                self._print_status(f"Total count: {len(artists)}", indent=2)

            self._record_test("list_artists", TestStatus.PASSED, response)
        else:
            self._print_status(
                f"Failed to list artists: {response.get('error', 'Unknown error')}",
                TestStatus.FAILED,
                1
            )
            self._record_test("list_artists", TestStatus.FAILED, response)

        return success

    def test_search_artists(self, search_term: str = "test") -> bool:
        """Test searching artists (READ-ONLY)"""
        self._print_status(f"\n[TEST] Search Artists: '{search_term}' (READ-ONLY)", indent=0)

        success, response = self._make_request(f"/artists/search?term={search_term}")

        if success:
            results = response["data"]
            if isinstance(results, list):
                self._print_status(f"Found {len(results)} matching artists", TestStatus.PASSED, 1)
            self._record_test("search_artists", TestStatus.PASSED, response)
        else:
            self._print_status("Search failed or not available", TestStatus.WARNING, 1)
            self._record_test("search_artists", TestStatus.WARNING, response)

        return success

    def test_get_artist_details(self, artist_id: str) -> bool:
        """Test getting specific artist details (READ-ONLY)"""
        self._print_status(f"\n[TEST] Get Artist Details (READ-ONLY)", indent=0)

        success, response = self._make_request(f'/artist/{artist_id}')

        if success:
            artist = response["data"]
            self._print_status(
                f"Retrieved artist data successfully",
                TestStatus.PASSED,
                1
            )
            # Don't print sensitive production data
            self._record_test("get_artist_details", TestStatus.PASSED, response)
        else:
            self._print_status("Failed to get artist details", TestStatus.FAILED, 1)
            self._record_test("get_artist_details", TestStatus.FAILED, response)

        return success

    def test_list_actionpages(self) -> bool:
        """Test listing action pages (READ-ONLY)"""
        self._print_status("\n[TEST] List Action Pages (READ-ONLY)", indent=0)

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

    def test_search_actionpages(self, search_term: str = "") -> bool:
        """Test searching action pages (READ-ONLY)"""
        self._print_status(f"\n[TEST] Search Action Pages (READ-ONLY)", indent=0)

        success, response = self._make_request(f"/actionpages/search?term={search_term}")

        if success:
            results = response["data"]
            if isinstance(results, list):
                self._print_status(f"Found {len(results)} matching action pages", TestStatus.PASSED, 1)
            self._record_test("search_actionpages", TestStatus.PASSED, response)
        else:
            self._print_status("Search failed or not available", TestStatus.WARNING, 1)
            self._record_test("search_actionpages", TestStatus.WARNING, response)

        return success

    def test_get_smartlink(self, smartlink_id: str) -> bool:
        """Test getting SmartLink details (READ-ONLY)"""
        self._print_status(f"\n[TEST] Get SmartLink Details (READ-ONLY)", indent=0)

        success, response = self._make_request(f'/smartlink/{smartlink_id}')

        if success:
            self._print_status("SmartLink data retrieved successfully", TestStatus.PASSED, 1)
            self._record_test("get_smartlink", TestStatus.PASSED, response)
        else:
            self._print_status("Failed to get SmartLink details", TestStatus.FAILED, 1)
            self._record_test("get_smartlink", TestStatus.FAILED, response)

        return success

    # ========== SAFETY CHECKS ==========

    def _prevent_write_operation(self, operation_name: str) -> None:
        """Block any write operations and log the attempt"""
        error_msg = (
            f"BLOCKED: Attempted to execute write operation '{operation_name}' "
            f"in PRODUCTION environment. Write operations are strictly prohibited."
        )
        self._print_status(error_msg, TestStatus.FAILED, 1)
        raise PermissionError(error_msg)

    # These methods are intentionally NOT implemented to prevent accidental writes

    def test_create_artist(self) -> None:
        """BLOCKED: Create operations not allowed in production"""
        self._prevent_write_operation("create_artist")

    def test_create_smartlink(self, artist_id: str) -> None:
        """BLOCKED: Create operations not allowed in production"""
        self._prevent_write_operation("create_smartlink")

    def test_create_presave(self, artist_id: str) -> None:
        """BLOCKED: Create operations not allowed in production"""
        self._prevent_write_operation("create_presave")

    def test_update_artist(self, artist_id: str, data: dict) -> None:
        """BLOCKED: Update operations not allowed in production"""
        self._prevent_write_operation("update_artist")

    def test_delete_resource(self, resource_id: str) -> None:
        """BLOCKED: Delete operations not allowed in production"""
        self._prevent_write_operation("delete_resource")

    def run_all_tests(self, sample_artist_id: str | None = None) -> bool:
        """Run all production tests (READ-ONLY)

        Args:
            sample_artist_id: Optional artist ID to test detail retrieval
        """
        print(f"\n{Fore.RED}{'='*70}")
        print(f"PRODUCTION ENVIRONMENT - READ-ONLY MODE")
        print(f"{'='*70}")
        print(f"Write operations: DISABLED")
        print(f"Safety: All write attempts will be blocked")
        print(f"{'='*70}{Style.RESET_ALL}")

        # Authentication tests
        self._print_header("Authentication Tests")
        auth_success = self.test_basic_auth()

        if not auth_success:
            print(f"\n{Fore.RED}Authentication failed. Stopping tests.{Style.RESET_ALL}")
            self._print_summary()
            return False

        self.test_jwt_auth()

        # Read tests
        self._print_header("Read Operations - Artists")
        self.test_list_artists()
        self.test_search_artists("test")

        if sample_artist_id:
            self.test_get_artist_details(sample_artist_id)

        self._print_header("Read Operations - Action Pages")
        self.test_list_actionpages()
        self.test_search_actionpages()

        # Print summary and save results
        self._print_summary()
        self._save_results("production_test_results")

        print(f"\n{Fore.GREEN}✓ All production tests completed safely (read-only){Style.RESET_ALL}")

        return bool(self.results["summary"]["failed"] == 0)


def main() -> None:
    """Main entry point for production tests"""
    try:
        # Initialize production configuration
        config = FeatureFMConfig(environment=Environment.PRODUCTION)

        # Double-check write protection
        if config.can_write():
            raise PermissionError(
                "CRITICAL SAFETY ERROR: Production configuration allows writes! "
                "This should never happen. Check config.py"
            )

        print(f"""
{Fore.RED}╔══════════════════════════════════════════════════════════════╗
║     Feature.fm API Production Test Suite (READ-ONLY)        ║
║                                                              ║
║  ⚠️  PRODUCTION ENVIRONMENT - EXTREME CAUTION  ⚠️            ║
║                                                              ║
║  Write Operations: DISABLED                                  ║
║  Delete Operations: DISABLED                                 ║
║  Update Operations: DISABLED                                 ║
║                                                              ║
║  Only read operations will be executed                       ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """)

        # Require user confirmation
        response = input(f"\n{Fore.YELLOW}Are you sure you want to run tests against PRODUCTION? (type 'yes' to confirm): {Style.RESET_ALL}")

        if response.lower() != 'yes':
            print(f"{Fore.CYAN}Tests cancelled by user.{Style.RESET_ALL}")
            return 0

        # Run tests
        tester = ProductionAPITester(config, verbose=True)

        # Optionally ask for a sample artist ID to test detail retrieval
        print(f"\n{Fore.CYAN}Optional: Enter an artist ID to test detail retrieval (or press Enter to skip):{Style.RESET_ALL}")
        sample_id = input().strip()

        success = tester.run_all_tests(sample_artist_id=sample_id if sample_id else None)

        return 0 if success else 1

    except ValueError as e:
        print(f"{Fore.RED}Configuration Error: {e}{Style.RESET_ALL}")
        return 1
    except PermissionError as e:
        print(f"{Fore.RED}CRITICAL SAFETY ERROR: {e}{Style.RESET_ALL}")
        return 1
    except Exception as e:
        print(f"{Fore.RED}Unexpected Error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
