import requests
import json
import asyncio
import httpx
import app_settings
from urllib.parse import urlparse
import os
import aiofiles
from urllib3.util import url


async def send_gen_request(promt: str, size_type: str, token: str):
    url = "https://api.myimg.ai/api/image/nsfw-text-to-image-v2"  # Thay bằng endpoint chính xác
    headers = app_settings.EXECUTION_ENGINE_HEADER
    headers["authorization"] = token
    size = app_settings.IMG_GENERATOR_SIZE[size_type]
    payload = {
        "prompt": promt,
        "style": "default",
        "width": size[0],
        "height": size[1],
        "website": "myimg",
    }
    print(payload)
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("✅ Success request")
            return response.json()["actionId"]
        print("❌ Lỗi:", response.status_code, response.text)
        return None


async def get_gen_status(request_id: int):
    url = "https://api.myimg.ai/api/action/info"
    headers = app_settings.EXECUTION_ENGINE_HEADER
    print("request_id:", request_id)
    params = {"action_id": request_id, "website": "myimg"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            percent = data["result"].get("percent")
            response_task = data["result"].get("response")
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
    os.makedirs(save_dir, exist_ok=True)
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    save_path = os.path.join(save_dir, filename)

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

        async with aiofiles.open(save_path, "wb") as f:
            await f.write(response.content)


def load_token():
    with open("token.txt", "r") as f:
        token = f.read()
    return token


def save_token(token):
    with open("token.txt", mode="w") as f:
        f.write(token)


async def check_token_count(token):
    headers = app_settings.EXECUTION_ENGINE_HEADER
    headers["authorization"] = token
    params = {"website": "myimg"}
    url = "https://api.myimg.ai/api/account/detail"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            result = data.get("result")
            if result is None:
                return False
            credits = result.get("credits")
            if credits is None:
                return False
            if credits <= 0:
                return False
            return True


async def start_gen_pipline(
    promt: str, size_type: str, is_logged_in: bool = True, download: bool = False
):
    token = load_token()
    is_enough_token = await check_token_count(token)
    if is_logged_in:
        if not is_enough_token:
            logged_in = await login()
            if logged_in:
                token = load_token()
            else:
                raise Exception("loggin failed")
    request_id = await send_gen_request(promt, size_type, token)
    if request_id is None:
        return {"gen_promt": promt, "status": False}
    await asyncio.sleep(1)
    while True:
        status = await get_gen_status(request_id)
        if status is None:
            return {"gen_promt": promt, "status": False}
        if status["is_success"]:
            if not download:
                return {"result_link": status["result"], "status": True}
            await download_file(status["result"], app_settings.LOCAL_RESUlT_FOLDER)
            break
        await asyncio.sleep(1)


async def login():
    url = "https://api.myimg.ai/api/account/login"  # Thay bằng endpoint chính xác
    headers = app_settings.LOGIN_HEADERS
    payload = {
        "platform": "guest",
        "device": {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "lang": "vi",
            "platform": "Win32",
            "screenWidth": 1536,
            "screenHeight": 864,
            "screenColorDepth": 24,
            "screenPixelDepth": 24,
            "canvasFingerprint": "data:image/png;base64,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",
            "audioFingerprint": 124.04347527516074,
        },
        "website": "myimg",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("✅ Success request")
            token = response.json()["result"]["token"]
            save_token(token)
            return True
        print("❌ Lỗi:", response.status_code, response.text)
        return False


async def gen_in_batch(
    promt: list[str], size_type: str, batch_size: str, download: bool = False
):
    results = []
    for index in range(batch_size):
        is_logged_in = True
        result = await start_gen_pipline(promt, size_type, is_logged_in, download)
        results.append(result)
    if not download:
        return results
    print("swap succes !")
