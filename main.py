from pytube import YouTube, Channel
import os
from audio_convert import convert
from metadata_to_audio import add_meta
from video_merge import merge


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
        for stream in yt.streams.filter(only_video=True, video_codec='vp9'):
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
        audiolist = []
        for stream in yt.streams.filter(only_audio=True).order_by('abr').asc():
            audiolist.append(stream.itag)
            bitrate = stream.abr
        print(f'{bitrate} Found!\n')
        return audiolist[0]


# some math shit
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


def video(output_path, yt, stream):
    stream.download(output_path=output_path, filename=f'{yt.title} Video.mp4')

    audiolist = []
    for stream in yt.streams.filter(only_audio=True).order_by('abr').asc():
        audiolist.append(stream.itag)
    audiostream = yt.streams.get_by_itag(audiolist[0])
    audiostream.download(output_path=output_path, filename=f'{yt.title} Audio.mp4')

    convert(output_folder=output_path, audio_name=f'{yt.title} Audio')

    video_path = os.path.join(output_path, f'{yt.title} Video.mp4')
    audio_path = os.path.join(output_path, f'{yt.title} Audio.mp3')
    output = os.path.join(output_path, f'{yt.title}.mp4')

    merge(video=video_path, audio=audio_path, output=output)
    

def audio(output_path, yt, stream):
    stream.download(output_path=output_path, filename=f'{yt.title}.mp4')
    convert(output_folder=output_path, audio_name=yt.title)
    add_meta(file=os.path.join(output_path, yt.title + '.mp3') ,yt=yt, output_path=output_path)


def main():
    ytlink = input('link >> ')
    yt = YouTube(ytlink, on_progress_callback=on_progress)
    print('\n', yt.title, '\n')

    type = vid_or_audio()
    stream_tag = quality(yt, type)
    stream = yt.streams.get_by_itag(stream_tag)
    output_path = input('output path (default : output/ ) >> ')
    if output_path == '':
        output_path = 'output/'

    if type == 'audio':
        audio(output_path=output_path, yt=yt, stream=stream)
    
    if type == 'video':
        video(output_path=output_path, yt=yt, stream=stream)

    print('\nDone ...')

main()
