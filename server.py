# encoding: utf-8
import os
import traceback

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse

from kaspad.KaspadMultiClient import KaspadMultiClient
from fastapi.middleware.gzip import GZipMiddleware

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
socket_app = socketio.ASGIApp(sio)

app = FastAPI(
    title="Kaspa REST-API server",
    description="This server is to communicate with kaspa network via REST-API",
    version="0.0.2",
    contact={
        "name": "lAmeR1"
    },
    license_info={
        "name": "MIT LICENSE"
    }
)

app.add_middleware(GZipMiddleware, minimum_size=500)

app.mount("/ws", socket_app)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping", include_in_schema=False,
         response_class=PlainTextResponse)
async def get_circulating_coins(in_billion: bool = False):
    """
    Ping Pong
    """
    return "pong"


kaspad_hosts = []

for i in range(100):
    try:
        kaspad_hosts.append(os.environ[f"KASPAD_HOST_{i + 1}"].strip())
    except KeyError:
        break

if not kaspad_hosts:
    raise Exception('Please set at least KASPAD_HOST_1 environment variable.')

kaspad_client = KaspadMultiClient(kaspad_hosts)

@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, exc: Exception):
    await kaspad_client.initialize_all()
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"
                 # "traceback": f"{traceback.format_exception(exc)}"
                 },
    )
