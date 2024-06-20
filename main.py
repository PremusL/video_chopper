from video_creation import return_seconds, chop_background
from transcript_selection import transcript_selection, combined_transcript, extract_audio, transcribe, combined_transcript
import pandas as pd


def start_end_times(final_data):
    data= pd.read_csv('fixed_subtitles.csv')

    complete_start_end_times = []
    for i in final_data:
        print(i)
        i = str.lower(i)
        i = i.replace(",", " ")
        i = i.replace(".", " ")
        i = i.replace("?", " ")
        i = i.replace("!", " ")

        temp_list = i.split(' ')
        index=0
        all_indices = []
        while index < len(temp_list)-7:
            current_slice = temp_list[index:index+7]
            current_slice = ' '.join(current_slice)

            indices = data[data['subtitle'].str.contains(current_slice, case=False)].index
            if len(indices) > 0:
                # print(data.loc[indices[0]]['start'])
                if indices[0] not in all_indices:
                    all_indices.append(indices[0])
            index += 1
        all_indices = sorted(all_indices)
        print(all_indices)
        complete_start_end_times.append([data.loc[all_indices[0]]['start'], data.loc[all_indices[-1]]['end']])
    
    return complete_start_end_times


def main():
    input_video = "./videos/general/joe_rogan_short.mp4"
    # first we extract audio from the video
    audio_name = extract_audio(input_video)
    print(f"audioooooooooooooooo name {audio_name}")
    # then we transcribe the audio
    srt_name = transcribe(audio_path=audio_name)
    # now we have srt file
    # combining
    combined_transcript(srt_name=srt_name)
    # now we have transcript.txt
    # now we have to select the best parts
    final_data = transcript_selection()
    time_list = start_end_times(final_data)

    for index,time in enumerate(time_list):
        start_time = return_seconds(time[0])
        end_time = return_seconds(time[1])
        chop_background(start_time, end_time, input_video, index)
        print(f"Chopped {index}th part")
    print("All done!")
    

if __name__ == '__main__':
    main()