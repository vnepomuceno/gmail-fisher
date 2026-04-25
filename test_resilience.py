#!/usr/bin/env python3
"""
Test script to verify the resilience improvements work correctly.
This script simulates network timeouts and tests the retry mechanism.
"""

import socket
import time
import random
from gmail_fisher.api.gateway import GmailGateway
from gmail_fisher import get_logger

logger = get_logger(__name__)

def simulate_intermittent_timeout():
    """Simulate a function that times out twice then succeeds"""
    if not hasattr(simulate_intermittent_timeout, 'call_count'):
        simulate_intermittent_timeout.call_count = 0

    simulate_intermittent_timeout.call_count += 1

    if simulate_intermittent_timeout.call_count <= 2:  # Fail first 2 attempts
        raise socket.timeout("Simulated network timeout")
    return "Success after retries!"

def simulate_always_timeout():
    """Simulate a function that always times out"""
    raise socket.timeout("Persistent network timeout")

def test_retry_success():
    """Test that retries eventually succeed"""
    print("\n=== Testing Intermittent Timeout (Should Eventually Succeed) ===")
    try:
        result = GmailGateway._retry_api_call(simulate_intermittent_timeout)
        print(f"✅ Success: {result}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_retry_failure():
    """Test that retries eventually give up"""
    print("\n=== Testing Persistent Timeout (Should Eventually Fail) ===")
    try:
        result = GmailGateway._retry_api_call(simulate_always_timeout)
        print(f"❌ Unexpected success: {result}")
        return False
    except Exception as e:
        print(f"✅ Expected failure after retries: {e}")
        return True

def main():
    print("🔧 Testing Gmail Fisher Resilience Improvements")
    print("=" * 60)

    # Test intermittent failures (should eventually succeed)
    success_test = test_retry_success()

    # Test persistent failures (should fail after retries)
    failure_test = test_retry_failure()

    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"  Intermittent timeout handling: {'✅ PASS' if success_test else '❌ FAIL'}")
    print(f"  Persistent timeout handling:   {'✅ PASS' if failure_test else '❌ FAIL'}")

    if success_test and failure_test:
        print("\n🎉 All resilience tests passed! The script should now handle timeout errors much better.")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()
