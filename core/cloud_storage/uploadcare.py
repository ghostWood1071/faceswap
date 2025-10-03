import os
import asyncio
import aiofiles
import app_settings
import httpx
from typing import List
import app_settings as settings

class UploadCareService:
    async def list_image_urls(self, limit: int = 100) -> List[str]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f'{app_settings.UPLOAD_CARE_BASE_API}/files/', headers=app_settings.UPLOAD_CARE_HEADER, params={'limit': limit})
            resp.raise_for_status()
            files = resp.json()['results']
            img_links = [f"{app_settings.UPLOAD_CARE_CDN_BASE}/{f['uuid']}/" for f in files if f.get("is_image")]
            return img_links

    async def upload_image(self, path: str) -> str:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"❌ File không tồn tại: {path}")

        async with aiofiles.open(path, "rb") as f:
            file_data = await f.read()

        filename = os.path.basename(path)

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{app_settings.UPLOAD_CARE_BASE_API}/base/",
                data={
                    "UPLOADCARE_PUB_KEY": app_settings.UPLOAD_CARE_CLOUD_STORAGE_API_KEY,
                    "UPLOADCARE_STORE": "auto",
                },
                files={"file": (filename, file_data)},
            )
            resp.raise_for_status()
            result = resp.json()
            return f"{app_settings.UPLOAD_CARE_CDN_BASE}/{result['file']}/"


    async def upload_images(self, paths: List[str]) -> List[str]:
        tasks = [upload_image(path) for path in paths]
        return await asyncio.gather(*tasks)

    async def upload_from_folders(self, folder_path:str, batch_size=1) -> List[str]:
        list_files = ["/".join([folder_path.replace("\\", "/"), x]) for x in os.listdir(folder_path)]
        result = []
        for file in list_files:
            result.append(await upload_image(file))
        return result