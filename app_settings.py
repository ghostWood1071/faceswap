UPLOAD_CARE_CLOUD_STORAGE_API_KEY = "821b56d0db8ef321d75e"
UPLOAD_CARE_CLOUD_STORAGE_API_KEY_SECRET = "1e03023b491fa49f3e51"
USER_SWAP_FACE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50SWQiOjE1ODkzMTIzLCJleHAiOjE3NjYyMTkzNjkuMzAzMTU3fQ.0C3GJ7MwPKHyNzUJTJH-6hH0V5DfPgznDQQ0QTszU_s"
EXECUTION_ENGINE_HEADER = {
        "accept": "*/*",
        "accept-language": "vi,en;q=0.9",
        "authorization": USER_SWAP_FACE_TOKEN,
        "content-type": "application/json",
        "origin": "https://www.myimg.ai",
        "priority": "u=1, i",
        "referer": "https://www.myimg.ai/",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
LOGIN_HEADERS = {
  "accept": "*/*",
  "accept-language": "vi,en;q=0.9",
  "content-type": "application/json",
  "origin": "https://www.myimg.ai",
  "priority": "u=1, i",
  "referer": "https://www.myimg.ai/",
  "sec-ch-ua": r"\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
  "sec-ch-ua-mobile": "?0",
  "sec-ch-ua-platform": r"\"Windows\"",
  "sec-fetch-dest": "empty",
  "sec-fetch-mode": "cors",
  "sec-fetch-site": "same-site",
  "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}
LOCAL_RESUlT_FOLDER = r"C:\Users\thinh\Downloads\crop-top"
S3_BUCKET = "ghost-fast-cdn"
AWS_REGION = "ap-southeast-1"
UPLOAD_CARE_BASE_API = 'https://api.uploadcare.com'
UPLOAD_CARE_CDN_BASE = 'https://ucarecdn.com'
UPLOAD_CARE_HEADER = {
    'Accept': 'application/vnd.uploadcare-v0.7+json',
    'Authorization': f'Uploadcare.Simple {UPLOAD_CARE_CLOUD_STORAGE_API_KEY}:{UPLOAD_CARE_CLOUD_STORAGE_API_KEY_SECRET}'
}
IMG_GENERATOR_SIZE = {
    "portrait": (576, 1024)
}
GEN_PROMT = "secretary white girl, sitting back straight, shoulders relaxed, and arms naturally resting down along both sides of the body, blonde hair is tied up in a tidy bun, wearing glasses, wearing thin white crop strapless top, wearing tiny silver skirt without panties, no underwear, no panties, show pinky pussy, skinny body, playful and youthful look, beautiful face, show beautiful pussy"
VIDEO_DURATION = 15
PARALLEL_VIDEO_PROCESS = 1
VIDEO_INDEX_TO_DETECT_FACE = 0
TOKEN_PER_ONE_SEC = 3
MAXIMUM_TOKEN = 90
MAX_RETRY=500
MAX_RETRY_LOGIN=5
VIDEO_SOURCE_FOLDER="s3://ghost-fast-cdn/videos/ssstwitter.com_1758364759646/"
TARGET_FACE_LINK = "https://ghost-fast-cdn.s3.ap-southeast-1.amazonaws.com/face/images%20%2812%29.jpg"
