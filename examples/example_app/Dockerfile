FROM python:3.14-slim
WORKDIR /app

# Install system dependencies required for psycopg2 and other C extensions
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --upgrade pip
# Set. poetry version
ENV POETRY_VERSION=1.8.3
RUN pip install "poetry==$POETRY_VERSION"

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]
