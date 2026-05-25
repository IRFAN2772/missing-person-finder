FROM python:3.10-slim

# Install system dependencies for dlib/face_recognition
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    && rm -rf /var/lib/apt/lists/*

# Speed up dlib compilation with parallel build
ENV CMAKE_BUILD_PARALLEL_LEVEL=4
ENV MAKEFLAGS="-j4"

# Create app directory
WORKDIR /app

# Create a non-root user (HF Spaces requirement)
RUN useradd -m -u 1000 appuser

# Install dlib first (heaviest step - cached separately)
RUN pip install --no-cache-dir cmake dlib

# Copy requirements and install remaining deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy app code
COPY . .

# Create directories with proper permissions
RUN mkdir -p /app/instance /app/static/uploads && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 7860 (Hugging Face Spaces requirement)
EXPOSE 7860

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "--timeout", "120", "app:create_app()"]
