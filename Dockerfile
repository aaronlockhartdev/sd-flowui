# Backend build stage
FROM python:3.10-bullseye AS build1
SHELL ["/bin/bash", "-c"]

# Create venv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install only dependencies to prevent cache invalidation
WORKDIR /usr/src/app
ENV FLIT_ROOT_INSTALL=1
COPY requirements.txt .
COPY backend/pyproject.toml backend/
COPY backend/src/api/__init__.py backend/src/api/
RUN --mount=type=cache,target=/root/.cache \
  pip install -U pip \
    && pip install wheel \
    && pip install flit \
    && flit -f backend/pyproject.toml install --only-deps \
    && pip install -r <(grep -v backend/. requirements.txt)

# Install backend module
COPY backend backend
RUN pip install backend/.

# Frontend build stage
FROM node:current-alpine AS build2

# Install only dependencies to prevent cache invalidation
WORKDIR /usr/src/app
COPY frontend/package.json frontend/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
  npm install

# Build static html files
COPY frontend .
RUN npm run build

# Web server execution
FROM python:3.10-bullseye AS run

# Copy python venv
ENV VIRTUAL_ENV=/opt/venv
COPY --from=build1 /opt/venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy static html files
ENV STATIC_DIR=/srv/www
COPY --from=build2 /usr/src/app/dist $STATIC_DIR

# Enforce production environment
ENV API_ENV=production

# Expose port
EXPOSE 80

# Run web server
WORKDIR /app 
COPY app.py .
ENTRYPOINT [ "uvicorn", "app:app"]
CMD ["--host", "0.0.0.0", "--port", "80"]