#!/usr/bin/env python3
"""
Test script for MCP Atlassian Server.
"""
import json
import subprocess
import sys
import time
import threading
from queue import Queue, Empty


def send_mcp_message(process, message_id, method, params=None):
    """Send MCP message to server process."""
    message = {
        "jsonrpc": "2.0",
        "id": message_id,
        "method": method
    }
    if params:
        message["params"] = params
    
    message_json = json.dumps(message) + "\n"
    process.stdin.write(message_json.encode())
    process.stdin.flush()


def read_output(process, queue):
    """Read output from process in separate thread."""
    try:
        for line in iter(process.stdout.readline, b''):
            if line:
                queue.put(line.decode().strip())
    except Exception as e:
        queue.put(f"ERROR: {str(e)}")


def test_mcp_server():
    """Test MCP server functionality."""
    print("🧪 Testing MCP Atlassian Server...")
    
    # Start server process
    try:
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="."
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False
    
    # Setup output reading thread
    output_queue = Queue()
    output_thread = threading.Thread(target=read_output, args=(process, output_queue))
    output_thread.daemon = True
    output_thread.start()
    
    def get_response(timeout=5):
        """Get response from server."""
        try:
            return output_queue.get(timeout=timeout)
        except Empty:
            return None
    
    # Test cases
    tests = [
        {
            "name": "Initialize",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        },
        {
            "name": "Ping",
            "method": "ping",
            "params": {}
        },
        {
            "name": "Health Check",
            "method": "health",
            "params": {}
        },
        {
            "name": "List Commands",
            "method": "list_commands",
            "params": {}
        },
        {
            "name": "Tools List",
            "method": "tools/list",
            "params": {}
        }
    ]
    
    # Run tests
    passed = 0
    failed = 0
    
    for i, test in enumerate(tests, 1):
        print(f"\n🔍 Test {i}: {test['name']}")
        
        # Send message
        send_mcp_message(process, i, test["method"], test.get("params"))
        
        # Get response
        response = get_response()
        
        if response:
            try:
                response_data = json.loads(response)
                if "result" in response_data:
                    print(f"✅ Passed: {test['name']}")
                    if "success" in response_data["result"]:
                        success = response_data["result"]["success"]
                        print(f"   Success: {success}")
                        if "message" in response_data["result"]:
                            print(f"   Message: {response_data['result']['message']}")
                    passed += 1
                else:
                    print(f"❌ Failed: {test['name']} - No result in response")
                    print(f"   Response: {response}")
                    failed += 1
            except json.JSONDecodeError:
                print(f"❌ Failed: {test['name']} - Invalid JSON response")
                print(f"   Response: {response}")
                failed += 1
        else:
            print(f"❌ Failed: {test['name']} - No response")
            failed += 1
        
        time.sleep(0.5)  # Small delay between tests
    
    # Test Jira debug info (if configured)
    print(f"\n🔍 Test {len(tests)+1}: Jira Debug Info")
    send_mcp_message(process, len(tests)+1, "get_jira_debug_info", {})
    response = get_response()
    
    if response:
        try:
            response_data = json.loads(response)
            if "result" in response_data and response_data["result"].get("success"):
                print("✅ Passed: Jira Debug Info")
                debug_info = response_data["result"].get("debug_info", {})
                if "projects" in debug_info:
                    print(f"   Found {len(debug_info['projects'])} projects")
                passed += 1
            else:
                print("⚠️  Jira not configured or failed")
                print(f"   Response: {response_data.get('result', {}).get('error', 'Unknown error')}")
        except json.JSONDecodeError:
            print("❌ Failed: Jira Debug Info - Invalid JSON")
    else:
        print("❌ Failed: Jira Debug Info - No response")
    
    # Cleanup
    process.terminate()
    process.wait()
    
    # Summary
    total = len(tests) + 1
    print(f"\n📊 Test Results:")
    print(f"   Passed: {passed}/{total}")
    print(f"   Failed: {failed}/{total}")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)
