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
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

RUN npm install
RUN npm run build

RUN python manage.py collectstatic --noinput && python manage.py makemigrations --noinput &&  \
    python manage.py migrate --noinput
