import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


def authenticate_drive() -> GoogleDrive:
    """Xác thực Google Drive, chỉ mở browser lần đầu."""
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.json")

    if gauth.credentials is None:
        # Lần đầu phải login, copy link -> dán code
        gauth.CommandLineAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("mycreds.json")
    return GoogleDrive(gauth)


def merge_and_upload_to_drive(folder_path: str,
                              output_name: str = "merged_video.mp4",
                              mode: str = "all") -> str | None:
    """
    Merge nhiều file video trong folder (theo thời gian tạo) thành 1 file,
    rồi upload lên Google Drive.

    :param folder_path: đường dẫn thư mục chứa video local
    :param output_name: tên file video merged (local)
    :param mode: "all" (merge + upload), "merge" (chỉ merge), "up" (chỉ upload)
    :return: file_id của video đã upload lên Google Drive hoặc None
    """
    os.makedirs("merge-video-results", exist_ok=True)
    output_path = os.path.join("merge-video-results", output_name)
    file_id = None

    # ===== MERGE =====
    if mode in ("all", "merge"):
        video_exts = {".mp4", ".avi", ".mov", ".mkv"}
        files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f)) and os.path.splitext(f)[1].lower() in video_exts
        ]

        if not files:
            raise ValueError("Không tìm thấy video nào trong folder.")

        # Sắp xếp theo thời gian tạo
        files.sort(key=lambda x: os.path.getctime(x))

        # Merge video
        clips = [VideoFileClip(f) for f in files]
        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        final_clip.close()
        for c in clips:
            c.close()

    # ===== UPLOAD =====
    if mode in ("all", "up"):
        drive = authenticate_drive()

        file = drive.CreateFile({"title": os.path.basename(output_path)})
        file.SetContentFile(output_path)
        file.Upload()

        print("Đã upload thành công:", file['title'], "File ID:", file['id'])
        file_id = file["id"]

    return file_id
