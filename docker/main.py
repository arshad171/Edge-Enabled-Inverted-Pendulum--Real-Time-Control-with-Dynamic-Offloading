import os
import uuid
import asyncio
import gc
import importlib
import time
import numpy as np
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
import setproctitle

from module.model import Model

if os.environ.get("PROC_TITLE", None) is not None:
    setproctitle.setproctitle(str(os.environ.get("PROC_TITLE")))

UID = uuid.uuid4()

port = 8000

MAX_QUEUE_SIZE = int(os.environ["MAX_QUEUE_SIZE"])
MODEL_URL: str = os.environ["APP_MODEL_URL"]
request_queue = asyncio.Queue()

app = FastAPI()
# Instrumentator().instrument(app).expose(app)
semaphore = asyncio.Semaphore(1)

service_times = []
arrivals = []
departures = []
queueing_times = []
iats = []
queue_lens = []


@app.middleware("http")
async def limit_concurrency(request: Request, call_next):
    queue_lens.append(request_queue.qsize())

    if request_queue.qsize() >= MAX_QUEUE_SIZE:
        print(f"queue saturated")
        raise HTTPException(
            status_code=429, detail="service queue is saturated, try later :( "
        )

    t_arrival = time.time()
    if request.url.path == "/flush":
        global semaphore

        res = await call_next(request)
        semaphore = asyncio.Semaphore(1)

        return res

    else:
        await request_queue.put(request)
        arrivals.append(t_arrival)

        # lock
        async with semaphore:
            try:
                await request_queue.get()
                t_wait = time.time()

                queueing_times.append(t_wait - t_arrival)

                response = await call_next(request)
                t_completion = time.time()

                departures.append(t_completion)
            except asyncio.CancelledError as e:
                print("*** task cancelled error")
                print(request, call_next)
        return response


async def flush_queue():
    while not request_queue.empty():
        try:
            print("*** flushing queue")
            request_queue.get_nowait()
            request_queue.task_done()
        except asyncio.QueueEmpty:
            break


# model = MLModel()

# model_lib = importlib.import_module("module.model")
# model = model_lib.Model()
model = Model()

last_arrival = None

RESPONSE_TIME = Histogram(
    "api_response_time_seconds",
    "Histogram of API response times in seconds",
    ["method", "endpoint", "status_code"],
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Record the metrics in the histogram
        RESPONSE_TIME.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
        ).observe(process_time)
        return response


# Add middleware to FastAPI
app.add_middleware(PrometheusMiddleware)


@app.get("/service-times")
def get_service_times():
    metrics = {
        "uid": UID,
        "service_times": service_times,
        "arrival_times": arrivals,
        "departure_times": departures,
        "interarrival_times": iats,
        "queueing_times": queueing_times,
        "queue_lens": queue_lens,
    }

    return metrics


class RequestBody(BaseModel):
    num_samples: int


@app.get("/request-static")
@app.post("/request-static")
# @app.api_route("/request-static", methods=["GET", "POST"])
def get_request(request_body: RequestBody = None):
    global last_arrival, service_times

    t1 = time.time()

    arrivals.append(t1)

    if last_arrival is not None:
        iats.append(t1 - last_arrival)

    last_arrival = t1

    preds = model.predict()
    t2 = time.time()
    print("st", t2 - t1)

    service_times.append(t2 - t1)
    gc.collect()

    return preds


# @app.get("/request-dynamic")
# def get_request():
#     return model.predict_dynamic_batch_size()


@app.get("/reset")
def reset():
    global model, service_times

    del model, service_times

    service_times = []
    gc.collect()

    model = model_lib.model.Model()
    return "done"


@app.post("/flush")
async def flush_queue_endpoint():
    await flush_queue()
    return {"message": "Request queue flushed!"}


# @app.on_event("startup")
# async def startup():
#     Instrumentator().instrument(app).expose(app)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=port)
