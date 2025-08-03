#ARG PYTHON_VERSION=3.12-slim-bookworm
#
#FROM python:${PYTHON_VERSION}
#
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1
#
#RUN mkdir -p /app
#
#WORKDIR /app
#
#COPY requirements.txt /app
#
#RUN pip install --no-cache-dir --upgrade pip && \
#    pip install --no-cache-dir uv && \
#    /usr/local/bin/uv pip install --system -r requirements.txt
#
#COPY . /app
#
#ENV PATH="/usr/local/bin:$PATH"
#
#RUN apt-get update && apt-get install -y \
#    curl \
#    gnupg \
#    ca-certificates && \
#    gettext && \
#    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
#    apt-get install -y nodejs
#
#RUN npm install
#
#COPY entrypoint.sh /app/
#
#RUN chmod +x /app/entrypoint.sh
#
#ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it.sh
#RUN chmod +x /usr/local/bin/wait-for-it.sh
#
#ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]


ARG PYTHON_VERSION=3.12-slim-bookworm

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    curl \
    gnupg \
    ca-certificates \
    gettext \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Download and install uv into /usr/local/bin (robust)
RUN curl -LsSf -o uv.tar.gz https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz && \
    mkdir -p /tmp/uv && \
    tar -xzf uv.tar.gz -C /tmp/uv && \
    find /tmp/uv -name uv -type f -exec mv {} /usr/local/bin/uv \; && \
    chmod +x /usr/local/bin/uv && \
    rm -rf /tmp/uv uv.tar.gz

# Confirm uv is available
RUN uv --version

# Set up work directory
RUN mkdir -p /app
WORKDIR /app

# Copy and install Python dependencies using uv
COPY requirements.txt /app
RUN uv pip install --system -r requirements.txt

# Copy rest of the app
COPY . /app

# Install Node dependencies
RUN npm install

# Add wait-for-it script
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Copy and set entrypoint
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
