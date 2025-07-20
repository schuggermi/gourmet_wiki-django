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

ENV SECRET_KEY "Zj4WG8b2pVCmKHhaJNtLhobfbGTEEBaxuc1Vv4wneEnRpDiv1R"
ENV DEBUG "False"

# Install Node.js and npm
RUN apt-get update && apt-get install -y nodejs npm

# Build Vite assets
RUN npm install

RUN python manage.py collectstatic --noinput
