import re
import requests
import random

DOWNLOAD_FOLDER = 'Downloads/'

def get_file_type(url):
    """
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    return content_type

def get_file_size(url):
    """
        Will return file size if file is valid otherwise will return 0
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_length = h.headers.get('content-length', None)
    if content_length:
        return content_length
    return 0

def is_downloadable(url):
    """
    Does the url contain a downloadable resource

    Max file size 200MB
    """
    h = requests.head(url, allow_redirects=True)
    content_type = get_file_type(url)
    file_size = get_file_size(url)
    if float(file_size) > 2e8:  # 200 mb approx
        return False

    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True


def get_filename(url):
    """
    Get filename from content-disposition
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    cd = header.get('content-disposition')
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]

def download_whole(url):
    if is_downloadable(url):
        file_name = get_filename(url)
        extension = get_file_type(url).split('/')[1]
        if not file_name:
            file_name = 'file_' + str(random.randint(1, 100)) +  '.' + extension
        
        r = requests.get(url, allow_redirects=True)
        open(DOWNLOAD_FOLDER + file_name.replace('\"', '').replace("'", '').replace(' ', ''), 'wb').write(r.content)
        print('Download complete')
    else:
        print('File cannot be downloaded')


exampleurls = [
    'https://www.youtube.com/watch?v=9bZkp7q19f0',
    'http://google.com/favicon.ico',
    'https://images.mentalfloss.com/sites/default/files/styles/mf_image_16x9/public/istock-511366776.jpg?itok=cWhdWNZ8&resize=1100x1100',
    'https://online.freemusicdownloads.world/get-file?fn=2Pac+-+Hit+%27Em+Up+%28Dirty%29+%28Official+Video%29+HD&pl=False&dt=MP4&vid=41qC3w3UUkU',
    'https://images.pexels.com/photos/658687/pexels-photo-658687.jpeg?cs=srgb&dl=beautiful-bloom-blooming-658687.jpg&fm=jpg'
]

for example in exampleurls:
    download_whole(example)