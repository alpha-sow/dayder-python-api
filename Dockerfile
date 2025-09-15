FROM python:3.12-slim

WORKDIR /code

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock* /code/

# Configure Poetry: Don't create virtual environment, install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-root

COPY  ./app /code/app/

CMD ["fastapi", "run", "app/main.py", "--port", "80"]