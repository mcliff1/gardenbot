FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir .

# Copy frontend assets
COPY static/ static/
COPY templates/ templates/
COPY data/ data/

EXPOSE 8000

CMD ["uvicorn", "gardenbot.main:app", "--host", "0.0.0.0", "--port", "8000"]
