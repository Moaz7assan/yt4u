from pytube import YouTube
import os
import ffmpeg
"""
link
title
v or a
quality
captions?
where to download
Progress Bar
done

combine 
def combine_audio(vidname, audname, outname, fps=25):
    import moviepy.editor as mpe
    my_clip = mpe.VideoFileClip(vidname)
    audio_background = mpe.AudioFileClip(audname)
    final_clip = my_clip.set_audio(audio_background)
    final_clip.write_videofile(outname,fps=fps)

>>> caption = yt.captions.get_by_language_code('en')
>>> print(caption.generate_srt_captions())
"""


def vid_or_audio():
    choice = ''
    while choice != 'a' and choice != 'v':
        choice = input('Audio(a) or Video(v) > ')
        print('\n')
        match choice.lower():
            case 'v':
                return 'video'
            case 'a':
                return 'audio'


def quality(yt, type):
    if type == 'video':
        viddict = {}
        for stream in yt.streams.filter(type=type, progressive=True):
            print(stream.resolution)
            viddict.setdefault(stream.resolution, stream.itag)
        while True:
            resolution = input('\nchoose resolution >> ')
            if resolution in viddict.keys():
                break
            else:
                print('enter a valid resolution')
        return viddict.get(resolution)
    elif type == 'audio':
        audiodict = {}
        for stream in yt.streams.filter(file_extension='mp4', type=type):
            audiodict.setdefault(stream.abr, stream.itag)
            print(stream.abr)
        while True:
            bitrate = input('\nchoose bitrate >> ')
            if bitrate in audiodict.keys():
                break
            else:
                print('enter a valid bitrate')
        return audiodict.get(bitrate)

# this func i don't fully understand it
def on_progress(vid, chunk, bytes_remaining):
    total_size = vid.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    totalsz = (total_size/1024)/1024
    totalsz = round(totalsz,1)
    remain = (bytes_remaining / 1024) / 1024
    remain = round(remain, 1)
    dwnd = (bytes_downloaded / 1024) / 1024
    dwnd = round(dwnd, 1)
    percentage_of_completion = round(percentage_of_completion,2)
    print(f'Download Progress: {percentage_of_completion}%, Total Size:{totalsz} MB, Downloaded: {dwnd} MB, Remaining:{remain} MB')


def main():
    ytlink = input('link >> ')
    yt = YouTube(ytlink, on_progress_callback=on_progress)
    print('\n', yt.title, '\n')
    type = vid_or_audio()
    stream_tag = quality(yt, type)
    stream = yt.streams.get_by_itag(stream_tag)
    output_path = input('output path (default : same directory) >> ')
    if output_path == '':
        output_path = './output/'
    
    stream.download(output_path=output_path)

    # if type == 'video':
    #     name = stream.title + f'({stream.resolution})' + '.mp4'
    #     stream.download(output_path=output_path, filename=name)
    # elif type == 'audio':
    #     stream.download(output_path=output_path)
    #     if os.path.exists(f'{output_path}{stream.title}.mp4'):
    #         input_file = f'{output_path}{stream.title}.mp4'
    #         output_file = f'{output_path}{stream.title}.mp3'
    #         input_file_encoded = input_file.encode('utf-8')  # Encode filename to UTF-8
    #         output_file_encoded = output_file.encode('utf-8')  # Encode filename to UTF-8
    #         (
    #             ffmpeg.input(input_file_encoded.decode('utf-8'))  # Decode filename to string
    #             .output(output_file_encoded.decode('utf-8'))  # Decode filename to string
    #             .run(overwrite_output=True)
    #         )
    #         os.remove(input_file)

    print('\nDone ...')


main()
