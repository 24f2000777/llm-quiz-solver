FROM python:3.12-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates curl unzip \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon0 \
    libgtk-3-0 libgbm1 libasound2 libxcomposite1 libxdamage1 libxrandr2 \
    libxfixes3 libpango-1.0-0 libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and Chromium
RUN pip install --no-cache-dir playwright && \
    playwright install --with-deps chromium

# Install uv for fast package management
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Environment settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Install dependencies using uv
RUN uv pip install --system -e .

# Expose port for HuggingFace Spaces
EXPOSE 7860

# Run the application
CMD ["python", "main.py"]
