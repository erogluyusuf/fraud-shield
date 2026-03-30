from typing import Any
import redis
import json
import asyncio
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

r = redis.Redis(host='redis', port=6379, decode_responses=True)

server = Server("fraud-shield-mcp")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="check_user_status",
            description="Belirli bir kullanicinin islem gecmisini ve risk durumunu getirir.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"}
                },
                "required": ["user_id"],
            },
        ),
        types.Tool(
            name="get_recent_frauds",
            description="Sistemdeki son supheli (fraud) islemleri listeler.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if name == "check_user_status":
        user_id = arguments.get("user_id")
        amounts = r.lrange(f"user:{user_id}:amounts", 0, -1)
        last_loc = r.get(f"user:{user_id}:last_loc")
        
        status_data = {
            "user_id": user_id,
            "recent_amounts": amounts,
            "last_known_location": last_loc,
            "risk_assessment": "YUKSEK" if amounts and len(amounts) > 3 else "NORMAL"
        }
        
        return [
            types.TextContent(
                type="text",
                text=json.dumps(status_data, indent=2)
            )
        ]
        
    elif name == "get_recent_frauds":
        return [
            types.TextContent(
                type="text",
                text="Not: MCP calisiyor. Canli fraud loglari worker tarafindan islenmektedir."
            )
        ]

    raise ValueError(f"Bilinmeyen arac: {name}")

async def main():
    options = InitializationOptions(
        server_name="fraud-shield-mcp",
        server_version="0.1.0",
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            options
        )

if __name__ == "__main__":
    asyncio.run(main())
