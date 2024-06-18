import os
import subprocess


def merge(video, audio, output):
    command = [
        'ffmpeg',
        '-i', video,
        '-i', audio,
        '-c:v', 'copy',
        '-c:a', 'copy',
        output
    ]

    try:
        subprocess.run(command, check=True)
        print(f'\nvideo saved to ({output}) !!')
    except subprocess.CalledProcessError as e:
        print(f'Error: {e}')

    os.remove(video)
    os.remove(audio)