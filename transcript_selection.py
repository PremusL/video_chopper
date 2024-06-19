import ollama
import time
import math
import ffmpeg

import whisper 
import torch

import srt
import re

import ast

import stable_whisper
import datetime


def extract_audio(input_video:str)->str:

    input_video_name = input_video.replace(".mp4", "")

    extracted_audio = f"audio-{input_video_name}.wav"
    stream = ffmpeg.input(input_video)
    stream = ffmpeg.output(stream, extracted_audio)
    ffmpeg.run(stream, overwrite_output=True)
    return extracted_audio


def transcribe(audio_path, output_name="audio.srt"):
    model = stable_whisper.load_model('base')
    result = model.transcribe(audio_path)
    result.to_srt_vtt(output_name)
    return output_name


def remove_tags(text):
    return re.sub('<[^>]*>', '', text)

def combined_transcript(srt_name): #? makes a new file where there are unique only subtitles and their times, made from srt

    with open(srt_name, 'r') as f:
        data = f.read()
    subs = list(srt.parse(data))

    all_subs = []
    all_subs_times = []
    index_time = -1
    with open("transcript.txt", 'w') as f:
        for i, _ in enumerate(subs):
            current = subs[i]
            start = current.start
            end = current.end
            temp_line = remove_tags(current.content)
            # print(f"{start} -> {end}: {temp_line}")
            if temp_line not in all_subs:
                all_subs.append(temp_line)
                all_subs_times.append([start, end])
                index_time += 1
                f.write(temp_line)
            else:
                all_subs_times[index_time][1] = end

    
    with open('fixed_subtitles.csv', 'w') as f:
        f.write("index,start,end,subtitle\n")
        for i, _ in enumerate(all_subs):
            temp_line = str.lower(all_subs[i])
            temp_line = temp_line.replace(",", " ")
            temp_line = temp_line.replace(".", " ")
            temp_line = temp_line.replace("?", " ")
            temp_line = temp_line.replace("!", " ")
            f.write(f"{i},{all_subs_times[i][0]},{all_subs_times[i][1]},{temp_line}\n")




#! This script is used to select the most important parts of a video transcript.
def transcript_selection():
    video_transcript = ""
    filename = "transcript.txt"
    with open(filename, 'r') as f:
        video_transcript = f.read()


    stream = ollama.chat(
        model='llama3',
        messages=[{'role': 'system',
                    'content': 'You are a system that gives me the most important/interetsing parts of a video transcript. You do not summerize or explain, just print the way it is written in the transcript. Parts should be at least 4 sentences long, do not concatenate the result. json format as follows: {"index": "important part"}, print 3 parts.'},
                    {'role': 'user',
                    'content': f'Here is the content do your job: {video_transcript}, give me correct json format'},                
                    ],
        stream=True,
    )
    data_write = ""
    for chunk in stream:
        data_write += chunk['message']['content']
    # print(chunk['message']['content'], end='', flush=True)

    with open('output.txt', 'w') as f:
        start = False
        for d in data_write:
            if d == '{':
                start = True
            if start:
                f.write(d)

    final_data = []
    with open('output.txt', 'r+') as file:
        for line in file:
            if line == '\n':
                continue
            d = ast.literal_eval(line)
            final_data.append(d['index'])

    return final_data




def return_seconds(time):
    time_object = datetime.strptime(time, "%H:%M:%S.%f").time()
    total_seconds = time_object.hour * 3600 + time_object.minute * 60 + time_object.second + time_object.microsecond / 1E6
    return total_seconds