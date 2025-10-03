import asyncio

import app_settings
from core.cloud_storage.uploadcare import UploadCareService
from core.cloud_storage.s3 import S3Service
from core.faceswaper import face_swap_service
from core.img_generator import img_generator_service
from core.video_faceswap.video_face_swap import process_video, detect_face_in_video
from core.video_faceswap import video_face_swap
from core.cloud_storage.google_drive import merge_and_upload_to_drive
import sys


def validate_int_arg(argv, index, default_val = 0):
    try:
        offset = int(argv[index])
        return offset
    except Exception as e:
        return default_val

async def main(argv):
    command = argv[1]
    if command == "swap":
      result = await face_swap_service.start_swap_pipline(argv[2], argv[3], argv[4]=='y')
      print(result)
      print("download succes !")
    elif command == "swap-batch":
        from_links = await UploadCareService().list_image_urls(1000)
        offset = validate_int_arg(argv, 3)
        limit = validate_int_arg(argv, 4)
        from_links = from_links[offset:limit]
        print(from_links)
        results = await face_swap_service.swap_in_batch(from_links, app_settings.TARGET_FACE_LINK, argv[2]=='y')
        if argv[2] == "n":
            print(results)
        print("download succes !")
    elif command == "upload-file":
       print("uploaded cloud link: ")
       cloud_link = await UploadCareService().upload_image(argv[2])
       print(cloud_link)
    elif command == "upload-folder":
       cloud_links = await UploadCareService().upload_from_folders(argv[2])
       print("uploaded cloud links: ")
       print(cloud_links)
    elif command == "list-cloud-files":
        cloud_links = await UploadCareService().list_image_urls()
        print("uploaded cloud links: ")
        print(cloud_links)
    elif command == "login":
        is_logged_in = await img_generator_service.login()
        if is_logged_in:
            print("login succes !")
        else:
            print("login fail !")
    elif command == "gen-img":
        result = await img_generator_service.start_gen_pipline(
            app_settings.GEN_PROMT,
            argv[2],
            True,
            argv[3] == "y"
        )
        if argv[3] == "n":
            print(result)
        else:
            print("download succes !")
    elif command == "gen-in-batch":
        result = await img_generator_service.gen_in_batch(
            app_settings.GEN_PROMT,
            argv[2],
            int(argv[3]),
            argv[4] == "y"
        )
        if argv[4] == "n":
            print(result)
        else:
            print("download succes !")
    elif command == "s3-up-folder":
        result = S3Service(app_settings.S3_BUCKET, app_settings.AWS_REGION).upload_folder(argv[2], argv[3])
        print(result)
    elif command == "s3-up-file":
        result = S3Service(app_settings.S3_BUCKET, app_settings.AWS_REGION).upload_file(argv[2], argv[3])
        print(result)
    elif command == "swap-batch-s3" or command == "swap-batch-s3-v2":
        from_links = S3Service(
            app_settings.S3_BUCKET,
            app_settings.AWS_REGION
        ).list_objects(argv[2])
        offset = validate_int_arg(argv, 4)
        limit = validate_int_arg(argv, 5)
        limit = len(from_links) if limit == 0 else limit
        from_links = from_links[offset:limit]
        print(from_links)
        if command == "swap-batch-s3":
            results = await face_swap_service.swap_in_batch(from_links, app_settings.TARGET_FACE_LINK, argv[3]=='y')
        else:
            results = await face_swap_service.start_optimize_swap_pipline(from_links, app_settings.TARGET_FACE_LINK, argv[3]=='y')
        if argv[3] == "n":
            print(results)
        print("download succes !")
    elif command == "list-object-s3":
        from_links = S3Service(
            app_settings.S3_BUCKET,
            app_settings.AWS_REGION
        ).list_objects(argv[2])
        for from_link in from_links:
            print(from_link)
    elif command == "get-result":
        await face_swap_service.download_in_batch()
        print("download succes !")
    elif command == "split-video":
        path = argv[2]
        mode = argv[3]
        process_video(
            path = path,
            mode = mode,
            duration=app_settings.VIDEO_DURATION,
            bucket = app_settings.S3_BUCKET,
            s3_prefix="videos"
        )
    elif command == "split-batch":
        import os
        video_path = "C:/Users/thinh/Downloads/kiki"
        list_videos = os.listdir(video_path)
        for video in list_videos:
            process_video(
                path=video_path+"/"+video,
                mode="upload",
                duration=app_settings.VIDEO_DURATION,
                bucket=app_settings.S3_BUCKET,
                s3_prefix="videos"
            )
    elif command == "detect-face":
        video_list = ["https://ghost-fast-cdn.s3.ap-southeast-1.amazonaws.com/videos/ssstwitter.com_1758364759646/_part002.mp4"]
        re = await detect_face_in_video(0, video_list)
        print(re)
    elif command == "swap-video":
        await video_face_swap.run_parallel_swap_pipeline(
            app_settings.VIDEO_SOURCE_FOLDER,
            target_face = app_settings.TARGET_FACE_LINK,
            index_to_detect=app_settings.VIDEO_INDEX_TO_DETECT_FACE
        )
    elif command == "merge-video":
        merge_and_upload_to_drive(argv[2], argv[3], argv[4])