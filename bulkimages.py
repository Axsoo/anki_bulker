# -*- coding: utf-8 -*-

from aqt.qt import *
from anki.hooks import addHook
from aqt import mw
from aqt.utils import showInfo
from .download_image import imageDownload

config = mw.addonManager.getConfig(__name__)

""" Config values """
srcFieldKanji = config['srcFieldKanji']
dstFieldImage = config['dstFieldImage']

def addImageFiles(nids):
    mw.checkpoint("Download Audio")
    mw.progress.start()
    for nid in nids:
        note = mw.col.getNote(nid)

        if srcFieldKanji not in note:
            showInfo(f"No source field '{srcFieldKanji}' field found for kanji")
            continue # no source kanji field
     
        if dstFieldImage not in note:
            showInfo(f"No destination field '{dstFieldImage}' field found for audio")
            continue # no destination image field

        if note[dstFieldImage]:
            continue # already contains data
    
        (data, file_name) = imageDownload(note[srcFieldKanji]) # download the actual image

        if data:
            mw.col.media.writeData(file_name, data) # write to the collection
            note[dstFieldImage] = '<img src="' + file_name + '" />' # make name for field
            note.flush()
        else:
            #showInfo("No sound found")
            continue 
    mw.progress.finish()
    mw.reset()

def setupBrowserMenu(browser):
    """ Add entry to browser window """
    do_add_image = QAction("Bulk-add Images", mw) #create menu item
    do_add_image.triggered.connect(lambda: onAddImages(browser)) # call function when triggered
    browser.form.menuEdit.addAction(do_add_image) # add action to the menu

def onAddImages(browser):
    addImageFiles(browser.selectedNotes()) # send note id:s as argument

addHook("browser.setupMenus", setupBrowserMenu)