# Dockerfile for WithSecure Elements MCP Server

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r withsecure && useradd -r -g withsecure withsecure

# Create working directory
WORKDIR /app

# Copy configuration files
COPY pyproject.toml ./
COPY README.md ./
COPY LICENSE ./

# Install package
RUN pip install --no-cache-dir -e .

# Change file ownership
RUN chown -R withsecure:withsecure /app

# Switch to non-root user
USER withsecure

# Expose default port
EXPOSE 8000

# Default environment variables
ENV MCP_DEBUG=false
ENV MCP_LOG_LEVEL=INFO
ENV WITHSECURE_MCP_MODULES=incidents,events,organizations,devices

# Default entrypoint
ENTRYPOINT ["withsecure-elements-mcp"]

# Default arguments
CMD ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]
