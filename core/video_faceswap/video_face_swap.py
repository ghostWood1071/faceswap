import os

from dns.e164 import to_e164
from moviepy.editor import VideoFileClip
import json
import app_settings
import uuid
import boto3
from urllib.parse import urlparse
import asyncio
import copy
import httpx
import aiofiles


def get_header(token):
    headers = {
      "accept": "*/*",
      "accept-language": "vi,en;q=0.9",
      "authorization": token,
      "content-type": "application/json",
      "origin": "https://www.myimg.ai",
      "priority": "u=1, i",
      "referer": "https://www.myimg.ai/",
      "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": "\"Windows\"",
      "sec-fetch-dest": "empty",
      "sec-fetch-mode": "cors",
      "sec-fetch-site": "same-site",
      "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    }
    return headers


def process_video(
    path: str,
    mode: str = "local",
    duration: int = None,
    bucket: str = None,
    s3_prefix: str = "",
):
    """
    Xử lý path theo mode:
    - Nếu path là local:
        * mode=local:
            - folder -> list file sorted
            - video  -> split theo duration
        * mode=upload:
            - folder -> upload toàn bộ folder lên S3
            - video  -> split video, upload lên folder uuid trong S3
    - Nếu path là s3://... -> list object sorted trong bucket/prefix

    :param path: đường dẫn local hoặc S3
    :param mode: "local" hoặc "upload"
    :param duration: độ dài split (chỉ áp dụng cho video). Nếu None -> không split.
    :param bucket: tên bucket S3 (bắt buộc nếu upload hoặc path là local mà muốn upload)
    :param s3_prefix: prefix trong bucket (nếu cần)
    :return: danh sách file path hoặc S3 URI
    """
    s3_client = boto3.client("s3")
    # ================== Case: path là S3 ==================
    if path.startswith("s3://"):
        parsed = urlparse(path)
        bucket_name = parsed.netloc
        prefix = parsed.path.lstrip("/")

        # Lấy region của bucket
        loc = s3_client.get_bucket_location(Bucket=bucket_name)
        region = loc.get("LocationConstraint") or "us-east-1"

        resp = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if "Contents" not in resp:
            return []

        files = sorted(
            [
                f"https://{bucket_name}.s3.{region}.amazonaws.com/{obj['Key']}"
                for obj in resp["Contents"]
                if not obj["Key"].endswith("/")
            ]
        )
        return files

    # ================== Case: path local ==================
    if not os.path.exists(path):
        raise FileNotFoundError(f"Đường dẫn không tồn tại: {path}")

    # ---- Nếu là folder ----
    if os.path.isdir(path):
        files = sorted(
            [
                os.path.abspath(os.path.join(path, f))
                for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))
            ]
        )
        if mode == "local":
            return files
        elif mode == "upload":
            if not bucket:
                raise ValueError("Phải truyền bucket khi upload folder")
            uploaded_files = []
            for f in files:
                key = os.path.join(s3_prefix, os.path.basename(f))
                s3_client.upload_file(f, bucket, key)
                uploaded_files.append(f"s3://{bucket}/{key}")
            return uploaded_files

    # ---- Nếu là file video ----
    video_exts = {".mp4", ".avi", ".mov", ".mkv"}
    _, ext = os.path.splitext(path)
    if ext.lower() not in video_exts:
        # Không phải video thì chỉ trả file local hoặc upload
        if mode == "local":
            return [os.path.abspath(path)]
        elif mode == "upload":
            if not bucket:
                raise ValueError("Phải truyền bucket khi upload file")
            key = os.path.join(s3_prefix, os.path.basename(path))
            s3_client.upload_file(path, bucket, key)
            return [f"s3://{bucket}/{key}"]

    # ---- Nếu là video và cần split ----
    if duration is None:
        raise ValueError("Phải truyền duration để split video")

    video = VideoFileClip(path)
    total_duration = video.duration
    base_name, _ = os.path.splitext(os.path.basename(path))
    output_files = []

    part = 1
    start = 0
    if not os.path.exists(f"split_results/{base_name}/"):
        os.makedirs(f"split_results/{base_name}/")
    while start < total_duration:
        end = min(start + duration, total_duration)
        subclip = video.subclip(start, end)
        output_file = f"split_results/{base_name}/_part{part:03d}{ext}"
        subclip.write_videofile(
            output_file, codec="libx264", audio_codec="aac", verbose=False, logger=None
        )
        output_files.append(os.path.abspath(output_file))
        start = end
        part += 1
    video.close()

    if mode == "local":
        return output_files

    elif mode == "upload":
        if not bucket:
            raise ValueError("Phải truyền bucket khi upload video")
        uploaded_files = []
        folder_s3 = (os.path.join(s3_prefix, base_name) + "/").replace("\\", "/")
        s3_client.put_object(Bucket=bucket, Key=folder_s3)
        for f in output_files:
            key = os.path.join(s3_prefix, base_name, os.path.basename(f)).replace("\\", "/")
            s3_client.upload_file(f, bucket, key)
            uploaded_files.append(f"s3://{bucket}/{key}")
        return uploaded_files


async def login(save=True):
    url = "https://api.myimg.ai/api/account/login"  # Thay bằng endpoint chính xác
    headers = app_settings.LOGIN_HEADERS
    payload = {"platform": "guest", "device": {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "lang": "vi", "platform": "Win32", "screenWidth": 1536, "screenHeight": 864, "screenColorDepth": 24,
            "screenPixelDepth": 24,
            "canvasFingerprint": "data:image/png;base64,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",
            "audioFingerprint": 124.04347527516074}, "website": "myimg"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("✅ Success request")
            token = response.json()["result"]["token"]
            if save:
                token_id = save_token(token)
                return {token_id : token}
            return token
        print("❌ Lỗi:", response.status_code, response.text)
        return None

def check_token_folder(parent_path="", token='token'):
    try:
        token_path = os.path.join(parent_path, token)
        if os.path.exists(token_path):
            if os.path.isdir(token_path):
                # kiểm tra có file trong folder không
                files = [f for f in os.listdir(token_path) if os.path.isfile(os.path.join(token_path, f))]
                return len(files) > 0
            else:
                # tồn tại nhưng không phải folder
                return False
        else:
            os.makedirs(token_path, exist_ok=True)
            return True
    except Exception as e:
        print(f"Lỗi: {e}")
        return False

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

async def download_file(url: str, output_dir: str, chunk_size: int = 8192) -> str | None:
    """
    Download file bất đồng bộ và lưu xuống folder, giữ nguyên tên file từ URL.

    :param url: URL của file
    :param output_dir: folder muốn lưu file
    :param chunk_size: kích thước chunk (default 8KB)
    :return: đường dẫn file vừa tải nếu thành công, None nếu lỗi
    """
    try:
        # Lấy tên file từ URL
        file_name = os.path.basename(urlparse(url).path)
        if not file_name:  # nếu URL không có tên file
            file_name = "downloaded_file"

        # Ghép thành đường dẫn file
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, file_name)

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                async with aiofiles.open(output_path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=chunk_size):
                        await f.write(chunk)

        return output_path
    except Exception as e:
        print(f"Lỗi khi download {url}: {e}")
        return None

async def get_task_status(request_id:int, token=None):
    url = "https://api.myimg.ai/api/action/info"
    headers = copy.copy(app_settings.EXECUTION_ENGINE_HEADER)
    print("request_id:", request_id)
    if token:
        headers['authorization'] = token
    params = {
        "action_id": request_id,
        "website": "myimg"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            percent = data['result'].get("percent")
            print(percent)
            response_task = data['result'].get("response")
            if response_task in [None, ""]:
                result_url = "NO RESULT"
            else:
                try:
                    result_url = json.loads(response_task)
                except Exception as e:
                    raise Exception("FAILED")
            return result_url
        return None

async def detect_face_in_video(video_index, video_list):
    video_detect = video_list[video_index]
    print("video detect:", video_detect)
    url = "https://api.myimg.ai/api/video/unlimit-face-swapper/detect/v2"
    headers = app_settings.EXECUTION_ENGINE_HEADER
    payload = {
        "videoUrl": video_detect,
        "website": "myimg"
    }
    action_id = None
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        print(response.json())
        if response.status_code == 200:
            print("✅ Success request")
            action_id = response.json()["actionId"]
    if action_id is None:
        return None
    retry_count = 0
    while True:
        try:
            action_status = await get_task_status(action_id)
            if action_status != "NO RESULT":
                face_urls = action_status.get("faceUrls")
                return face_urls
            if retry_count >= app_settings.MAX_RETRY:
                print("DETECT FAILED")
                break
            await asyncio.sleep(1)
            retry_count+=1
        except Exception as e:
            raise e

async def run_swap_task(token, video_path, face_path, target_face_path):
    print("run: ", video_path)
    url = "https://api.myimg.ai/api/video/unlimit-face-swapper/swap/v2"
    payload = {
        "videoUrl": video_path,
        "items": [
            {
                "faceUrl": face_path,
                "sourceUrl": target_face_path
            }
        ],
        "website": "myimg"
    }

    headers = {
        "accept": "*/*",
        "accept-language": "vi,en;q=0.9",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://www.myimg.ai",
        "priority": "u=1, i",
        "referer": "https://www.myimg.ai/",
        "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    }
    action_id = None
    retry = app_settings.MAX_RETRY_LOGIN
    while retry > 0:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            print(response.json())
            if response.status_code == 200:
                print("✅ Success request")
                action_id = response.json()["actionId"]
        if action_id is None:
            print("❌ Lỗi swap:", response.status_code, response.text)
            if response.json()['code'] == -10:
                logged_in = await login()
                if logged_in:
                    token = load_token()
                    headers['authorization'] = token
                retry -= 1
            else:
                return None
        else:
            break
    retry_count = 0
    while True:
        try:
            action_status = await get_task_status(action_id, token=token)
            if action_status != 'NO RESULT':
                return action_status.get("resultUrl")
            await asyncio.sleep(1)
            retry_count += 1
            if retry_count >= app_settings.MAX_RETRY:
                break
        except Exception as e:
            raise e

async def get_token():
    token = load_token()
    is_enough_token = await check_token_count(token)
    if not is_enough_token:
        logged_in = await login()
        if logged_in:
            token = load_token()
        else:
            raise Exception("loggin failed")
    return token

async def run_parallel_swap_pipeline(s3_folder, target_face, index_to_detect):
    list_video_files = process_video(s3_folder)
    face_url = await detect_face_in_video(index_to_detect, list_video_files)
    print("face_url: ", face_url)
    result_folder = f"video-swap-result/{str(uuid.uuid4())}"
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
    for file in list_video_files:
        token = await get_token()
        url = await run_swap_task(token, file, face_url[0], target_face)
        await download_file(url, result_folder)







