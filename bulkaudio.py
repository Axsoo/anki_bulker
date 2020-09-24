# -*- coding: utf-8 -*-

from aqt.qt import *
from anki.hooks import addHook
from aqt import mw
from aqt.utils import showInfo
from .download_audio import audioDownload

config = mw.addonManager.getConfig(__name__)

""" Config values """
srcFieldKanji = config['srcFieldKanji']
srcFieldKana = config['srcFieldKana']
dstFieldAudio = config['dstFieldAudio']

def addAudioFiles(nids):
    mw.checkpoint("Download Audio")
    mw.progress.start()
    for nid in nids:
        note = mw.col.getNote(nid)

        if "no_sound" in note.tags:
            continue
        
        if srcFieldKana not in note:
            showInfo(f"No source field '{srcFieldKana}' field found for kana")
            continue # no source kana field

        if srcFieldKanji not in note:
            showInfo(f"No source field '{srcFieldKanji}' field found for kanji")
            continue # no source kanji field
     
        if dstFieldAudio not in note:
            showInfo(f"No destination field '{dstFieldAudio}' field found for audio")
            continue # no destination audio field

        if note[dstFieldAudio]:
            continue # already contains data
    
        (data, file_name) = audioDownload(note[srcFieldKana], note[srcFieldKanji]) # download the actual audio

        if data:
            mw.col.media.writeData(file_name, data) # write to the collection
            note[dstFieldAudio] = u'[sound:{}]'.format(file_name) # add corresponding file name to field
        else:
            #showInfo("No sound found")
            note.tags.append("no_sound")
        note.flush()
    mw.progress.finish()
    mw.reset()

def setupBrowserMenu(browser):
    """ Add entry to browser window """
    do_add_audio = QAction("Bulk-add Audio", mw) # create menu item
    do_add_audio.triggered.connect(lambda: onAddAudio(browser)) # call function when triggered
    browser.form.menuEdit.addSeparator() # add a separator to the menu
    browser.form.menuEdit.addAction(do_add_audio) # add action to the menu

def onAddAudio(browser):
    addAudioFiles(browser.selectedNotes()) # send note id:s as argument

addHook("browser.setupMenus", setupBrowserMenu)