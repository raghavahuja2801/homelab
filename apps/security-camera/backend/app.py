import asyncio
import os
import threading
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from onvif import ONVIFCamera


CAMERA_IP = os.environ["CAMERA_IP"]
ONVIF_PORT = int(os.getenv("ONVIF_PORT", "2020"))
CAMERA_USERNAME = os.environ["CAMERA_USERNAME"]
CAMERA_PASSWORD = os.environ["CAMERA_PASSWORD"]


app = FastAPI(title="Camera API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class MoveRequest(BaseModel):
    pan: float = Field(default=0.0, ge=-1.0, le=1.0)
    tilt: float = Field(default=0.0, ge=-1.0, le=1.0)


class PresetRequest(BaseModel):
    name: str


class CameraController:
    def __init__(self):
        self.camera = None
        self.media = None
        self.ptz = None
        self.profile = None
        self.lock = threading.Lock()

    def connect(self):
        if self.camera is not None:
            return

        self.camera = ONVIFCamera(
            CAMERA_IP,
            ONVIF_PORT,
            CAMERA_USERNAME,
            CAMERA_PASSWORD,
        )

        self.media = self.camera.create_media_service()
        self.profile = self.media.GetProfiles()[0]
        self.ptz = self.camera.create_ptz_service()

    def _move(self, pan: float, tilt: float):
        with self.lock:
            self.connect()

            self.ptz.ContinuousMove({
                "ProfileToken": self.profile.token,
                "Velocity": {
                    "PanTilt": {
                        "x": pan,
                        "y": tilt,
                    }
                },
            })

    def _stop(self):
        with self.lock:
            self.connect()

            self.ptz.Stop({
                "ProfileToken": self.profile.token,
            })

    def _status(self):
        with self.lock:
            self.connect()

            status = self.ptz.GetStatus({
                "ProfileToken": self.profile.token,
            })

            position = status.Position.PanTilt

            return {
                "pan": position.x,
                "tilt": position.y,
                "status": status.MoveStatus.PanTilt,
            }

    def _presets(self):
        with self.lock:
            self.connect()

            presets = self.ptz.GetPresets({
                "ProfileToken": self.profile.token,
            })

            return [
                {
                    "token": preset.token,
                    "name": preset.Name,
                }
                for preset in presets
            ]

    def _goto_preset(self, token: str):
        with self.lock:
            self.connect()

            self.ptz.GotoPreset({
                "ProfileToken": self.profile.token,
                "PresetToken": token,
            })

    def _set_preset(self, name: str):
        with self.lock:
            self.connect()

            result = self.ptz.SetPreset({
                "ProfileToken": self.profile.token,
                "PresetName": name,
            })

            return {
                "token": result.token,
                "name": result.Name,
            }


controller = CameraController()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ptz/status")
async def ptz_status():
    try:
        return await asyncio.to_thread(controller._status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ptz/move")
async def ptz_move(request: MoveRequest):
    try:
        await asyncio.to_thread(
            controller._move,
            request.pan,
            request.tilt,
        )

        return {
            "status": "moving",
            "pan": request.pan,
            "tilt": request.tilt,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ptz/stop")
async def ptz_stop():
    try:
        await asyncio.to_thread(controller._stop)

        return {"status": "stopped"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/presets")
async def get_presets():
    try:
        return await asyncio.to_thread(controller._presets)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/presets/{token}/goto")
async def goto_preset(token: str):
    try:
        await asyncio.to_thread(
            controller._goto_preset,
            token,
        )

        return {
            "status": "ok",
            "token": token,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/presets")
async def set_preset(request: PresetRequest):
    try:
        return await asyncio.to_thread(
            controller._set_preset,
            request.name,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
