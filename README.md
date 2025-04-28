# Agent Registration Server Python Client

A Python client library for interacting with the Agent Registration Server (ARS).

## Installation

```bash
pip install ars-client
```

Or install from source:

```bash
git clone https://github.com/yourusername/ars.git
cd ars/sdk/python
pip install -e .
```

## Usage

```python
from ars_client import ARSClient
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Create client
client = ARSClient("https://ars.example.com")

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
    name="My Agent",
    version="1.0.0",
    endpoint="https://myagent.example.com/api",
    capabilities=["query", "response"],
    public_key=public_key,
    metadata={"description": "My awesome agent"}
)

# Save the agent ID and token for future sessions
agent_id = result["agent"]["id"]
token = result["token"]

# Discover other agents
agents = client.discover_agents(
    capabilities=["query"],
    limit=5
)

print(f"Found {agents['total']} agents with 'query' capability")

# Get a specific agent
agent = client.get_agent("some-agent-id")
print(f"Agent name: {agent['name']}")

# Update your agent
client.update_agent(
    version="1.0.1",
    metadata={"status": "active"}
)

# Deregister when done
client.deregister_agent()
```

## API Reference

### ARSClient

```python
client = ARSClient(server_url, agent_id=None, auth_token=None)
```

Create a new client with optional agent ID and token if already registered.

### Methods

- `register_agent(name, version, endpoint, capabilities, public_key, metadata=None)`: Register a new agent
- `discover_agents(capabilities=None, metadata_filter=None, limit=20, offset=0)`: Find agents matching criteria
- `get_agent(agent_id)`: Get details for a specific agent
- `update_agent(name=None, version=None, endpoint=None, capabilities=None, metadata=None)`: Update your agent
- `deregister_agent()`: Remove your agent from the registry
- `verify_agent(agent_id, challenge, signature)`: Verify another agent's identity

## Error Handling

All methods raise exceptions if the server returns an error status. You should handle these exceptions in your code:

```python
try:
    agents = client.discover_agents(capabilities=["query"])
except Exception as e:
    print(f"Error discovering agents: {e}")
```

## License

MIT
