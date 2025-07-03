ARG PYTHON_VERSION=3.12-slim-bookworm

FROM python:${PYTHON_VERSION}
#COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /code

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir uv && \
    /usr/local/bin/uv pip install --system -r requirements.txt

COPY . /code

ENV PATH="/usr/local/bin:$PATH"

ENV SECRET_KEY "Zj4WG8b2pVCmKHhaJNtLhobfbGTEEBaxuc1Vv4wneEnRpDiv1R"
ENV DEBUG "False"

# Install Node.js and npm
RUN apt-get update && apt-get install -y nodejs npm

# Build Vite assets
RUN npm install && npm run build

RUN python manage.py collectstatic --noinput && python manage.py makemigrations --noinput &&  \
    python manage.py migrate --noinput

EXPOSE 8000

CMD ["gunicorn","--bind",":8000","--workers","2","gourmet_wiki.wsgi"]
