import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

async def main():
    try:
        url = "https://mcp-server-351454544171.us-central1.run.app/sse"
        print(f"Connecting to {url}...")
        async with sse_client(url, timeout=60.0) as streams:
            print("Connected! Initializing session...")
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("Success! Fetching tools...")
                tools = await session.list_tools()
                print(f"Available tools: {[t.name for t in tools.tools]}")
                
                print("\nCalling tool check_inventory...")
                result = await session.call_tool("check_inventory", arguments={"product_id": "P1002"})
                print("Result Object:", result)
                print("Result Content:", result.content)
    except Exception as e:
        import traceback
        print("EXCEPTION CAUGHT:", repr(e))
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
