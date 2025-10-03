import requests
import json
import asyncio
import httpx
import app_settings
from urllib.parse import urlparse
import os
import aiofiles

async def send_swap_request(from_face_link:str, to_face_link:str):
    url = "https://api.myimg.ai/api/image/unlimit-face-swapper/swap"  # Thay bằng endpoint chính xác
    headers = app_settings.EXECUTION_ENGINE_HEADER
    payload = {
        "imageUrl": from_face_link,
        "items": [
            {
                "faceUrl": from_face_link,
                "sourceUrl": to_face_link
            }
        ],
        "website": "myimg"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("✅ Success request")
            return response.json()["actionId"]
        print("❌ Lỗi:", response.status_code, response.text)
        return None

async def get_swap_status(request_id:int):
    url = "https://api.myimg.ai/api/action/info"
    headers = app_settings.EXECUTION_ENGINE_HEADER
    print("request_id:", request_id)
    params = {
        "action_id": request_id,
        "website": "myimg"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            percent = data['result'].get("percent")
            response_task = data['result'].get("response")
            if response_task is None:
                result_url = "NO RESULT"
            else:
                try:
                    result_url = json.loads(response_task)["resultUrl"]
                except Exception as e:
                    raise Exception("SWAP FAILED")
            print("✅ percent:", percent)
            print("✅ resultUrl:", result_url)
            return {"is_success": percent == 1.0, "result": result_url}
        return None

async def download_file(url: str, save_dir: str):
    if url is None:
        print("url is None")
        return
    os.makedirs(save_dir, exist_ok=True)
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    save_path = os.path.join(save_dir, filename)

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

        async with aiofiles.open(save_path, 'wb') as f:
            await f.write(response.content)

async def start_swap_pipline(from_face_link:str, to_face_link:str, download:bool = False):
    request_id = await send_swap_request(from_face_link, to_face_link)
    if request_id is None:
        return {"from_face_link": from_face_link, "status": False}
    await asyncio.sleep(1)
    retry_count = 0
    while True:
        status = await get_swap_status(request_id)
        if retry_count >= 30:
            return {"from_face_link": from_face_link, "status": False}
        if status is None:
            return {"from_face_link": from_face_link, "status": False}
        if status["is_success"]:
            if not download:
                return {"result_link": status["result"], "status": True}
            await download_file(status["result"], app_settings.LOCAL_RESUlT_FOLDER)
            break
        retry_count += 1
        await asyncio.sleep(1)

async def start_optimize_swap_pipline(from_face_links:list[str], to_face_link:str, download:bool = False):
    tasks = [send_swap_request(from_face_link, to_face_link) for from_face_link in from_face_links]
    task_ids = await asyncio.gather(*tasks)
    with open('pending_tasks', mode = 'w') as f:
        f.write(json.dumps(task_ids))
    return task_ids

async def download_in_batch():
    with open('pending_tasks', mode = 'r') as f:
        task_ids = json.loads(f.read())
    async def get_result_status(request_id):
        res = await get_swap_status(request_id)
        return res["result"]
    get_link_tasks = [get_result_status(request_id) for request_id in task_ids]
    download_links = await asyncio.gather(*get_link_tasks)
    with open('pending_links', mode = 'w') as f:
        f.write(json.dumps(download_links))
    download_tasks = [download_file(download_link, app_settings.LOCAL_RESUlT_FOLDER) for download_link in download_links]
    await asyncio.gather(*download_tasks)

async def swap_in_batch(from_face_links:list[str], to_face_link:str, download:bool = False):
    tasks = []
    results = []
    for from_face_link in from_face_links:
      results.append(await start_swap_pipline(from_face_link, to_face_link, download))
    if not download:
        return results
    print("swap succes !")