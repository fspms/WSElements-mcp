# Support - WithSecure Elements MCP

This document provides information about support and troubleshooting for the WithSecure Elements MCP server.

## Getting Help

### Documentation

1. **README.md** - Installation and basic usage guide
2. **DEVELOPMENT.md** - Development and contribution guide
3. **Examples** - `examples/` directory with usage examples
4. **WithSecure Elements API** - [Official documentation](https://api.connect.withsecure.com)

### Common Issues

#### Authentication Errors

**Issue**: `Authentication failed: 401 - Unauthorized`

**Solutions**:
- Check that `WITHSECURE_CLIENT_ID` and `WITHSECURE_CLIENT_SECRET` are correct
- Ensure credentials have appropriate permissions
- Verify base URL matches your environment

**Issue**: `Authorization header is missing`

**Solutions**:
- Check that User-Agent is set correctly
- Ensure HTTP headers are properly formed

#### Configuration Errors

**Issue**: `Module 'module_name' not recognized`

**Solutions**:
- Check that module name is correct (incidents, events, organizations, devices)
- Ensure module is available in supported modules list

**Issue**: `WITHSECURE_CLIENT_ID and WITHSECURE_CLIENT_SECRET must be defined`

**Solutions**:
- Create `.env` file based on `env.example`
- Set required environment variables
- Restart the server

#### Network Errors

**Issue**: `Error retrieving data: 500 - Internal Server Error`

**Solutions**:
- Check network connectivity
- Verify WithSecure Elements API is accessible
- Check logs for more details

**Issue**: `Request timeout`

**Solutions**:
- Increase timeout in configuration
- Check network connection stability
- Contact WithSecure support if issue persists

### Debugging

#### Enable Debug Logs

```bash
# Via environment variable
export MCP_DEBUG=true
export MCP_LOG_LEVEL=DEBUG

# Via command line argument
withsecure-elements-mcp --debug
```

#### Docker Logs

```bash
# View container logs
docker logs withsecure-elements-mcp

# Follow logs in real-time
docker logs -f withsecure-elements-mcp

# Logs with timestamps
docker logs -t withsecure-elements-mcp
```

#### Docker Compose Logs

```bash
# View logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# Logs for specific service
docker-compose logs withsecure-elements-mcp
```

### Connectivity Tests

#### Authentication Test

```python
from withsecure_elements_mcp.auth import WithSecureAuth
from withsecure_elements_mcp.config import WithSecureConfig

config = WithSecureConfig(
    client_id="your_client_id",
    client_secret="your_client_secret",
    base_url="https://api.connect.withsecure.com"
)

async def test_auth():
    async with WithSecureAuth(config) as auth:
        try:
            token = await auth.get_token()
            print(f"Authentication successful: {token[:10]}...")
        except Exception as e:
            print(f"Authentication error: {e}")

import asyncio
asyncio.run(test_auth())
```

#### API Test

```bash
# Test with curl
curl -X POST \
  -H "User-Agent: WithSecure-Elements-MCP/0.1.1" \
  -u "your_client_id:your_client_secret" \
  -d "grant_type=client_credentials&scope=connect.api.read connect.api.write" \
  https://api.connect.withsecure.com/as/token.oauth2
```

### Performance

#### Query Optimization

- Use appropriate filters to limit results
- Paginate large lists with `limit` parameter
- Use date parameters to limit data range

#### Monitoring

- Monitor memory usage
- Monitor API response times
- Monitor errors in logs

### Limits and Constraints

#### WithSecure Elements API Limits

- Rate limiting based on your plan
- Pagination limits (usually 100 items per page)
- Authentication token timeout (usually 1 hour)

#### MCP Server Limits

- Memory: depends on retrieved data size
- Concurrent connections: limited by HTTP configuration
- Response size: limited by available memory

### Updates

#### Package Update

```bash
# With uv
uv tool upgrade withsecure-elements-mcp

# With pip
pip install --upgrade withsecure-elements-mcp
```

#### Docker Update

```bash
# Rebuild image
docker build -t withsecure-elements-mcp .

# Or pull latest version
docker pull withsecure-elements-mcp:latest
```

### Community Support

#### GitHub Issues

- [Create an issue](https://github.com/withsecure/elements-mcp/issues)
- Search existing issues
- Provide detailed information about the problem

#### Discussions

- [GitHub Discussions](https://github.com/withsecure/elements-mcp/discussions)
- General questions and suggestions
- Experience sharing

### Commercial Support

For commercial support or questions about WithSecure Elements API:

- [WithSecure Support](https://www.withsecure.com/en/support)
- Official API documentation
- Dedicated technical support

### Contributing

#### Report a Bug

1. Check that the bug hasn't already been reported
2. Create an issue with:
   - Detailed problem description
   - Steps to reproduce
   - Error logs
   - Configuration used
   - Package version

#### Suggest an Enhancement

1. Create an issue with "enhancement" label
2. Describe the proposed enhancement
3. Explain why it would be useful
4. Propose an implementation if possible

#### Contribute Code

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Create a Pull Request

### Version Information

- **Current version**: 0.1.1
- **Python**: 3.8+
- **Dependencies**: See `pyproject.toml`
- **License**: MIT

### Version History

See [CHANGELOG.md](CHANGELOG.md) for complete version history.
