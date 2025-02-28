export PYTHONPATH="./":$PYTHONPATH

# 1. Extracts the frames from the videos and the events from the DVS recordings
python registration/extract_aedat4.py \
    --aedat_folder="VIDEOS/Group-1/" \
    --video_folder="VIDEOS/Group-1/"

python registration/extract_aedat4.py \
    --aedat_folder="VIDEOS/Group-2/" \
    --video_folder="VIDEOS/Group-2/"

python registration/extract_aedat4.py \
    --aedat_folder="VIDEOS/Group-3/" \
    --video_folder="VIDEOS/Group-3/"

python registration/extract_aedat4.py \
    --aedat_folder="VIDEOS/Group-4/" \
    --video_folder="VIDEOS/Group-4/"

python registration/extract_aedat4.py \
    --aedat_folder="VIDEOS/Group-5/" \
    --video_folder="VIDEOS/Group-5/"

# 2. Plat the IMU data
python registration/plt_imu_2d_3d.py --video_root="VIDEOS/"


# 3. Make video without registration
python registration/make_group_in_a_video_for_visualization.py \
    --video_folder="VIDEOS/"

# 4. Registration
python ./registration/main.py \
    --video_group_root="VIDEOS-3/"
