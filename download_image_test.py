from urllib.request import urlopen, Request, urlretrieve
from urllib.parse import quote
from urllib.error import URLError
from bs4 import BeautifulSoup
import logging
import uuid
import re

DIR2 = 'C:/tmp/'
REQUEST_HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}

def configure_logging():
    logger = logging.getLogger("image_logger")
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

def get_extension(url):
    if 'jpg' in url:
        return 'jpg'
    elif 'png' in url:
        return 'png'
    else:
        return 'gif'

def sort_url_list(url_list):
    url_list = [value for value in url_list if 'gstatic' not in value] #Remove google icons
    return url_list

def imageDownload(kanji):
    # Make query url
    query = quote(kanji)
    query = '+'.join(query.split())
    url = "https://www.google.co.in/search?q=%s&source=lnms&tbm=isch" % query

    # Getting image url addresses from google
    response = urlopen(Request(url, headers=REQUEST_HEADER))
    soup = BeautifulSoup(response, 'html.parser')
    logger.info('Getting image elements...')
    img_url_matches = re.findall(r'(?:http(?:s?):)(?:[/|.|\w|\s|-])*\.(?:jpg|gif|png)',soup.text)

    # Remove bad urls
    img_url_matches = [url for url in img_url_matches if not "trans-suite" in url]
    img_url_matches = [url for url in img_url_matches if not "google" in url]
    img_url_matches = [url for url in img_url_matches if not "meaning-book" in url]
    img_url_matches = [url for url in img_url_matches if not "cidianwang.com" in url]
    img_url_matches = [url for url in img_url_matches if not "moedict.tw" in url]
    img_url_matches = [url for url in img_url_matches if not "business-textbooks.com" in url]
    img_url_matches = [url for url in img_url_matches if not "jlptsensei.com" in url]
    img_url_matches = [url for url in img_url_matches if not "japanesetest4you.com" in url]
    img_url_matches = [url for url in img_url_matches if not "otonasalone.jp" in url]

    sorted_url_list = sort_url_list(img_url_matches)
    logger.info(sorted_url_list)

    # Download images
    for url in sorted_url_list:
        try:
            logger.info("Making request (%s)", kanji)
            req = Request(url, headers=REQUEST_HEADER)
            logger.info("Opening response...")
            resp = urlopen(req, timeout=10.0) #Timeout if slower than 10 sec
            raw_image = resp.read()
            extension = get_extension(url) # Generate filename
            file_name = uuid.uuid4().hex + "." + extension 
            # urlretrieve(url, DIR2 + file_name) # Save file locally to DIR2
            return (raw_image, file_name)
        except URLError as e:
            logger.info("Authentication failed...")
        except Exception as e:
            logger.info("Other exception...")
            logger.exception(e)
        logger.info("Trying for next image...")
    return (None, '404.jpg') # If nothing is found

if __name__ == "__main__":
    
    logger.info("Testing...")
    imageDownload("隔離イラスト")


    