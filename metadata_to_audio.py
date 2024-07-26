from pytubefix import Channel
import urllib.request
import eyed3
import os

def add_meta(file, yt, output_path, album=''):
    title = yt.title
    if '/' in yt.title:
        title = title.replace('/', '')

    ch = Channel(url=f'https://www.youtube.com/channel/{yt.channel_id}')

    artist = ch.channel_name
    if ' - Topic' in artist:
        artistlist = artist.split(' ')
        artistlist.remove('Topic')
        artistlist.pop()
        name = None
        for word in artistlist:
            if name == None:
                name = str(word)
            else:
                name = str(name) + ' ' + str(word)
        artist = name
    
    # if 'VEVO' in artist:
    #     artistlist = artist.split()
    #     for i in range(4):
    #         artistlist.pop()

    #     name = ''
    #     for word in artistlist:
    #         name = str(name) + str(word)
    #     artist = name
        

    release_date = f'{yt.publish_date.year}-{yt.publish_date.month:02d}-{yt.publish_date.day:02d}'
    img_url = f'https://img.youtube.com/vi/{yt.video_id}/hqdefault.jpg'

    # Downloading the Artwork
    artwork = f"{output_path}/{title} Artwork.png"
    urllib.request.urlretrieve(img_url, artwork)


    if album == '':
        text = f'Metadata Found !\n   Artist : {artist}\n   Release Date : {release_date}\n   Artwork Found'
    else:
        text = f'Metadata Found !\n   Artist : {artist}\n   Album : {album}\n   Release Date : {release_date}\n   Artwork Found'
    print(text)

    # Adding the metadata
    audiofile = eyed3.load(file)
    audiofile.tag.artist = artist
    audiofile.tag.release_date = release_date
    with open(artwork, "rb") as cover_art:
        audiofile.tag.images.set(1, cover_art.read(), "image/png")
    if album != '':
        audiofile.tag.album = yt.title
    else:
        audiofile.tag.album = album

    audiofile.tag.save()

    print('Metadata Successfully Added !!')


    os.remove(artwork)