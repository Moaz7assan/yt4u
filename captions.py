import xml.etree.ElementTree as ET
import os

def ms_to_srt_time(ms):
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def convert_xml_to_srt(xml_file, srt_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    captions = []
    for i, p in enumerate(root.findall('.//p')):
        start_time_ms = int(p.get('t'))
        duration_ms = p.get('d')
        if duration_ms is None:
            continue  # Skip this caption if duration is missing (because auto-generated captions are pain in the ass)
        else:
            duration_ms = int(duration_ms)
        end_time_ms = start_time_ms + duration_ms
        text = p.text.strip() if p.text else ''
        
        start_time = ms_to_srt_time(start_time_ms)
        end_time = ms_to_srt_time(end_time_ms)
        
        captions.append((i + 1, start_time, end_time, text))
    
    with open(srt_file, 'w') as f:
        for index, start_time, end_time, text in captions:
            f.write(f"{index}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")


def get_captions(yt, output_path):
    title = yt.title
    if '/' in yt.title:
        title = title.replace('/', '')
    
    cap = yt.caption_tracks
    final_path = os.path.join(output_path, title)
    try:
        os.mkdir(final_path)
    except OSError as error:
        pass 
    for lang in cap:
        lang_path = os.path.join(os.path.join(output_path, title), lang.name)
        try:
            os.mkdir(lang_path)
        except OSError as error:
            pass
        lang.download(title=lang.name, output_path=lang_path, srt=False)
        convert_xml_to_srt(xml_file=f'{lang_path}/{lang.name} ({lang.code}).xml', srt_file=f'{lang_path}/{lang.name} ({lang.code}).srt')

    return final_path

