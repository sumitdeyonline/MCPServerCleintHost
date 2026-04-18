FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen || uv pip install -r pyproject.toml --system

COPY . .

# Default Streamlit Port
ENV PORT=8501
EXPOSE $PORT

# Cloud Run deployment requires passing the dynamic PORT given by Google
# Using shell-form CMD ensures ${PORT} variable is correctly unpacked as an integer instead of a literal string!
CMD uv run streamlit run src/client.py --server.port=${PORT} --server.address=0.0.0.0
