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
        return int(content_length)
    return 0

def get_chunks(total, parts):
    """
        Given total file size and the number of parts it is to be downloaded in
        it returns the chunk ranges
    """
    start = 0
    range_size = total // parts
    end = range_size
    ranges = []
    for i in range(parts):
        #check if its the last chunk
        if i != parts - 1:
            r = 'bytes=' + str(start) + '-' + str(end)
            ranges.append(r)
            start = end
            end += range_size
        else:
            r = 'bytes=' + str(start) + '-' + str(total)
            ranges.append(r)
            
    return ranges

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
    return fname[0].replace('\"', '').replace("'", '').replace(' ', '')

def download_whole(url, head=None):
    if is_downloadable(url):
        file_name = get_filename(url)
        if not file_name:
            extension = get_file_type(url).split('/')[1]
            file_name = 'file_' + str(random.randint(1, 100)) +  '.' + extension
        
        r = requests.get(url, allow_redirects=True, stream=True)

        #In order to avoid having file in memory, it it streamed and writen in chunks
        with open(DOWNLOAD_FOLDER + file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        #downloaded file is written to a file
        #open(DOWNLOAD_FOLDER + file_name.replace('\"', '').replace("'", '').replace(' ', ''), 'wb').write(r.content)
        print('Download complete')
    else:
        print('File cannot be downloaded')

def download_chunk(url, file_name, file_range):
    r = requests.get(url, stream=True, headers={"Range": file_range})
    with open(file_name, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    print('Chunk download complete')

def combine_chunks(filenames):
    """
    """
    with open('final', 'wb') as wf:
        for filename in filenames:
            print(filename)
            with open(filename, 'rb') as rf:
                byte = rf.read(1)
                while byte:
                    wf.write(byte)
                    byte = rf.read(1)


def main():
    """
    """

    exampleurls = [
    'https://www.youtube.com/watch?v=9bZkp7q19f0',
    'http://google.com/favicon.ico',
    'https://images.mentalfloss.com/sites/default/files/styles/mf_image_16x9/public/istock-511366776.jpg?itok=cWhdWNZ8&resize=1100x1100',
    'https://online.freemusicdownloads.world/get-file?fn=2Pac+-+Hit+%27Em+Up+%28Dirty%29+%28Official+Video%29+HD&pl=False&dt=MP4&vid=41qC3w3UUkU',
    'https://images.pexels.com/photos/658687/pexels-photo-658687.jpeg?cs=srgb&dl=beautiful-bloom-blooming-658687.jpg&fm=jpg',
    'http://dl20.mihanpix.net/94/series/the.big.bang.theory/s12/The.Big.Bang.Theory.S12E01.720p.HDTV.2CH.x265.mkv'
    ]
    for example in exampleurls:
        #download_whole(example)
        h = requests.head(example, allow_redirects=True)
        header = h.headers
        filename = get_filename(example)
        if not filename:
            filename = 'file_' + str(random.randint(1, 100))

        #print('File name: {}, \n Size: {}, \n Headers: {}, \n\n'.format(filename, get_file_size(example), header))
        #download_whole(example)
        fsize = get_file_size(example)
        print('Size: {}, Chunks: {}\n\n'.format(fsize, get_chunks(fsize, 3)))

if __name__ == '__main__':
    url = 'https://online.freemusicdownloads.world/get-file?fn=2Pac+-+Hit+%27Em+Up+%28Dirty%29+%28Official+Video%29+HD&pl=False&dt=MP4&vid=41qC3w3UUkU'
    filename = get_filename(url)
    if filename == None:
        filename = 'file_' + str(random.randint(1, 100))
    
    chunks = get_chunks(get_file_size(url), 3)

    filenames = []
    for k, chunk in enumerate(chunks):
        chunknumber = filename + str(k)
        filenames.append(chunknumber)
        download_chunk(url, chunknumber, chunk)
    
    combine_chunks(filenames)


## How to handle timeouts?
## HTTP range requests to get partial file
## https://developer.mozilla.org/en-US/docs/Web/HTTP/Range_requests
## https://stackabuse.com/the-python-requests-module/c