#!/bin/bash

# Startup script for WithSecure Elements MCP Server

set -e

# Colors for messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display messages
print_message() {
    echo -e "${BLUE}[WithSecure Elements MCP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[WithSecure Elements MCP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WithSecure Elements MCP]${NC} $1"
}

print_error() {
    echo -e "${RED}[WithSecure Elements MCP]${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from env.example..."
    if [ -f "env.example" ]; then
        cp env.example .env
        print_warning "Please edit .env file with your WithSecure Elements information"
        exit 1
    else
        print_error "env.example file not found"
        exit 1
    fi
fi

# Check required environment variables
source .env

if [ -z "$WITHSECURE_CLIENT_ID" ] || [ -z "$WITHSECURE_CLIENT_SECRET" ]; then
    print_error "WITHSECURE_CLIENT_ID and WITHSECURE_CLIENT_SECRET must be defined in .env"
    exit 1
fi

# Default parameters
TRANSPORT=${1:-"stdio"}
HOST=${2:-"localhost"}
PORT=${3:-"8000"}
MODULES=${4:-"incidents,events,organizations,devices"}

print_message "Starting WithSecure Elements MCP server..."
print_message "Transport: $TRANSPORT"
print_message "Host: $HOST"
print_message "Port: $PORT"
print_message "Modules: $MODULES"

# Build arguments
ARGS="--transport $TRANSPORT"

if [ "$TRANSPORT" != "stdio" ]; then
    ARGS="$ARGS --host $HOST --port $PORT"
fi

if [ -n "$MODULES" ]; then
    ARGS="$ARGS --modules $MODULES"
fi

# Start server
print_success "Launching server..."
exec withsecure-elements-mcp $ARGS
