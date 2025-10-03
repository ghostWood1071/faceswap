import httpx
import asyncio
import app_settings


async def call_swap_api():
    url = "https://api.myimg.ai/api/image/unlimit-face-swapper/swap"

    payload = {
        "imageUrl": "https://ucarecdn.com/4845e0a3-ea5a-45fc-8184-882e96a453e2/",
        "items": [
            {
                "faceUrl": "https://ucarecdn.com/4845e0a3-ea5a-45fc-8184-882e96a453e2/",
                "sourceUrl": "https://nguoinoitieng.tv/images/nnt/107/0/bka2.jpg",
            }
        ],
        "website": "myimg",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url, headers=app_settings.EXECUTION_ENGINE_HEADER, json=payload
        )
        print("Status:", response.status_code)
        print("Response:", response.text)


if __name__ == "__main__":
    asyncio.run(call_swap_api())
