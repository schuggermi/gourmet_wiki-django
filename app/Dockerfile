ARG PYTHON_VERSION=3.12-slim-bookworm

FROM python:${PYTHON_VERSION}
#COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /app

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir uv && \
    /usr/local/bin/uv pip install --system -r requirements.txt

COPY . /app

ENV PATH="/usr/local/bin:$PATH"

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

RUN npm install && npm run build

RUN chmod +x /app/entrypoint.sh

ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
