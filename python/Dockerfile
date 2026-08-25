FROM python:3.12.1
SHELL ["/bin/bash", "-c"]
WORKDIR /workspace

# Install vim (and update apt cache first)
RUN apt-get update \
    && apt-get install -y --no-install-recommends vim \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /workspace/venv

# Activate venv by putting it first on PATH
ENV PATH="/workspace/venv/bin:$PATH"

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .
COPY . .
