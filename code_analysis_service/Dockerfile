FROM python:3.9-slim

WORKDIR /app

# Install git for repository cloning
RUN apt-get update && apt-get install -y git && apt-get clean

# Install Poetry
RUN pip install poetry==1.6.1

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* /app/

# Configure poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY . /app/

# Create directory for repositories
RUN mkdir -p /app/repos

# Expose the port the app will run on
EXPOSE 8002

# Command to run the application
CMD ["python", "-m", "app.main"] 