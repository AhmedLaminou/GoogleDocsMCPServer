FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml README.md LICENSE server.json ./
COPY google_docs_mcp_server ./google_docs_mcp_server
COPY docs ./docs
RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn google_docs_mcp_server.app:app --host 0.0.0.0 --port ${PORT}"]
