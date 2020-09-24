from urllib.request import urlopen, Request, URLError, urlretrieve, HTTPError
from urllib.parse import quote
from bs4 import BeautifulSoup
import logging
import hashlib
import re

#DIR2 = 'C:/tmp/'
BASE_URL = 'http://assets.languagepod101.com/dictionary/japanese/audiomp3.php?kanji='
WANI_URL = 'https://www.wanikani.com/vocabulary/'

def configure_logging():
    logger = logging.getLogger("audio_logger")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('[%(module)s]: %(message)s'))
    logger.addHandler(handler)
    Filehandler = logging.FileHandler("C:/users/public/image_downloader_log.txt") #Path to your LOG FILE.
    Filehandler.setFormatter(
        logging.Formatter('[%(module)s]: %(message)s'))
    logger.addHandler(Filehandler)
    return logger

logger = configure_logging()

def audioDownloadWani(kanji):
    kanji = re.sub('<[^<]+?>', '', kanji) # Remove trailing html
    url = WANI_URL + quote(kanji)

    # Souping
    try:
        response = urlopen(Request(url))
    except HTTPError:
        logger.info(f'Exception occured returning (None,None)...')
        return (None,None)
    soup = BeautifulSoup(response, 'html.parser')
    logger.info('Getting sound elements...')
    mp3_url_matches = re.findall(r'(?:http(?:s?):)(?:[/|.|\w|\s|-])*\.(?:mp3)',str(soup))
    # Check matches
    if mp3_url_matches:
        url = mp3_url_matches[0] # We go with the first mp3 (lady voice)
    else:
        return (None,None)
    # Filename
    filename = u'wanikani_{}'.format(kanji)
    filename += u'.mp3'
    logger.info(f"Filename: {filename}")
    # Get file from url
    try:
        logger.info(f'Opening url for {kanji}...')
        resp = urlopen(url)
        #urlretrieve(url, DIR2 + filename) # Downloads file
        raw_sound = resp.read()
        return (raw_sound, filename)
    except URLError:
        logger.info(f'Exception occured returning (None,None)...')
        return (None,None)

def audioDownloadYomi(kana, kanji):
    kana = re.sub('<[^<]+?>', '', kana) # Remove trailing html
    kanji = re.sub('<[^<]+?>', '', kanji) # Remove trailing html
    url = BASE_URL + quote(kanji)
    # Filename
    filename = u'yomichan_{}'.format(kana)
    if kanji:
        filename += u'_{}'.format(kanji)
    filename += u'.mp3'
    logger.info(f"Filename: {filename}")
    if kana:
        url += u'&kana={}'.format(quote(kana))
    # Get file from url
    try:
        logger.info(f'Opening url for {kana}...')
        resp = urlopen(url)
        #urlretrieve(url, DIR2 + filename)
        raw_sound = resp.read()
        return (raw_sound, filename)
    except URLError:
        logger.info(f'Exception occured returning (None,None)...')
        return (None,None)

def audioIsPlaceholder(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest() == '7e2c2f954ef6051373ba916f000168dc'

def audioDownload(kana, kanji):
    # Test downloading from yomichan
    (sound_data, filename) = audioDownloadYomi(kana,kanji)
    # Check if placeholder
    if audioIsPlaceholder(sound_data):
        logger.info(f"No sound found (Yomichan) {(kana, kanji)}")
        # Test downloading from wanikani
        (sound_data, filename) = audioDownloadWani(kanji)
        if sound_data == None:
            logger.info(f"No sound found (Wanikani) {(kana, kanji)}")
            return (None, None)
        else:
            logger.info(f"Sound found (Wanikani) {(kana, kanji)}")
            return (sound_data, filename)
    else:
        logger.info(f"Sound found (Yomichan) {(kana, kanji)}")
        return (sound_data, filename)

if __name__ == "__main__":
    print("testing...")
    audioDownload('おとこ','男')
    audioDownload('ちょうしゅ','聴取')
    audioDownload('test', 'hej')
    audioDownload('いつごろ', 'いつ頃')
    audioDownload('はくしてっかい', '白紙撤回')
    


