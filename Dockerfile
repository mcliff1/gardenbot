FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application code
COPY src/ src/
COPY static/ static/
COPY templates/ templates/
COPY data/ data/

EXPOSE 8000

CMD ["uvicorn", "gardenbot.main:app", "--host", "0.0.0.0", "--port", "8000"]
