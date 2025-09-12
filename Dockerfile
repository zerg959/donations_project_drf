# Dockerfile
FROM python:3.11-slim

# Sys dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Work dir
WORKDIR /app

# Copy dependencies file
COPY requirements.txt .

# Install Python packages from dependencies list
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files (except ignored files)
COPY . .

# Create extra floders
RUN mkdir db

# App port
EXPOSE 8000

# Run dev-server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
