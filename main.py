from pytubefix import YouTube, Playlist
import os
from audio_convert import convert
from metadata_to_audio import add_meta
from video_merge import merge
from captions import get_captions

def vid_or_audio():
    choice = ''
    while choice.lower() not in ['a', 'v', 'audio', 'video']:
        choice = input('Audio(a) or Video(v) > ')
        print('\n')
    return 'audio' if choice.lower() in ['a', 'audio'] else 'video'


def quality(yt, type):
    if type == 'video':
        resolutiondict = {}
        for stream in yt.streams.filter(only_video=True, video_codec='vp9'):
            print(stream.resolution)
            resolutiondict.setdefault(stream.resolution, stream.itag)
        while resolutiondict != {}:
            resolution = input('\nchoose resolution >> ')
            if resolution in resolutiondict.keys():
                break
            else:
                print('enter a valid resolution')
        if resolutiondict != {}:
            return resolutiondict.get(resolution)
        else:
            print('!! No vp9 codec found\n ** the script will download the highest resolution automatically')
            return False
    
    
def playlist_quality(plist, type):
    if type == 'video':
        print('Please wait while requesting the resolutions... ')
        resolutiondict = {}
        for vid in plist.videos:
            yt = YouTube(vid.watch_url, on_progress_callback=on_progress)
            yt.bypass_age_gate()
            for stream in yt.streams.filter(only_video=True, video_codec='vp9'):
                resolutiondict.update({stream.resolution : stream.itag})

        for resolution in resolutiondict.keys():
            print(resolution)
        
        while resolutiondict != {}:
            resolution = input('\nchoose resolution >> ')
            if resolution in resolutiondict.keys():
                break
            else:
                print('enter a valid resolution')
        if resolutiondict != {}:
            return resolutiondict.get(resolution)
        else:
            print('!! No vp9 codec found\n** the script will download the highest resolution automatically')
            return False


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
    print(f'( {percentage_of_completion}% ), Downloaded: {dwnd} MB out of {totalsz} MB ')


def caption_search(yt, output_path):
    cap = yt.caption_tracks
    if cap != []:
        choice = ''
        print('\nThere are some Captions that have been Found !!')
        for lang in cap:
            print(f"- {lang.name}")
        while choice != 'y' and choice != 'n':
            choice = input('Do you want to download these Captions? (y/n)\n>> ')
            match choice.lower():
                case 'y':
                    return get_captions(yt=yt, output_path=output_path)
                case 'n':
                    return output_path
    return output_path


def video(output_path, yt, stream):

    title = yt.title
    if '/' in yt.title:
        title = title.replace('/', '')
                
    stream.download(output_path=output_path, filename=f'{title} Video.mp4')

    audiolist = []
    for stream in yt.streams.filter(only_audio=True).order_by('abr').asc():
        audiolist.append(stream.itag)
    audiostream = yt.streams.get_by_itag(audiolist[0])
    audiostream.download(output_path=output_path, filename=f'{title} Audio.mp4')

    convert(output_folder=output_path, audio_name=f'{title} Audio')

    video_path = os.path.join(output_path, f'{title} Video.mp4')
    audio_path = os.path.join(output_path, f'{title} Audio.mp3')
    output = os.path.join(output_path, f'{title}.mp4')

    merge(video=video_path, audio=audio_path, output=output)
    

def audio(output_path, yt, stream, album=''):
    title = yt.title
    if '/' in yt.title:
        title = title.replace('/', '')

    stream.download(output_path=output_path, filename=f'{title}.mp4')
    convert(output_folder=output_path, audio_name=title)
    add_meta(file=os.path.join(output_path, title + '.mp3') ,yt=yt, output_path=output_path, album=album)


def caption_choice():
    choice = ''
    while choice.lower() not in ['y', 'n', 'yes', 'no']:
        choice = input('Do you want to download Captions if found (y/n)>> ')
        print('\n')
    return True if choice.lower() in ['y', 'yes'] else False


def grab_playlist(plist):
    captions = False
    type = vid_or_audio()
    if type == 'video':
        captions = caption_choice()
    stream_tag = playlist_quality(plist, type)

    output_path = input('output path (default : output/ ) >> ')
    if output_path == '':
        output_path = 'output/'

    output_path = os.path.join(output_path, plist.title)
    try:
        os.mkdir(output_path)
    except OSError as error:
        pass 

    counter = 0
    for vid in plist.videos:
            path = output_path
            yt = YouTube(vid.watch_url, on_progress_callback=on_progress)
            yt.bypass_age_gate()

            if captions == True:
                cap = yt.caption_tracks
                if cap != []:
                    print('\nThere are some Captions that have been Found !!')
                    path = get_captions(yt=yt, output_path=output_path)


            if stream_tag != False:
                if type == 'video':
                    try:
                        stream = yt.streams.get_by_itag(stream_tag)
                    except:
                        stream = yt.streams.get_highest_resolution()
            else:
                stream = yt.streams.get_highest_resolution()

            if type == 'audio':
                audio(output_path=path, yt=yt, stream=yt.streams.get_audio_only(), album=plist.title)
            elif type == 'video':
                video(output_path=path, yt=yt, stream=stream)
            
            counter += 1
            print(f'### Downloaded {counter} out of {plist.length}')


def playlist_checker(link):
    if "list=" in link:
        try:
            plist = Playlist(link)
            title = plist.title
            print(f"A Playlist has been found !!\n-- {title} -- ({plist.length})\nDo you want to grab the whole playlist? (y/n)")
            choice = ''
            while choice.lower() != 'y' or choice != 'n':
                choice = input('>> ')
                match choice.lower():
                    case 'y': return True
                    case 'n': return False
                    case _: print('Wrong input (y/n)')
        except:
            return False



def main():
    ytlink = input('link >> ')
    if '/playlist?list=' in ytlink:
        plist = Playlist(ytlink)
        print('Playlist:\n', plist.title, f' ({plist.length})\n')
        grab_playlist(plist)
    else:
        yt = YouTube(ytlink, on_progress_callback=on_progress)
        # yt.bypass_age_gate()
        print('\n', yt.title, '\n')
        is_playlist = playlist_checker(ytlink)

        if not is_playlist:
            type = vid_or_audio()
            stream_tag = quality(yt, type)
            if stream_tag != False:
                if type == 'video':
                    stream = yt.streams.get_by_itag(stream_tag)
            else:
                stream = yt.streams.get_highest_resolution()
            
            output_path = input('output path (default : output/ ) >> ')
            if output_path == '':
                output_path = 'output/'

            if type == 'audio':
                audio(output_path=output_path, yt=yt, stream=yt.streams.get_audio_only())
            elif type == 'video':
                output_path = caption_search(yt=yt, output_path=output_path)
                video(output_path=output_path, yt=yt, stream=stream)

        elif is_playlist:
            plist = Playlist(ytlink)
            grab_playlist(plist)

        print('\nDone ...')

main()
