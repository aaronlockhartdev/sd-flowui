FROM python:3.10 AS build1

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /usr/src/app
COPY ./backend ./backend
COPY requirements.txt LICENSE README.md ./
RUN pip install -U pip \
  && pip install wheel \
  && pip install -r requirements.txt

FROM node:19 AS build2

WORKDIR /usr/src/app
COPY ./frontend .
RUN npm install \
  && npm run build

FROM python:3.10 AS run

ENV VIRTUAL_ENV=/opt/venv
COPY --from=build1 /opt/venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV STATIC_DIR=/srv/www
COPY --from=build2 /usr/src/app/dist $STATIC_DIR

EXPOSE 80

WORKDIR /app 
COPY ./app.py .
ENTRYPOINT [ "uvicorn", "app:app"]
CMD ["--host", "0.0.0.0", "--port", "80"]