FROM python:3.10-slim


# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy pyproject.toml and install dependencies
COPY pyproject.toml .
COPY requirements.txt .

RUN uv pip install --system --no-cache --requirements requirements.txt
RUN apt-get update && apt-get install -y sqlite3

# Copy source code
COPY . .


# Start FastAPI app or scheduler depending on the image
CMD ["python", "app.py"]
