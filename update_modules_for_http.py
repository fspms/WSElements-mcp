#!/usr/bin/env python3
"""
Script to update all MCP modules to support HTTP transport.
"""

import os
import re
from pathlib import Path

def update_module_file(file_path):
    """Update a module file to support HTTP transport."""
    print(f"Updating {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already updated
    if 'self._tools.extend([' in content:
        print(f"  {file_path} already updated, skipping...")
        return
    
    # Add resources to HTTP list
    resources_pattern = r'(def _register_resources\(self\) -> None:\s*"""Register resources for [^"]*"""\.\s*)(\s*@self\.server\.list_resources\(\))'
    resources_replacement = r'\1# Add resources to the list for HTTP transport\n        self._resources.append({\n            "uri": "withsecure://\1",\n            "name": "\1",\n            "description": "WithSecure Elements \1 list",\n            "mimeType": "application/json"\n        })\n        \n        \2'
    
    # This is a simplified approach - we'll need to manually handle each module
    print(f"  {file_path} needs manual update")
    return content

def main():
    """Update all module files."""
    modules_dir = Path("withsecure_elements_mcp/modules")
    
    for module_file in modules_dir.glob("*.py"):
        if module_file.name in ["__init__.py", "base.py"]:
            continue
        
        update_module_file(module_file)

if __name__ == "__main__":
    main()
