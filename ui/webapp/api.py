import asyncio

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from core.cloud_storage.s3 import S3Service
import app_settings
from core.faceswaper import face_swap_service

app = FastAPI()

# Cho phép truy cập từ trình duyệt
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve trang HTML
@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("./ui/webapp/faceswap.html", encoding="utf-8") as f:
        return f.read()

# Dữ liệu mô phỏng
DUMMY_SOURCE = [
    {"url": "https://via.placeholder.com/300x200?text=Source+1", "type": "file"},
    {"url": "https://via.placeholder.com/300x200?text=Source+2", "type": "file"}
]

DUMMY_TARGET = [
    {"url": "https://via.placeholder.com/100x100?text=Target+1", "type": "file"},
    {"url": "https://via.placeholder.com/100x100?text=Target+2", "type": "file"},
    {"url": "https://via.placeholder.com/100x100?text=Folder", "type": "folder"}
]

@app.get("/api/source-list")
async def get_source_list(path:str=None):
    print(path)
    s3 = S3Service(app_settings.S3_BUCKET, app_settings.AWS_REGION)
    result = s3.list_objects(path)
    return result

@app.get("/api/target-list")
async def get_target_list(path:str=None):
    s3 = S3Service(app_settings.S3_BUCKET, app_settings.AWS_REGION)
    result = s3.list_objects(path)
    return result

class ProcessRequest(BaseModel):
    source: str
    targets: list[str]
    paramRange: list[int]

@app.post("/api/process")
async def process_images(payload: ProcessRequest):
    print("📥 PROCESS REQUEST:")
    print("Source:", payload.source)
    print("Targets:", payload.targets)
    print("Param range:", payload.paramRange)
    task_ids = await face_swap_service.start_optimize_swap_pipline(payload.targets, payload.source, False)
    return task_ids

@app.post("/api/download")
async def download_result(ids: list[int] = []):
    tasks = [face_swap_service.get_swap_status(id) for id in ids]
    results = await asyncio.gather(*tasks)
    return results

