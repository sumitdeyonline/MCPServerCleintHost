# Cloud Deployment Guide

This document outlines the exact procedure for securely containerizing and deploying the Retail MCP System to **Google Cloud Run**.

## The Architecture
The infrastructure utilizes two independent, fully-managed Google Cloud Run instances:
1. **mcp-server**: The FastMCP backend service operating via Python server-sent events (SSE).
2. **mcp-ui**: The frontend Streamlit UI interpreting logic loops between OpenAI and the backend system.

### Containerization Strategy
To deploy precisely, this project relies on two customized Docker configurations (`Dockerfile.backend` and `Dockerfile.frontend`). Google Cloud Run's strict continuous integration tools typically search for a single file simply named `Dockerfile`. Therefore, during deployment, we temporarily copy the specific service configuration into a primary `Dockerfile` to enforce successful builds and avoid "Buildpack" errors.

---

## Deployment Steps

### 1. Deploy the Backend (FastMCP Server)
Ensure your Firebase credentials are ready.

1. Swap the Docker configurations to prioritize the backend:
   ```bash
   cp Dockerfile.backend Dockerfile
   ```

2. Push the code to Google Cloud Run:
   ```bash
   gcloud run deploy mcp-server \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars FIREBASE_CREDENTIALS_PATH="./firebase-key.json"
   ```
   > **Note on Safety:** For production, it is highly recommended to store your `firebase-key.json` contents as a Secret inside **Google Cloud Secret Manager** and mount it via `--set-secrets` rather than baking the physical credential file inside the system.
   
3. **Save your URL:** Wait for the deployment to finish, and copy the `Service URL` (e.g., `https://mcp-server-12345.a.run.app`).

---

### 2. Deploy the Frontend (Streamlit Client)
Now that the backend is live, you must bridge the UI to it over the internet.

1. Swap the Docker configurations to prioritize the frontend:
   ```bash
   cp Dockerfile.frontend Dockerfile
   ```

2. Point the UI securely at the Backend utilizing the `SSE_URL` injection, and authenticate your LLM Agent using `OPENAI_API_KEY`:
   ```bash
   gcloud run deploy mcp-ui \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars OPENAI_API_KEY="sk-YOUR-API-KEY" \
     --set-env-vars SSE_URL="https://mcp-server-12345.a.run.app/sse"
   ```
   > **Critical Details:** 
   > - Make sure you append `/sse` precisely to the end of the URL you received in step 1.
   > - The Frontend's internal timeout has been configured to **60 seconds** to tolerate Google Cloud "Cold Starts".

Once the sequence completes, your live AI application URL will be officially provided in the terminal output!
