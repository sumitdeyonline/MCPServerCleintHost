# Agentic Retail MCP System

A full-stack artificial intelligence application implementing a Model Context Protocol (MCP) server securely attached to a Firebase Firestore database, controlled via a Streamlit Chat interface and powered by OpenAI's `gpt-4o`.

## System Architecture

This project is built using a decoupled Microservice pattern:
1. **MCP Backend Server (`src/server.py`)**: A `fastmcp` Python server exposing Retail-specific tools `['check_inventory', 'calculate_elasticity', 'get_demand_forecast']`. Connects directly to Google Cloud Firestore.
2. **AI Streamlit Frontend (`src/client.py`)**: An asynchronous Web UI that communicates with your Backend Server using persistent `Server-Sent Events` (SSE). Parses tool inputs and loops them dynamically into OpenAI Function calls.

## Prerequisites & Configuration

Before running any scripts, you must configure your `.env` file at the root of the project.

Create a `.env` file and define the following variables:
```properties
# Your OpenAI API Key for the GPT-4o Agent
OPENAI_API_KEY="sk-proj-YOUR-KEY-HERE"

# The absolute path to your Firebase Service Account JSON key
FIREBASE_CREDENTIALS_PATH="./firebase-key.json"
```
*(If `FIREBASE_CREDENTIALS_PATH` is left blank, the system will attempt to utilize Google Cloud's Application Default Credentials natively).*

## Installation

This project utilizes `uv` as the lightning-fast python package dependency manager. 

Run the following inside the root directory to ensure dependencies are mapped to Python >= 3.11:
```bash
uv init
uv add mcp pydantic firebase-admin python-dotenv openai streamlit
```

## Database Initialization (Mock Data)

If you have a fresh Firebase Firestore instance, you can use the built-in seeding tools to populate your database with 100 sample retail products.

1. Generate the static CSV mock data structures:
   ```bash
   uv run python generate_data.py
   ```
2. Stream the generated CSV data directly into your Firebase NoSQL Database:
   ```bash
   uv run python seed_db.py
   ```

## Running the Application

Because the Web Interface and the Tool Server communicate over an isolated local network loop, **you must run both processes parallelly in two separate terminal tabs.**

### 1. Boot up the Backend Tool Server
This stands up an ASGI Uvicorn app on port 8000 handling all tool execution requests natively via HTTP Server Sent Events.
```bash
uv run python src/server.py
```

### 2. Boot up the Streamlit Client
In a new terminal window, start the Streamlit conversational agent:
```bash
uv run streamlit run src/client.py 
```
A web browser tab will automatically open at `http://localhost:8501`. You can now ask questions like *"What is the stock level of product P1002?"* or *"Analyze pricing elasticity projections for P1100"*.

## Cloud Deployments (Google Cloud Run)
If you want to move your AI Agent and Backend infrastructure permanently to the cloud, I have configured advanced Dockerfiles designed explicitly for serverless deployment on Google Cloud Run. 

Please refer to the complete **[`DEPLOYMENT.md`](DEPLOYMENT.md)** documentation guide for instructions on pushing both containers to the web.
