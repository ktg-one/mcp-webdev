"""
FastMCP 3 Webdev Gateway
Project-only servers not available in global gateway.

Servers: figma, vercel, in-memoria, next-devtools, serena
"""

import os
import sys
from pathlib import Path
from fastmcp import FastMCP
from fastmcp.client.transports import (
    NpxStdioTransport,
    UvxStdioTransport,
)
from fastmcp.server import create_proxy
from dotenv import load_dotenv

MCP_ROOT = Path(__file__).parent
load_dotenv(MCP_ROOT / ".env")

gateway = FastMCP("webdev-gateway")


def mount(name: str, transport):
    """Mount a stdio sub-server as a proxy, skip on failure."""
    try:
        proxy = create_proxy(transport, name=name)
        gateway.mount(proxy, namespace=name)
        print(f"  ✓ {name}", file=sys.stderr)
    except Exception as e:
        print(f"  ✗ {name}: {e}", file=sys.stderr)


print("Mounting webdev servers...", file=sys.stderr)

# 1. Figma design-to-code
mount("figma", NpxStdioTransport(
    package="figma-developer-mcp",
    env_vars={"FIGMA_API_KEY": os.getenv("FIGMA_API_KEY", "")},
))

# 2. Vercel deploy
mount("vercel", NpxStdioTransport(
    package="@vercel/mcp-adapter",
    env_vars={"VERCEL_API_KEY": os.getenv("VERCEL_API_KEY", "")},
))

# 3. Session memory
mount("in-memoria", NpxStdioTransport(
    package="in-memoria",
))

# 4. Next.js devtools
mount("next-devtools", NpxStdioTransport(
    package="next-devtools-mcp@latest",
))

# 5. Code navigation (project-specific)
mount("serena", UvxStdioTransport(
    tool_name="serena",
    from_package="git+https://github.com/oraios/serena",
    tool_args=["start-mcp-server", "--context", "claude-code"],
))

if __name__ == "__main__":
    if "--http" in sys.argv:
        gateway.run(transport="http", host="0.0.0.0", port=8788)
    else:
        gateway.run()
