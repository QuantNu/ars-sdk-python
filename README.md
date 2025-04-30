# ARS Python SDK

Python SDK for the Agent Registration Server (ARS).

## Overview

The ARS Python SDK provides a client library for interacting with the Agent Registration Server, enabling Python applications to register agents, discover capabilities, manage sessions, and execute operations across different agent protocols.

## Installation

### For Users

```bash
pip install ars-client
```

### For Developers

Clone the repository and install in development mode:

```bash
git clone https://github.com/quantnu/ars.git
cd ars/sdk/python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

## Building Independently

The Python SDK can be built independently using the included Makefile:

```bash
# Create virtual environment, install dependencies, and build
make

# Individual steps
make venv      # Create virtual environment
make setup     # Install dependencies
make build     # Build the package
make test      # Run tests
make clean     # Clean build artifacts
make dist      # Create distribution packages
```

If you don't have `make` available, you can use these commands directly:

```bash
# Create virtual environment
python -m venv venv

# Install in development mode with dev dependencies
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"

# Run tests
pytest tests/

# Build distribution packages
python setup.py sdist bdist_wheel
```

## Usage

```python
from ars_client import ARSClient, Protocol, TrustLevel

# Create client
client = ARSClient(server_url="https://ars.example.com")

# Register an agent
agent, token = client.register_agent(
    name="Example Agent",
    description="An example agent demonstrating basic functionality",
    capabilities=["translate", "summarize"],
    endpoint="https://example.com/agent",
    protocol=Protocol.MCP,
    protocol_version="1.0",
    public_key="example-public-key"
)

# Discover agents with specific capabilities
agents = client.discover_agents(
    capabilities=["translate"],
    trust_levels=[TrustLevel.VERIFIED, TrustLevel.PARTNER]
)

# Execute a task
result = client.execute_task(
    "translate",
    {
        "text": "Hello world",
        "source_language": "en",
        "target_language": "fr"
    }
)

print(result)  # "Bonjour le monde"
```

## Session Management

```python
from ars_client_with_sessions import ARSSessionClient

# Create session-aware client
client = ARSSessionClient(server_url="https://ars.example.com")

# Create a session
session, session_token = client.create_session(
    initial_data={
        "context": {
            "user": "user-123",
            "preferences": {
                "language": "en"
            }
        }
    }
)

# Execute task using session context
result = client.execute_task_with_session(
    "translate",
    {
        "text": "Hello world", 
        "target_language": "fr"
    },
    session_id=session.id
)

# Update session with new information
client.update_session(
    session.id,
    update_data={
        "context": {
            "history": [
                {
                    "task": "translate",
                    "input": {"text": "Hello world", "target_language": "fr"},
                    "output": "Bonjour le monde"
                }
            ]
        }
    }
)
```

## Features

- **Agent Registration**: Register agents with the ARS
- **Agent Discovery**: Find agents based on capabilities and trust levels
- **Trust Verification**: Verify agent identity and trust levels
- **Session Management**: Maintain stateful interactions between agents
- **Cross-Protocol Operation**: Work with agents across different protocols
- **Error Handling**: Comprehensive error handling and reporting

## Contributing

Contributions are welcome! Please see the main repository's CONTRIBUTING.md for guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
