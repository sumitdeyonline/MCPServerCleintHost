import streamlit as st
import asyncio
import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI

from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

# --- Configuration ---
load_dotenv()
# When deployed, explicitly set SSE_URL in Streamlit's environment to the Cloud Run server URL
SSE_URL = os.getenv("SSE_URL", "http://127.0.0.1:8000/sse")

st.set_page_config(page_title="Retail AI Agent", page_icon="🤖")
st.title("🛒 Agentic Retail Assistant")

# Basic auth check and strip trailing newlines (often caused by copy-pasting into terminal)
raw_api_key = os.getenv("OPENAI_API_KEY", "").strip()
if not raw_api_key:
    st.error("Missing OPENAI_API_KEY in your .env file! Please add it and refresh.")
    st.stop()

# Initialize OpenAI Client explicitly with the cleaned key
aclient = AsyncOpenAI(api_key=raw_api_key)

# Initialize Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render UI Chat History
for msg in st.session_state.messages:
    role = msg.get("role")
    
    # Hide raw tool execution messages from the UI
    if role == "tool":
        continue
    
    # If standard user/assistant message
    with st.chat_message(role):
        # The AI sometimes returns a tool request object before the actual content
        if msg.get("content"):
            st.markdown(msg["content"])
        elif msg.get("tool_calls"):
            st.markdown("*[System: Invoking Retail Tool...]*")

def mcp_to_openai_schema(mcp_tool):
    """Converts a FastMCP tool schema into standard OpenAI tool specification."""
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": mcp_tool.description,
            "parameters": mcp_tool.inputSchema
        }
    }

async def display_and_process_prompt(prompt: str):
    # 1. Store and display user input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Main Logic Block
    try:
        # Establish connection to your running FastMCP SSE Microservice!
        # Increased timeout to 60 because Cloud Run cold-starts often take ~10 seconds.
        async with sse_client(SSE_URL, timeout=60.0) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                
                # Fetch live tools from your server
                mcp_tools_response = await session.list_tools()
                openai_formatted_tools = [mcp_to_openai_schema(t) for t in mcp_tools_response.tools]

                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    
                    with st.spinner("Analyzing request and determining tool constraints..."):
                        # Send context + tools to OpenAI
                        completion = await aclient.chat.completions.create(
                            model="gpt-4o",
                            messages=st.session_state.messages,
                            tools=openai_formatted_tools
                        )

                    response_message = completion.choices[0].message
                    # Save AI state to conversational history
                    st.session_state.messages.append(response_message.model_dump(exclude_none=True))

                    # 3. Handle Tool Executions natively supporting recursive parallel actions
                    while response_message.tool_calls:
                        for tool_call in response_message.tool_calls:
                            tool_name = tool_call.function.name
                            tool_args = json.loads(tool_call.function.arguments)
                            
                            st.info(f"🛠️ Agent Executing Server Tool: `{tool_name}(**{tool_args})`")

                            # Dispatch execution to the MCP Backend using SSE remotely
                            result = await session.call_tool(tool_name, arguments=tool_args)
                            
                            # Parse result content intelligently tracking MCP internal syntax structures
                            tool_output_val = "Success"
                            if result.isError:
                                tool_output_val = f"Error: {result.content}"
                            elif result.content:
                                tool_output_val = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content)
                            
                            # Append tool response perfectly formatted for GPT-4 rules
                            st.session_state.messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": str(tool_output_val)
                            })

                        # Immediately re-query OpenAI passing along the results of the tool execution
                        with st.spinner("Synthesizing answer from database response..."):
                            completion = await aclient.chat.completions.create(
                                model="gpt-4o",
                                messages=st.session_state.messages,
                                tools=openai_formatted_tools
                            )
                            response_message = completion.choices[0].message
                            st.session_state.messages.append(response_message.model_dump(exclude_none=True))

                    # Direct response finalized output
                    if response_message.content:
                        response_placeholder.markdown(response_message.content)
                            
    except Exception as e:
        import traceback
        traceback.print_exc()
        st.error(f"⚠️ Communication Error with MCP Backend or OpenAI: {str(e)}")
        st.caption("Review your terminal logs for the deep Python stacktrace.")


# Streamlit Execution Loop Trigger
if prompt := st.chat_input("E.g., What is the stock level for P1002?"):
    # Streamlit is strictly synchronous normally, so we bridge to Asyncio here
    asyncio.run(display_and_process_prompt(prompt))
