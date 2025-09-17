#!/usr/bin/env python3
"""
Quick installation script for WithSecure Elements MCP Server.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_message(message, color="blue"):
    """Print a colored message."""
    colors = {
        "blue": "\033[94m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "end": "\033[0m"
    }
    print(f"{colors.get(color, colors['blue'])}[WithSecure Elements MCP]{colors['end']} {message}")


def check_python_version():
    """Check Python version."""
    if sys.version_info < (3, 8):
        print_message("Python 3.8 or higher is required", "red")
        sys.exit(1)
    print_message(f"Python {sys.version.split()[0]} detected ✓", "green")


def check_package_manager():
    """Check and recommend a package manager."""
    if subprocess.run(["uv", "--version"], capture_output=True).returncode == 0:
        print_message("uv detected ✓", "green")
        return "uv"
    elif subprocess.run(["pip", "--version"], capture_output=True).returncode == 0:
        print_message("pip detected ✓", "green")
        return "pip"
    else:
        print_message("No package manager detected", "red")
        print_message("Install pip or uv to continue", "yellow")
        sys.exit(1)


def install_package(manager):
    """Install the package."""
    print_message("Installing package...")
    
    if manager == "uv":
        try:
            subprocess.run(["uv", "tool", "install", "withsecure-elements-mcp"], check=True)
            print_message("Installation successful with uv ✓", "green")
        except subprocess.CalledProcessError:
            print_message("Installation failed with uv", "red")
            sys.exit(1)
    else:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "withsecure-elements-mcp"], check=True)
            print_message("Installation successful with pip ✓", "green")
        except subprocess.CalledProcessError:
            print_message("Installation failed with pip", "red")
            sys.exit(1)


def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print_message(".env file already exists ✓", "green")
        return
    
    if env_example.exists():
        env_file.write_text(env_example.read_text())
        print_message(".env file created from env.example", "yellow")
        print_message("Please edit .env with your WithSecure Elements information", "yellow")
    else:
        # Create a basic .env file
        env_content = """# WithSecure Elements API Configuration
WITHSECURE_CLIENT_ID=your_client_id
WITHSECURE_CLIENT_SECRET=your_client_secret
WITHSECURE_BASE_URL=https://api.connect.withsecure.com
WITHSECURE_ORGANIZATION_ID=your_organization_id

# MCP Server Configuration
MCP_DEBUG=false
MCP_LOG_LEVEL=INFO
WITHSECURE_MCP_MODULES=incidents,events,organizations,devices
"""
        env_file.write_text(env_content)
        print_message(".env file created", "yellow")
        print_message("Please edit .env with your WithSecure Elements information", "yellow")


def show_usage():
    """Show usage instructions."""
    print_message("Installation completed!", "green")
    print()
    print_message("Next steps:", "blue")
    print("1. Edit .env file with your WithSecure Elements information")
    print("2. Test the installation:")
    print("   withsecure-elements-mcp --help")
    print()
    print_message("Usage examples:", "blue")
    print("# stdio transport (default)")
    print("withsecure-elements-mcp")
    print()
    print("# SSE transport")
    print("withsecure-elements-mcp --transport sse --host 0.0.0.0 --port 8000")
    print()
    print("# HTTP transport")
    print("withsecure-elements-mcp --transport streamable-http --host 0.0.0.0 --port 8080")
    print()
    print("# Specific modules")
    print("withsecure-elements-mcp --modules incidents,events")
    print()
    print_message("Documentation:", "blue")
    print("- README.md : Usage guide")
    print("- DEVELOPMENT.md : Development guide")
    print("- SUPPORT.md : Support and troubleshooting")
    print("- examples/ : Usage examples")


def main():
    """Main function."""
    print_message("Installing WithSecure Elements MCP Server", "blue")
    print()
    
    # Checks
    check_python_version()
    manager = check_package_manager()
    
    # Installation
    install_package(manager)
    
    # Configuration
    create_env_file()
    
    # Instructions
    show_usage()


if __name__ == "__main__":
    main()
