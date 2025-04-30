#!/usr/bin/env python3
"""
ARS Python SDK - Session Management Example

This example demonstrates how to use session management features in the Python SDK
to maintain context across multiple agent interactions.
"""

import json
import time
from typing import Dict, Any

from ars_client_with_sessions import ARSClient, Protocol, TrustLevel


def main():
    """Run the session management example"""
    
    # Initialize the ARS client
    client = ARSClient(server_url="https://ars-backend.example.com")
    
    try:
        # Step 1: Create a session
        print("Creating a new session...")
        
        # Prepare initial session data
        initial_session_data = {
            "context": {
                "user": {
                    "id": "user-123",
                    "preferences": {
                        "language": "en",
                        "responseFormat": "markdown",
                        "responseLength": "concise"
                    }
                },
                "conversation": {
                    "id": f"conv-{int(time.time())}",
                    "history": []
                }
            },
            "metadata": {
                "application": "python-example",
                "sdkVersion": "1.0.0"
            },
            "ttl": 3600  # Session lifetime in seconds
        }
        
        # Create the session
        session_response = client.create_session(initial_session_data)
        
        session_id = session_response["session"]["id"]
        session_token = session_response["token"]
        
        print(f"Session created successfully with ID: {session_id}")
        print(f"Session token: {session_token}")
        
        # Step 2: Discover relevant agents
        print("\nDiscovering agents with 'text-processing' capability...")
        
        discovery_response = client.discover_agents({
            "capabilities": ["text-processing"],
            "trustLevels": [TrustLevel.VERIFIED, TrustLevel.PARTNER]
        })
        
        if not discovery_response.get("agents"):
            print("No suitable agents found.")
            return
        
        # Select the first agent from results
        selected_agent = discovery_response["agents"][0]
        print(f"Selected agent: {selected_agent['name']} (ID: {selected_agent['id']})")
        
        # Step 3: Execute a task using the session context
        print("\nExecuting a text processing task with session context...")
        
        task_input = {
            "text": "Analyze the sentiment of this message: I really enjoyed my experience with this product!",
            "operations": ["sentiment", "keywords", "summary"]
        }
        
        task_response = client.execute_task(
            capability="text-processing",
            input_data=task_input,
            options={
                "useSession": True,
                "agentId": selected_agent["id"]
            }
        )
        
        print("Task execution result:")
        print(json.dumps(task_response.get("result", {}), indent=2))
        
        # Step 4: Update the session with task results
        print("\nUpdating session with task results...")
        
        # Get current session data
        current_session = client.get_session()
        session_data = current_session["session"]["data"]
        
        # Update conversation history
        if "context" in session_data and "conversation" in session_data["context"]:
            session_data["context"]["conversation"]["history"].append({
                "type": "task",
                "timestamp": int(time.time()),
                "agent": selected_agent["id"],
                "input": task_input,
                "result": task_response.get("result", {})
            })
        
        # Update the session
        updated_session = client.update_session(session_data)
        print("Session updated successfully")
        
        # Step 5: Execute another task using updated context
        print("\nExecuting a second task with updated session context...")
        
        # This task can use context from the previous interaction
        second_task_input = {
            "text": "Based on the previous sentiment analysis, suggest related products.",
            "maxSuggestions": 3
        }
        
        second_task_response = client.execute_task(
            capability="recommendation",
            input_data=second_task_input,
            options={
                "useSession": True  # Using the current session
            }
        )
        
        print("Second task execution result:")
        print(json.dumps(second_task_response.get("result", {}), indent=2))
        
        # Step 6: Load a domain-specific handler with session context
        print("\nLoading a domain-specific handler with session context...")
        
        handler_response = client.load_handler(
            domain="text-analytics",
            capabilities=["text-processing", "recommendation"],
            # Session ID is automatically used from the current session
        )
        
        handler = handler_response["handler"]
        handler_instance_id = handler_response["handlerInstanceId"]
        
        print(f"Loaded handler: {handler['name']} (Instance ID: {handler_instance_id})")
        
        # Step 7: Execute task through the domain handler
        print("\nExecuting task through the domain handler...")
        
        handler_task_input = {
            "text": "Analyze customer feedback across all previous interactions and provide insights",
            "analysisType": "comprehensive"
        }
        
        handler_task_response = client.execute_task(
            capability="text-processing",
            input_data=handler_task_input,
            options={
                "useSession": True,
                "domain": "text-analytics",
                "handlerInstanceId": handler_instance_id
            }
        )
        
        print("Handler task execution result:")
        print(json.dumps(handler_task_response.get("result", {}), indent=2))
        
        # Step 8: Demonstrate protocol translation with session context
        print("\nDemonstrating protocol translation with session context...")
        
        # Create a request in MCP format
        mcp_request = {
            "request_id": f"req-{int(time.time())}",
            "operation": "analyze",
            "parameters": {
                "text": "Translate this to A2A format while preserving session context",
                "mode": "detailed"
            }
        }
        
        # Translate to A2A format
        translation_response = client.translate_request({
            "sourceProtocol": Protocol.MCP,
            "targetProtocol": Protocol.A2A,
            "requestData": mcp_request,
            "capability": "text-processing",
            "sessionId": session_id  # Explicitly providing session ID
        })
        
        print("Protocol translation result:")
        print(json.dumps(translation_response.get("translatedRequest", {}), indent=2))
        
        # Step 9: Demonstrate session resumption
        print("\nDemonstrating session persistence by simulating a new client instance...")
        
        # Create a new client instance to simulate a new connection
        new_client = ARSClient(server_url="https://ars-backend.example.com")
        
        # Resume the existing session
        resumed_session = new_client.resume_session(session_id)
        print(f"Session resumed with ID: {resumed_session['session']['id']}")
        
        # Verify session data was preserved
        session_history_count = len(resumed_session["session"]["data"]["context"]["conversation"]["history"])
        print(f"Session contains {session_history_count} historical interactions")
        
        # Step 10: End the session
        print("\nEnding the session...")
        session_ended = new_client.end_current_session()
        print(f"Session ended successfully: {session_ended}")
        
    except Exception as e:
        print(f"Error in session management example: {str(e)}")


if __name__ == "__main__":
    main()
