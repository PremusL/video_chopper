import pandas as pd

from datetime import datetime


from moviepy.editor import AudioFileClip, VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


def return_seconds(time):
    time_object = datetime.strptime(time, "%H:%M:%S.%f").time()
    total_seconds = time_object.hour * 3600 + time_object.minute * 60 + time_object.second + time_object.microsecond / 1E6
    return total_seconds


def chop_background(start: int, end: int, index: int = 0):
    video_choice = "bbswitzer-parkour.mp4"
    path2 = "./joe_rogan_short.mp4"
    try:
        print("extracting subclip")
        ffmpeg_extract_subclip(
            f"assets/backgrounds/video/{video_choice}",
            start,
            end,
            targetname=f"moje/temp/{index}/background.mp4",
        )
    except (OSError, IOError):  # ffmpeg issue see #348
        print("FFMPEG issue. Trying again...")
        with VideoFileClip(path2) as video:
            new = video.subclip(start, end)
            new.write_videofile(f"./clips/joe_rogan_short_{index}.mp4")
    print("Background video chopped successfully!")


time_list = [['0:00:00.660000', '0:00:32.100000'], ['0:00:35.780000', '0:01:01.200000'], ['0:01:43.240000', '0:02:20.160000']]

data = pd.read_csv("fixed_subtitles.csv")

for index,time in enumerate(time_list):
    start_time = return_seconds(time[0])
    end_time = return_seconds(time[1])
    chop_background(start_time, end_time, index)
