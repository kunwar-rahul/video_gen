#!/usr/bin/env python3
"""
API Testing Suite - Validates all endpoints
"""
import requests
import json
import time
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8080"
TIMEOUT = 10


class APITester:
    def __init__(self):
        self.job_id = None
        self.passed = 0
        self.failed = 0

    def test(self, name: str, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> bool:
        """Run a single test"""
        try:
            url = f"{BASE_URL}{endpoint}"
            if method == "GET":
                resp = requests.get(url, timeout=TIMEOUT)
            elif method == "POST":
                resp = requests.post(url, json=data, timeout=TIMEOUT)
            else:
                return False

            if resp.status_code == expected_status:
                print(f"✅ {name}")
                self.passed += 1
                return resp
            else:
                print(f"❌ {name} - Expected {expected_status}, got {resp.status_code}")
                print(f"   Response: {resp.text[:200]}")
                self.failed += 1
                return False
        except Exception as e:
            print(f"❌ {name} - {str(e)}")
            self.failed += 1
            return False

    def run_all(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("Video Generation API Test Suite")
        print("=" * 60 + "\n")

        # Test 1: Health Check
        resp = self.test("Health Check", "GET", "/health", expected_status=200)

        # Test 2: Generate Video
        resp = self.test(
            "Generate Video",
            "POST",
            "/mcp/generate",
            data={
                "prompt": "A beautiful sunset over the ocean with waves",
                "duration_target": 30,
                "style": "cinematic",
                "priority": 5
            },
            expected_status=202
        )
        if resp:
            job_data = resp.json()
            self.job_id = job_data.get("job_id")
            print(f"   Job ID: {self.job_id}")

        # Test 3: List Jobs
        resp = self.test(
            "List Jobs (No Filter)",
            "GET",
            "/mcp/jobs",
            expected_status=200
        )
        if resp:
            data = resp.json()
            print(f"   Total jobs: {data.get('pagination', {}).get('total', 0)}")

        # Test 4: List Jobs with Filters
        resp = self.test(
            "List Jobs (With Filters)",
            "GET",
            "/mcp/jobs?status=pending&limit=10&offset=0",
            expected_status=200
        )

        # Test 5: Get Job Status
        if self.job_id:
            resp = self.test(
                f"Get Job Status ({self.job_id[:8]}...)",
                "GET",
                f"/mcp/status/{self.job_id}",
                expected_status=200
            )

        # Test 6: Get Storyboard
        if self.job_id:
            resp = self.test(
                f"Get Storyboard ({self.job_id[:8]}...)",
                "GET",
                f"/mcp/storyboard/{self.job_id}",
                expected_status=200
            )

        # Test 7: List Jobs with Pagination
        resp = self.test(
            "List Jobs (Pagination)",
            "GET",
            "/mcp/jobs?limit=5&offset=0&sort_by=created_at&sort_order=desc",
            expected_status=200
        )

        # Test 8: Invalid Job ID
        resp = self.test(
            "Get Invalid Job (Should fail)",
            "GET",
            "/mcp/status/invalid-job-id",
            expected_status=404
        )

        # Summary
        print("\n" + "=" * 60)
        print(f"Tests Passed: {self.passed}")
        print(f"Tests Failed: {self.failed}")
        print(f"Success Rate: {self.passed}/{self.passed + self.failed} ({100 * self.passed // (self.passed + self.failed) if (self.passed + self.failed) > 0 else 0}%)")
        print("=" * 60 + "\n")

        return self.failed == 0


if __name__ == "__main__":
    tester = APITester()
    try:
        success = tester.run_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest suite failed: {e}")
        sys.exit(1)
