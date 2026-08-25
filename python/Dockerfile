FROM python:3.12
SHELL ["/bin/bash", "-c"]
WORKDIR /workspace

# Create virtual environment
RUN python -m venv /workspace/venv

# Activate venv by putting it first on PATH
ENV PATH="/workspace/venv/bin:$PATH"

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

COPY . .
