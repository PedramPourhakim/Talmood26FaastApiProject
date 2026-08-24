#FROM python:3.14.5-alpine
#
#WORKDIR /usr/src/core
#
#COPY ./requirements.txt .
#
#RUN apk add --no-cache gcc musl-dev libffi-dev \
#    && pip install --no-cache-dir --upgrade -r ./requirements.txt \
#    && apk del gcc musl-dev libffi-dev \
#
#COPY ./app .
#
## set up an entrypoint script
#COPY entrypoint.sh /entrypoint.sh
#RUN chmod +x /entrypoint.sh
#
#ENTRYPOINT ["/entrypoint.sh"]

# ==========================================
# Stage 1: Frontend Build
# ==========================================
FROM node:22-alpine AS frontend

WORKDIR /frontend

COPY package.json package-lock.json ./

RUN npm ci

COPY app ./app
COPY static ./static
COPY vite.config.js .
COPY tailwind.config.js .

RUN npm run tailwind:build
RUN npm run build


# ==========================================
# Stage 2: Backend
# ==========================================
FROM python:3.14.5-slim

WORKDIR /usr/src/core

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY app ./app
COPY static ./static

COPY --from=frontend \
    /frontend/static/css/output.css \
    ./static/css/output.css

COPY --from=frontend \
    /frontend/static/dist \
    ./static/dist

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]

# FROM python:3.14.5-slim

# WORKDIR /usr/src/core

# COPY ./requirements.txt .

# RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# CMD ["fastapi","run","--host","0.0.0.0","--port","80"]

# COPY ./app .


# docker build -t myimage .
# docker run -d --name mycontainer -p 8000:8000 myimage
# docker pull docker.arvancloud.ir/python:3.14.5-slim

