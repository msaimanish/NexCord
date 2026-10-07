import asyncio

from mcp import Client


MCP_URL = "http://127.0.0.1:8001/mcp"


class NexCordMCPClient:
    def __init__(self, url: str = MCP_URL) -> None:
        self.url = url

    async def _call_async(
        self,
        tool_name: str,
        arguments: dict,
    ):
        async with Client(self.url) as client:
            result = await client.call_tool(
                tool_name,
                arguments,
            )

            return result

    def call(
        self,
        tool_name: str,
        arguments: dict,
    ):
        return asyncio.run(
            self._call_async(
                tool_name,
                arguments,
            )
        )