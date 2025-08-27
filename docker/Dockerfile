FROM python:3.10-bullseye

ARG ARG_MODULE=""
ARG APP_PORT=""
ARG APP_MODEL_URL=""
ARG APP_MODEL_BATCH_SIZE=""
ARG USE_GPU=""
ARG ARG_MAX_QUEUE_SIZE=512
ARG ARG_TF_USE_LEGACY_KERAS=""

ENV MODULE=$ARG_MODULE
ENV APP_PORT=$APP_PORT
ENV APP_MODEL_URL=$APP_MODEL_URL
ENV APP_MODEL_BATCH_SIZE=$APP_MODEL_BATCH_SIZE
ENV MAX_QUEUE_SIZE=$ARG_MAX_QUEUE_SIZE
ENV TF_USE_LEGACY_KERAS=$ARG_TF_USE_LEGACY_KERAS

ENV CUDA_VISIBLE_DEVICES=$USE_GPU

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /app

COPY module/ /app/module/
COPY main.py /app/main.py
COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt
RUN pip install -r /app/module/requirements.txt

EXPOSE $APP_PORT

CMD uvicorn main:app --host 0.0.0.0 --port $APP_PORT --workers 1 --backlog $MAX_QUEUE_SIZE