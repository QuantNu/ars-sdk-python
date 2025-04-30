"""
ARS Client with Session Management

A Python client for interacting with the Agent Registration Server (ARS) with full
session management capabilities for maintaining context across agent interactions.
"""

import json
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import requests


class Protocol(str, Enum):
    """Supported agent protocols"""
    MCP = "mcp"
    A2A = "a2a"
    CUSTOM = "custom"


class TrustLevel(str, Enum):
    """Trust levels for agents"""
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    PARTNER = "partner"
    INTERNAL = "internal"


class ARSClient:
    """
    Client for interacting with the Agent Registration Server (ARS) with session management.
    
    This client provides methods for all ARS operations including agent discovery, registration,
    session management, handler operations, and cross-protocol translation.
    """

    def __init__(self, server_url: str, token: Optional[str] = None):
        """
        Initialize the ARS client.
        
        Args:
            server_url: The URL of the ARS server
            token: Optional authentication token
        """
        self.server_url = server_url.rstrip("/")
        self.token = token
        self.current_session_id: Optional[str] = None
        self.current_session_token: Optional[str] = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including authentication token if available"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        elif self.current_session_token:
            headers["Authorization"] = f"Bearer {self.current_session_token}"
            
        return headers
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the ARS server.
        
        Args:
            method: HTTP method (get, post, put, delete)
            endpoint: API endpoint
            data: Optional request body
            
        Returns:
            Response data as a dictionary
            
        Raises:
            Exception: If the request fails
        """
        url = f"{self.server_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        try:
            if method.lower() == "get":
                response = requests.get(url, headers=headers)
            elif method.lower() == "post":
                response = requests.post(url, headers=headers, json=data)
            elif method.lower() == "put":
                response = requests.put(url, headers=headers, json=data)
            elif method.lower() == "delete":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_message = str(e)
            try:
                error_data = e.response.json()
                error_message = error_data.get("error", error_message)
            except Exception:
                pass
            
            raise Exception(f"ARS request failed: {error_message}")
    
    # Agent Registration Methods
    
    def register_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new agent with ARS.
        
        Args:
            agent_data: Agent information including name, description, capabilities, etc.
            
        Returns:
            Dictionary with registered agent details and authentication token
        """
        return self._make_request("post", "/agents", agent_data)
    
    def update_agent(self, agent_id: str, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing agent's information.
        
        Args:
            agent_id: ID of the agent to update
            agent_data: Updated agent information
            
        Returns:
            Dictionary with updated agent details
        """
        return self._make_request("put", f"/agents/{agent_id}", agent_data)
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get information about a specific agent.
        
        Args:
            agent_id: ID of the agent to retrieve
            
        Returns:
            Dictionary with agent details
        """
        return self._make_request("get", f"/agents/{agent_id}")
    
    def deregister_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Remove an agent from the registry.
        
        Args:
            agent_id: ID of the agent to deregister
            
        Returns:
            Dictionary with confirmation details
        """
        return self._make_request("delete", f"/agents/{agent_id}")
    
    # Agent Discovery Methods
    
    def discover_agents(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Discover agents matching specific criteria.
        
        Args:
            query: Query parameters like capabilities, trust levels, etc.
            
        Returns:
            Dictionary with matching agents
        """
        return self._make_request("post", "/discovery", query)
    
    # Session Management Methods
    
    def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new session for stateful agent interactions.
        
        Args:
            session_data: Initial session data including context, metadata, etc.
            
        Returns:
            Dictionary with session details and token
        """
        response = self._make_request("post", "/sessions", session_data)
        
        # Save current session info
        if "session" in response and "id" in response["session"]:
            self.current_session_id = response["session"]["id"]
            if "token" in response:
                self.current_session_token = response["token"]
        
        return response
    
    def get_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get details about a session.
        
        Args:
            session_id: Optional session ID (uses current session if not provided)
            
        Returns:
            Dictionary with session details
        """
        if not session_id and not self.current_session_id:
            raise ValueError("No session ID provided or current session")
        
        target_id = session_id or self.current_session_id
        return self._make_request("get", f"/sessions/{target_id}")
    
    def update_session(self, session_data: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing session with new data.
        
        Args:
            session_data: Updated session data
            session_id: Optional session ID (uses current session if not provided)
            
        Returns:
            Dictionary with updated session details
        """
        if not session_id and not self.current_session_id:
            raise ValueError("No session ID provided or current session")
        
        target_id = session_id or self.current_session_id
        return self._make_request("put", f"/sessions/{target_id}", session_data)
    
    def end_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        End a session.
        
        Args:
            session_id: Optional session ID (uses current session if not provided)
            
        Returns:
            Dictionary with confirmation details
        """
        if not session_id and not self.current_session_id:
            raise ValueError("No session ID provided or current session")
        
        target_id = session_id or self.current_session_id
        response = self._make_request("delete", f"/sessions/{target_id}")
        
        # Clear current session if it's the one being ended
        if self.current_session_id == target_id:
            self.current_session_id = None
            self.current_session_token = None
        
        return response
    
    def end_current_session(self) -> bool:
        """
        End the current session.
        
        Returns:
            True if successfully ended, False otherwise
        """
        if not self.current_session_id:
            return False
        
        try:
            self.end_session(self.current_session_id)
            return True
        except Exception:
            return False
    
    def resume_session(self, session_id: str) -> Dict[str, Any]:
        """
        Resume an existing session.
        
        Args:
            session_id: ID of the session to resume
            
        Returns:
            Dictionary with session details
        """
        response = self._make_request("post", f"/sessions/{session_id}/resume")
        
        # Save current session info
        if "session" in response and "id" in response["session"]:
            self.current_session_id = response["session"]["id"]
            if "token" in response:
                self.current_session_token = response["token"]
        
        return response
    
    # Task Execution Methods
    
    def execute_task(
        self, 
        capability: str,
        input_data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a task using a capable agent, optionally within a session context.
        
        Args:
            capability: The capability required for this task
            input_data: Task input data
            options: Optional parameters like session usage, specific agent ID, etc.
            
        Returns:
            Dictionary with task results
        """
        options = options or {}
        
        request_data = {
            "capability": capability,
            "input": input_data,
            "options": options
        }
        
        # Add session ID if using session and one is available
        if options.get("useSession", False) and self.current_session_id:
            request_data["sessionId"] = self.current_session_id
        
        return self._make_request("post", "/execute", request_data)
    
    # Handler Methods
    
    def load_handler(
        self,
        domain: str,
        capabilities: List[str],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load a domain-specific handler for specialized tasks.
        
        Args:
            domain: The domain name for the handler
            capabilities: Required capabilities
            session_id: Optional session ID for stateful handlers
            
        Returns:
            Dictionary with handler details
        """
        request_data = {
            "domain": domain,
            "capabilities": capabilities
        }
        
        # Use provided session ID or current session if available
        if session_id:
            request_data["sessionId"] = session_id
        elif self.current_session_id:
            request_data["sessionId"] = self.current_session_id
        
        return self._make_request("post", "/handlers/load", request_data)
    
    def unload_handler(self, handler_instance_id: str) -> Dict[str, Any]:
        """
        Unload a previously loaded handler.
        
        Args:
            handler_instance_id: ID of the handler instance to unload
            
        Returns:
            Dictionary with confirmation details
        """
        return self._make_request("delete", f"/handlers/instances/{handler_instance_id}")
    
    def get_handler_info(self, handler_id: str) -> Dict[str, Any]:
        """
        Get information about a specific handler.
        
        Args:
            handler_id: ID of the handler
            
        Returns:
            Dictionary with handler details
        """
        return self._make_request("get", f"/handlers/{handler_id}")
    
    def search_handlers(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for handlers matching specific criteria.
        
        Args:
            query: Query parameters like domain, capabilities, etc.
            
        Returns:
            Dictionary with matching handlers
        """
        return self._make_request("post", "/handlers/search", query)
    
    # Protocol Translation Methods
    
    def translate_request(self, translation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate a request between different protocols.
        
        Args:
            translation_data: Translation parameters including source and target protocols
            
        Returns:
            Dictionary with translated request
        """
        return self._make_request("post", "/translate", translation_data)
    
    # Trust Registry Methods
    
    def verify_agent(self, agent_id: str, verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit verification information for an agent.
        
        Args:
            agent_id: ID of the agent to verify
            verification_data: Verification information
            
        Returns:
            Dictionary with verification results
        """
        return self._make_request("post", f"/trust/verify/{agent_id}", verification_data)
    
    def get_trust_info(self, agent_id: str) -> Dict[str, Any]:
        """
        Get trust information for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dictionary with trust details
        """
        return self._make_request("get", f"/trust/{agent_id}")


# Helper type definitions for improved code completion
SessionData = Dict[str, Any]
AgentData = Dict[str, Any]
HandlerData = Dict[str, Any]
