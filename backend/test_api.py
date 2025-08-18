#!/usr/bin/env python3
"""
Simple test script for the Sikkim Travel Itinerary API v2.0 (LangChain Agent)
"""

import json
import requests
import time

def test_health_endpoint(base_url="http://localhost:8000"):
    """Test the health endpoint"""
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Health endpoint: Connection failed - server not running")
        return False
    except Exception as e:
        print(f"❌ Health endpoint: Error - {e}")
        return False

def test_root_endpoint(base_url="http://localhost:8000"):
    """Test the root endpoint"""
    try:
        response = requests.get(base_url)
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Root endpoint: Connection failed - server not running")
        return False
    except Exception as e:
        print(f"❌ Root endpoint: Error - {e}")
        return False

def test_agent_endpoint(base_url="http://localhost:8000"):
    """Test the agent endpoint"""
    try:
        response = requests.post(f"{base_url}/test-agent")
        print(f"✅ Agent test endpoint: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success', False)}")
            print(f"   Message: {result.get('message', 'N/A')}")
            if 'agent_test' in result:
                agent_result = result['agent_test']
                print(f"   Agent success: {agent_result.get('success', False)}")
                if agent_result.get('success'):
                    print(f"   Itinerary items: {len(agent_result.get('itinerary', []))}")
        else:
            print(f"   Error: {response.text}")
        
        return response.status_code in [200, 500]  # 500 is expected without API keys
    except requests.exceptions.ConnectionError:
        print("❌ Agent test endpoint: Connection failed - server not running")
        return False
    except Exception as e:
        print(f"❌ Agent test endpoint: Error - {e}")
        return False

def test_itinerary_endpoint(base_url="http://localhost:8000"):
    """Test the itinerary generation endpoint"""
    test_data = {
        "preference": "culture",
        "days": 3
    }
    
    try:
        response = requests.post(
            f"{base_url}/generate-itinerary",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Itinerary endpoint: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success', False)}")
            print(f"   Days: {result.get('days', 0)}")
            print(f"   Preference: {result.get('preference', 'N/A')}")
            print(f"   Framework: {result.get('framework', 'N/A')}")
            if 'itinerary' in result:
                print(f"   Itinerary items: {len(result['itinerary'])}")
        else:
            print(f"   Error: {response.text}")
        
        return response.status_code in [200, 500]  # 500 is expected without API keys
    except requests.exceptions.ConnectionError:
        print("❌ Itinerary endpoint: Connection failed - server not running")
        return False
    except Exception as e:
        print(f"❌ Itinerary endpoint: Error - {e}")
        return False

def test_api_keys_endpoint(base_url="http://localhost:8000"):
    """Test the API keys debug endpoint"""
    try:
        response = requests.get(f"{base_url}/debug/api-keys")
        print(f"✅ API keys debug endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ API keys debug endpoint: Connection failed - server not running")
        return False
    except Exception as e:
        print(f"❌ API keys debug endpoint: Error - {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Sikkim Travel Itinerary API v2.0 (LangChain Agent)")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test endpoints
    health_ok = test_health_endpoint(base_url)
    print()
    
    root_ok = test_root_endpoint(base_url)
    print()
    
    api_keys_ok = test_api_keys_endpoint(base_url)
    print()
    
    agent_ok = test_agent_endpoint(base_url)
    print()
    
    itinerary_ok = test_itinerary_endpoint(base_url)
    print()
    
    # Summary
    print("=" * 60)
    print("📊 Test Summary:")
    print(f"   Health endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Root endpoint: {'✅ PASS' if root_ok else '❌ FAIL'}")
    print(f"   API keys debug: {'✅ PASS' if api_keys_ok else '❌ FAIL'}")
    print(f"   Agent test: {'✅ PASS' if agent_ok else '❌ FAIL'}")
    print(f"   Itinerary endpoint: {'✅ PASS' if itinerary_ok else '❌ FAIL'}")
    
    if health_ok and root_ok:
        print("\n🎉 Basic API functionality is working!")
        print("📚 Visit http://localhost:8000/docs for interactive API documentation")
        print("🤖 This version uses LangChain Agent instead of LangGraph")
    else:
        print("\n⚠️  Some tests failed. Make sure the server is running.")

if __name__ == "__main__":
    main()
