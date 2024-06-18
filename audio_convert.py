import os
import subprocess

def convert(output_folder, audio_name):
    file = os.path.join(output_folder, audio_name + '.mp4')
    output = os.path.join(output_folder, audio_name + '.mp3')

    command = [
            'ffmpeg',
            '-i', file,
            '-q:a', '0',        # Audio quality (0 is the best quality)
            '-map', 'a',
            output
        ]
    
    try:
        subprocess.run(command, check=True)
        print(f'\naudio saved to ({output}) !!')
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion to mp3: {e}")

    os.remove(file)

