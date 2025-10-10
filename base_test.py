#!/usr/bin/env python3
"""
Base Test Class for Feature.fm API Testing
Provides common functionality for both sandbox and production tests
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Any
from enum import Enum

import jwt
import requests
from colorama import Fore, Style, init

from config import FeatureFMConfig, Environment

# Initialize colorama
init(autoreset=True)


class TestStatus(Enum):
    """Test result statuses"""
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    WARNING = "WARNING"


class BaseAPITester:
    """Base class for Feature.fm API testing"""

    def __init__(self, config: FeatureFMConfig, *, verbose: bool = True):
        """Initialize the API tester

        Args:
            config: Configuration object for the target environment
            verbose: Enable verbose output
        """
        self.config = config
        self.verbose = verbose

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": self.config.api_key,
            "User-Agent": f"FeatureFM-API-Tester/2.0-{self.config.environment.value}",
        })

        # Test results
        self.results: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "environment": self.config.environment.value,
            "credentials": {
                "api_key": self.config.api_key[:8] + "..." if len(self.config.api_key) > 8 else self.config.api_key,
                "iss": self.config.iss,
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
        """Generate JWT token for authentication"""
        if payload is None:
            payload = {}

        payload.update({
            "iss": self.config.iss,
            "sub": self.config.api_key,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
            "jti": hashlib.sha256(f"{time.time()}".encode()).hexdigest(),
        })

        return str(jwt.encode(payload, self.config.secret_key, algorithm="HS256"))

    def _print_status(self, message: str, status: TestStatus | None = None, indent: int = 0) -> None:
        """Print status message"""
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

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        data: dict[str, Any] | None = None,
        use_jwt: bool = False,
        retry_count: int = 3,
    ) -> tuple[bool, dict[str, Any]]:
        """Make an API request with retry logic

        Args:
            endpoint: API endpoint path (without base URL)
            method: HTTP method
            data: Request payload
            use_jwt: Whether to use JWT authentication
            retry_count: Number of retry attempts

        Returns:
            Tuple of (success, response_data)
        """
        # Build full URL
        url = f"{self.config.manage_base}{endpoint}"

        headers = dict(self.session.headers)

        # Add JWT if required
        if use_jwt:
            token = self._generate_jwt()
            headers["Authorization"] = f"Bearer {token}"

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
                    self._print_status(
                        f"Rate limited. Waiting {retry_after} seconds...",
                        TestStatus.WARNING,
                        2
                    )
                    time.sleep(int(retry_after))
                    continue

                return (response.ok, result)

            except requests.exceptions.Timeout:
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)
                    continue
                return (False, {"error": "Request timeout", "url": url})

            except requests.exceptions.RequestException as e:
                return (False, {"error": str(e), "url": url})

        return (False, {"error": "All retry attempts failed", "url": url})

    def _record_test(self, test_name: str, status: TestStatus, details: dict[str, Any]) -> None:
        """Record test result"""
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

    def _print_header(self, title: str) -> None:
        """Print section header"""
        if self.verbose:
            print(f"\n{Fore.YELLOW}━━━ {title} ━━━{Style.RESET_ALL}")

    def _print_summary(self) -> None:
        """Print test results summary"""
        summary = self.results["summary"]

        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Test Summary - {self.config.get_env_name()} Environment{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")

        print(f"Total Tests: {summary['total']}")
        print(f"{Fore.GREEN}✓ Passed: {summary['passed']}{Style.RESET_ALL}")
        print(f"{Fore.RED}✗ Failed: {summary['failed']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠ Warnings: {summary['warnings']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}→ Skipped: {summary['skipped']}{Style.RESET_ALL}")

        if summary["total"] > 0:
            success_rate = (summary["passed"] / summary["total"]) * 100
            color = Fore.GREEN if success_rate >= 70 else Fore.YELLOW if success_rate >= 50 else Fore.RED
            print(f"\n{color}Success Rate: {success_rate:.1f}%{Style.RESET_ALL}")

        print(f"\nEndpoints tested: {len(self.results['endpoints_tested'])}")

        if self.results["errors"]:
            print(f"\n{Fore.RED}Errors encountered:{Style.RESET_ALL}")
            for error in self.results["errors"][:5]:
                print(f"  • {error['test']}: {str(error['error'])[:100]}")

        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")

    def _save_results(self, filename_prefix: str = "test_results") -> None:
        """Save test results to JSON file"""
        filename = f"{filename_prefix}_{self.config.environment.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filename, "w") as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\n{Fore.GREEN}✓ Results saved to: {filename}{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}✗ Failed to save results: {e}{Style.RESET_ALL}")

    # Common test methods that both sandbox and production can use

    def test_basic_auth(self) -> bool:
        """Test basic API key authentication"""
        self._print_status("\n[TEST] Basic API Key Authentication", indent=0)

        success, response = self._make_request("/artists")

        if success:
            self._print_status("API key authentication successful", TestStatus.PASSED, 1)
            self._print_status(f"Response: {response['status_code']}", indent=2)
            self._record_test("basic_auth", TestStatus.PASSED, response)
        else:
            self._print_status(
                f"Authentication failed: {response.get('error', 'Unknown error')}",
                TestStatus.FAILED,
                1
            )
            self._record_test("basic_auth", TestStatus.FAILED, response)

        return success

    def test_jwt_auth(self) -> bool:
        """Test JWT authentication"""
        self._print_status("\n[TEST] JWT Token Authentication", indent=0)

        success, response = self._make_request("/artists", use_jwt=True)

        if success:
            self._print_status("JWT authentication successful", TestStatus.PASSED, 1)
            self._record_test("jwt_auth", TestStatus.PASSED, response)
        else:
            self._print_status(
                "JWT authentication not required or failed",
                TestStatus.WARNING,
                1
            )
            self._record_test("jwt_auth", TestStatus.WARNING, response)

        return success
