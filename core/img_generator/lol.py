import asyncio
import httpx
import json

url = "https://api.myimg.ai/api/video/unlimit-face-swapper/swap/v2"

payload = {
    "videoUrl": "https://ghost-fast-cdn.s3.ap-southeast-1.amazonaws.com/videos/ssstwitter.com_1758364759646/_part001.mp4",
    "items": [
        {
            "faceUrl": "https://files.myimg.ai/MyIMG.AI_20250921_309bc7d4-91c2-4783-ad9d-fb42636c218d.png",
            "sourceUrl": "https://ghost-fast-cdn.s3.ap-southeast-1.amazonaws.com/face/353648845_1957863064587269_6650026831014609955_n.jpg"
        }
    ],
    "website": "myimg"
}

headers = {
    "accept": "*/*",
    "accept-language": "vi,en;q=0.9",
    "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50SWQiOjE1ODgyODAwLCJleHAiOjE3NjYyMTA3OTcuOTUxMTY0fQ.U45VLMcMyu_cSq70ifQIKlmXxooDLRrkfqZGIkjsTFI",
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


async def main():
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        print("Status:", response.status_code)
        print("Response:", response.text)


if __name__ == "__main__":
    asyncio.run(main())



x = {
    'videoUrl': 'https://files.myimg.ai/MyIMG.AI_20250921_309bc7d4-91c2-4783-ad9d-fb42636c218d.png',
    'items': [
        {
            'faceUrl': 'https://ghost-fast-cdn.s3.ap-southeast1.amazonaws.com/videos/ssstwitter.com_1758364759646/_part001.mp4',
            'sourceUrl': 'https://ghost-fast-cdn.s3.ap-southeast-1.amazonaws.com/face/399571729_1964564307263877_3672545899304896706_n.jpg'
         }
    ],
    'website': 'myimg'
}