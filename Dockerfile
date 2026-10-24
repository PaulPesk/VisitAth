FROM python:3.12-slim

WORKDIR /app

COPY api_requirements.txt .
RUN pip install --no-cache-dir -r api_requirements.txt

COPY pyproject.toml .
COPY src ./src
RUN pip install --no-cache-dir -e .

ENV OLLAMA_HOST=http://host.docker.internal:11434

EXPOSE 8000
CMD ["uvicorn", "visitath.api.main:app", "--host", "0.0.0.0", "--port", "8000"]