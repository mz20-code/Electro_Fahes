# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13.7
FROM python:${PYTHON_VERSION}-slim

LABEL fly_launch_runtime="flask"

# Set working directory (match Fly's default /code)
WORKDIR /code

# Copy only requirements first for caching
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose port for Flask
EXPOSE 8080

# Set environment variable for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080

# Run Flask
CMD ["flask", "run"]
