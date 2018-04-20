import skvideo.io
import skvideo.datasets
import skvideo.utils
import skvideo.measure

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

import glob,os
import datetime
import random
import functools, itertools

from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip

#start time
print ("[STATUS] start time - {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
start_time = datetime.datetime.now()
   
'''
INPUT DATA
'''
david_videos_path = 'dataset/david/'

david_videos_list = glob.glob("dataset/david/*.mp4") #list of videos in the directory

next_video_list = [] #list of index of the videos
len_video_list = [] #list of len of the videos

video_list = [] #list of videos to avoid repetition
video_hist = [9,9,9,9]
video_score_list = [] #list of scores of the videos

data = []



'''
Verify the quality score using niqe algorithm and add to the plot graph.

@args: video file from sk-video

'''
def video_quality_score(video_file, name_file):
    score_by_frame = skvideo.measure.niqe(video_file)
    plt.plot(score_by_frame,label=name_file)
    #return score_by_frame


'''
FIFO video list - to increase variety
'''
def fifo_video(video):
    video_hist.pop(0)
    video_hist.append(video)

'''
if video appeared too much, return true. else false
'''
def isreapeated(video):
    if video == video_hist[-1]:
        return True
    

    count = 0
    for i in video_hist:
        if i == video:
            count+=1
    
    if count > 1:
        return True
    
    return False


'''
go through all files in the dataset
'''
for file in david_videos_list:
    #downsample files
    downsample_file = file.split('.')[0] + '_D.mp4'
    output_file = file.split('.')[0] + '_F.mp4'
    output_audio = file.split('.')[0] + '.wav'
    print(file)

    #downsample for processing
    command_downsample = 'ffmpeg -i {0} -r 30 -vf scale=480:-1 -y -profile:v baseline -crf 18 -c:a copy  {1}'.format(file,downsample_file)
    os.system(command_downsample)

    #get audio file
    command_audio = 'ffmpeg -i {0} -map 0:1 -acodec pcm_s16le -ac 2 {1}'.format(file,output_audio)
    os.system(command_audio)

    #framerate for final edit
    #command_framerate = 'ffmpeg -i {0} -r 30 -y -profile:v baseline -crf 18 -c:a copy  {1}'.format(file,output_file)
    #os.system(command_framerate)


    #work on downsampled file
    vid = skvideo.io.vread(downsample_file, outputdict={"-pix_fmt": "gray"})[:, :, :, 0]
    video_quality_score(vid,file.split('/')[-1])


    #load big videos
    video_list.append(VideoFileClip(file))




'''
BUILD FINAL VIDEO
'''
max_frames = video_list[0].duration 
#max_frames = len(video_list[0])
print (max_frames)

#order of file list (input from Learning part)
next_video_index = random.randint(0,len(david_videos_list)-1)
#len_video_index = random.randint(60, 90) #length in frames
len_video_index = random.randint(2, 3) #length in seconds

final_cut = []

i = 0
while i < (max_frames-3):
    
    print(i,i+len_video_index)
    print(next_video_index)
    final_cut.append(video_list[next_video_index].subclip(i,i+len_video_index))

    i+=len_video_index
    
    next_video_index = random.randint(0,len(david_videos_list)-1)
    #print(next_video_index)
    if isreapeated(next_video_index):
        next_video_index = ((next_video_index + random.randint(1,2)) % 3)
    
    fifo_video(next_video_index)

    len_video_index = random.randint(2, 3)

final_cut.append(video_list[next_video_index].subclip(max_frames-3,max_frames))

#load best audio
audio_file = AudioFileClip("dataset/david/david_02.wav")

final_clip = concatenate_videoclips(final_cut).set_audio(audio_file)
#final_clip = final_clip.set_audio(audio)
final_clip.write_videofile("dataset/david/final.mp4")



#print total time
print ("[STATUS] start time - {}".format(start_time.strftime("%Y-%m-%d %H:%M")))
print ("[STATUS] end time - {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))

#show plot graph for visual help
sns.set()
plt.legend()
plt.show()


