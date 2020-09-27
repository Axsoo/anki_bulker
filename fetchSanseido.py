from bs4 import BeautifulSoup
from urllib.request import urlopen, Request, URLError, urlretrieve, HTTPError, quote
import re
import random

"""
    pulls definitions from sanseido.net's デイリーコンサイス国語辞典

    Definition fetching adapted from 'Sanseido Definitions plugin for Anki' by kqueryful
"""

def fetchDef(term):
    # Removes trailing square brackets
    searched = re.search(r'^[^\[]+',term)
    if searched:
        term = searched.group(0)
    defText = ""
    
    """ Souping for def url """
    pageUrl = "http://www.sanseido.biz/User/Dic/Index.aspx?TWords=" + quote(term.encode('utf-8')) + "&st=0&DailyJJ=checkbox"
    response = urlopen(pageUrl)
    soup = BeautifulSoup(response,'html.parser')

    """ Checking for body """
    NetDicBody = soup.find('div', class_ = "NetDicBody")
    if NetDicBody != None:
        defFinished = False
        for line in NetDicBody.children:
            if line.name == "b":
                if len(line) != 1:
                    for child in line.children:
                        if child.name == "span":
                            defFinished = True
            if defFinished:
                break
            if line.string != None and line.string != u"\n":
                defText += line.string
    defText = re.sub(r'［(?P<no>[２-９]+)］', r'<br/><br/>［\1］', defText)
    if defText:
        defText = u"<b>" + term + "</b>: " + defText

    return re.sub(r"（(?P<num>[２-９]+)）", r"<br/>（\1）", defText)

if __name__ == "__main__":
    """ Testing """
    # Existing def
    foo = fetchDef('女')
    print(foo)
    # Non-existant def
    bar = fetchDef('リース')
    print(bar)