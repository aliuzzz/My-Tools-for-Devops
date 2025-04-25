import shutils
import os

xg_video_path = "/xg_data"

for root, dirs, files in os.walk(xg_video_path):
    for file in files:
        os.remove(os.path.join(root, file))
    for dir in dirs:
        shutil.rmtree(os.path.join(root, dir))