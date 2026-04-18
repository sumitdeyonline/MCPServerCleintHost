from mcp.server.fastmcp import FastMCP
mcp = FastMCP("test")
if __name__ == "__main__": mcp.run(transport="sse")
