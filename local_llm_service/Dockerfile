FROM python:3.9-slim

WORKDIR /app

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

# Create directory for model files
RUN mkdir -p /app/models

# Expose the port the app will run on
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "app.main"] 