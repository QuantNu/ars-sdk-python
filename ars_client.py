#!/usr/bin/env python3
"""
Agent Registration Server (ARS) Python Client

A client library for interacting with the ARS system.
"""

import json
import base64
import time
from typing import Dict, List, Optional, Any, Union
import requests


class ARSClient:
    """Client for interacting with the Agent Registration Server"""

    def __init__(self, server_url: str, agent_id: Optional[str] = None, auth_token: Optional[str] = None):
        """
        Initialize a new ARS client
        
        Args:
            server_url: URL of the ARS server
            agent_id: Optional agent ID if already registered
            auth_token: Optional authentication token if already registered
        """
        self.server_url = server_url.rstrip('/')
        self.agent_id = agent_id
        self.auth_token = auth_token
    
    def register_agent(self, 
                       name: str, 
                       version: str, 
                       endpoint: str, 
                       capabilities: List[str], 
                       public_key: bytes,
                       metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Register a new agent with the ARS
        
        Args:
            name: Human-readable name of the agent
            version: Version string
            endpoint: API endpoint URL
            capabilities: List of capabilities
            public_key: Agent's public key as bytes
            metadata: Optional additional metadata
            
        Returns:
            Dict containing agent details and authentication token
        """
        if metadata is None:
            metadata = {}
            
        payload = {
            "name": name,
            "version": version,
            "endpoint": endpoint,
            "capabilities": capabilities,
            "publicKey": base64.b64encode(public_key).decode('utf-8'),
            "metadata": metadata
        }
        
        response = requests.post(
            f"{self.server_url}/api/agents",
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"Registration failed: {response.text}")
        
        result = response.json()
        self.agent_id = result["agent"]["id"]
        self.auth_token = result["token"]
        
        return result
    
    def discover_agents(self, 
                        capabilities: Optional[List[str]] = None, 
                        metadata_filter: Optional[Dict[str, str]] = None, 
                        limit: int = 20, 
                        offset: int = 0) -> Dict[str, Any]:
        """
        Discover agents based on capabilities and metadata
        
        Args:
            capabilities: Optional list of required capabilities
            metadata_filter: Optional metadata key-value pairs to filter by
            limit: Maximum number of results to return
            offset: Pagination offset
            
        Returns:
            Dict containing list of agents and total count
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if capabilities:
            params["capability"] = ",".join(capabilities)
            
        if metadata_filter:
            params["metadata"] = json.dumps(metadata_filter)
            
        response = requests.get(
            f"{self.server_url}/api/agents/discover",
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Discovery failed: {response.text}")
            
        return response.json()
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get information about a specific agent
        
        Args:
            agent_id: ID of the agent to retrieve
            
        Returns:
            Dict containing agent details
        """
        response = requests.get(
            f"{self.server_url}/api/agents/{agent_id}"
        )
        
        if response.status_code != 200:
            raise Exception(f"Get agent failed: {response.text}")
            
        return response.json()
    
    def update_agent(self, 
                     name: Optional[str] = None, 
                     version: Optional[str] = None, 
                     endpoint: Optional[str] = None, 
                     capabilities: Optional[List[str]] = None, 
                     metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Update agent details
        
        Args:
            name: Optional new name
            version: Optional new version
            endpoint: Optional new endpoint
            capabilities: Optional new capabilities list
            metadata: Optional metadata to update/add
            
        Returns:
            Dict containing updated agent details
        """
        if not self.agent_id or not self.auth_token:
            raise Exception("Agent not registered or not authenticated")
        
        payload = {}
        
        if name is not None:
            payload["name"] = name
        if version is not None:
            payload["version"] = version
        if endpoint is not None:
            payload["endpoint"] = endpoint
        if capabilities is not None:
            payload["capabilities"] = capabilities
        if metadata is not None:
            payload["metadata"] = metadata
            
        response = requests.patch(
            f"{self.server_url}/api/protected/agents/{self.agent_id}",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"Update failed: {response.text}")
            
        return response.json()
    
    def deregister_agent(self) -> bool:
        """
        Deregister an agent
        
        Returns:
            True if successful
        """
        if not self.agent_id or not self.auth_token:
            raise Exception("Agent not registered or not authenticated")
            
        response = requests.delete(
            f"{self.server_url}/api/protected/agents/{self.agent_id}",
            headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        
        if response.status_code != 200:
            raise Exception(f"Deregistration failed: {response.text}")
            
        # Clear client state
        self.agent_id = None
        self.auth_token = None
        
        return True
    
    def verify_agent(self, agent_id: str, challenge: bytes, signature: bytes) -> bool:
        """
        Verify another agent's identity using challenge-response
        
        Args:
            agent_id: ID of the agent to verify
            challenge: Challenge bytes
            signature: Signature bytes
            
        Returns:
            True if verification successful
        """
        payload = {
            "challenge": base64.b64encode(challenge).decode('utf-8'),
            "signature": base64.b64encode(signature).decode('utf-8')
        }
        
        response = requests.post(
            f"{self.server_url}/api/agents/{agent_id}/verify",
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"Verification failed: {response.text}")
            
        result = response.json()
        return result.get("verified", False)


# Example usage
if __name__ == "__main__":
    # Create client
    client = ARSClient("https://ars.example.com")
    
    # Register a new agent
    import os
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    
    # Generate a key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Register the agent
    result = client.register_agent(
        name="Example Python Agent",
        version="1.0.0",
        endpoint="https://agent.example.com/api",
        capabilities=["query", "response", "calculation"],
        public_key=public_key,
        metadata={"description": "Example agent for demonstration", "creator": "ARS SDK"}
    )
    
    print(f"Registered agent with ID: {result['agent']['id']}")
    
    # Discover agents
    agents = client.discover_agents(
        capabilities=["query"],
        limit=5
    )
    
    print(f"Found {agents['total']} agents with 'query' capability")
    
    # Deregister
    client.deregister_agent()
    print("Agent deregistered")
