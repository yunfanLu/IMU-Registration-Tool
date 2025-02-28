from os.path import join
import json
from absl import app
from absl.flags import FLAGS
from absl.logging import info
from os import listdir
from os.path import isdir
import os
import cv2
from tqdm import tqdm
import numpy as np


def adjust_average_brightness(image, target_brightness):
    # 转换为灰度图
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # 计算当前均值和极值
    current_mean = np.mean(gray)
    x_min = np.min(gray)
    x_max = np.max(gray)

    # 钳制目标亮度
    target = np.clip(target_brightness, 0, 255)

    # 处理所有像素相同的情况
    if x_min == x_max:
        delta = target - current_mean
        adjusted = np.clip(gray.astype(np.int16) + delta, 0, 255).astype(np.uint8)
        return adjusted

    # 计算缩放因子a
    a1 = (255 - target) / (x_max - current_mean)
    a2 = target / (current_mean - x_min)
    a = min(a1, a2)

    # 计算偏移量b
    b = target - a * current_mean

    # 应用线性变换并钳制
    adjusted = cv2.convertScaleAbs(gray, alpha=a, beta=b)

    # 如果是彩色图像，则将调整后的灰度图转换回彩色
    if len(image.shape) == 3:
        # change the Y channel
        yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        yuv[:, :, 0] = adjusted
        adjusted = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

    return adjusted

def make_video_in_a_group(group_folder, videos, event_frames):
    info(f"Group: {group_folder}")
    info(f"  Videos: {videos}")
    # 现在的几个视频的帧率不一样，以最长的为准。
    length_max = 0
    for frames, events in event_frames:
        length_max = max(length_max, len(frames), len(events))
        info(f"  Frames: {len(frames)}, Events: {len(events)}")
    info(f"  Max length: {length_max}")
    video_count = len(videos)
    H, W = 290, 346

    output_path = os.path.join(group_folder, f"video-{length_max}-registrated-same-Y.avi")
    info(f"  Output: {output_path}")
    # 指定编码器和创建 VideoWriter 对象
    fourcc = cv2.VideoWriter_fourcc(*"XVID")  # 定义视频编码器
    out = cv2.VideoWriter(output_path, fourcc, 10, (W * 2, H * video_count))  # 定义视频写入对象

    # make a video with this frames and events
    for i in tqdm(range(length_max)):
        # make a frame
        frame_in_video = np.zeros((H * video_count, W * 2, 3), dtype=np.uint8)
        average_illumination = 256 * 0.6
        for j in range(video_count):
            # 根据比率算当前视频是第几帧
            idx = int(1.0 * i * (len(event_frames[j][0]) - 1) / length_max)
            frame_path = os.path.join(group_folder, videos[j], "frame_event", event_frames[j][0][idx])
            event_path = os.path.join(group_folder, videos[j], "frame_event", event_frames[j][1][idx])
            frame = cv2.imread(frame_path)
            event = cv2.imread(event_path)

            # to make the frame with the same illumination by YUV ?
            # frame = frame * (average_illumination / np.mean(frame))
            # The above code is wrong, it will make some pixel value larger than 255
            frame = adjust_average_brightness(frame, average_illumination)

            frame_with_text = np.zeros((H, W * 2, 3), dtype=np.uint8)
            frame_with_text[:260, :W, :] = frame
            frame_with_text[:260, W:, :] = event
            frame_with_text = cv2.putText(
                frame_with_text,
                f"{videos[j]}",
                (20, 280),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )
            frame_in_video[j * H : (j + 1) * H, :, :] = frame_with_text
        out.write(frame_in_video)
    out.release()


def make_registration_visualization_of_each_group(GROUP_ROOT):
    with open(join(GROUP_ROOT, "registrate_result.json"), "r") as f:
        registrate_result = json.load(f)
    event_frames = []
    videos = []
    for key, value in registrate_result.items():
        start_timestamp = value["start_timestamp"]
        end_timestamp = value["end_timestamp"]
        frame_event_folder = join(GROUP_ROOT, key, "frame_event")
        # f ends with png
        files = [f for f in listdir(frame_event_folder) if f.endswith(".png")]
        files = sorted(files)
        # timestamp is the first number of files
        frame_event_files = [[], []]
        for f in files:
            timestamp = float(f.split("_")[0])
            if start_timestamp <= timestamp <= end_timestamp:
                if "_vis" in f:
                    frame_event_files[1].append(f)
                else:
                    frame_event_files[0].append(f)
        videos.append(key)
        event_frames.append(frame_event_files)
    make_video_in_a_group(GROUP_ROOT, videos, event_frames)


if __name__ == "__main__":
    import pudb

    app.run(main)
