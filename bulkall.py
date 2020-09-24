# -*- coding: utf-8 -*-

import os, sys, json
from aqt.qt import *
from anki.hooks import addHook
from aqt import mw
from aqt.utils import showInfo
from .download_audio import audioDownload
from .download_image import imageDownload

config = mw.addonManager.getConfig(__name__)

""" Config values """
srcFieldKanji = config['srcFieldKanji']
srcFieldKana = config['srcFieldKana']
dstFieldAudio = config['dstFieldAudio']
dstFieldImage = config['dstFieldImage']
dstFieldDef = config['dstFieldDef']

ResDir = os.path.join(os.path.dirname(__file__), "resources")

def getWordInfo(kanji_word):
    with open(os.path.join(ResDir, "final_dict.json"),"r",encoding='utf-8') as dict_file:
        data = json.load(dict_file)
    word_info_tuple = (data["reading"].get(kanji_word), \
                        data["vocabulary position"].get(kanji_word), \
                        data["translation"].get(kanji_word), \
                        data["frequency"].get(kanji_word), \
                        data["definition"].get(kanji_word))
    return word_info_tuple

def addAllFiles(nids):
    mw.checkpoint("Download")
    mw.progress.start()

    """ Audio adder """
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
    
    """ Image adder """
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

    """ Definition adder """
    for nid in nids:
        note = mw.col.getNote(nid)

        if "no_daijisen" in note.tags:
            continue

        if srcFieldKanji not in note:
            showInfo(f"No source field '{srcFieldKanji}' field found for kanji")
            continue # no source kanji field
     
        if dstFieldDef not in note:
            showInfo(f"No destination field '{dstFieldDef}' field found for definition")
            continue # no destination definition field

        if note[dstFieldDef]:
            continue # already contains data
    
        entry = getWordInfo(note[srcFieldKanji]) # get the actual definition

        if entry[4]:
            note[dstFieldDef] = entry[4] # add corresponding file name to field
        else:
            #showInfo("No def found")
            note.tags.append("no_daijisen")
        note.flush()

    mw.progress.finish()
    mw.reset()

def setupBrowserMenu(browser):
    """ Add entry to browser window """
    do_add_everything = QAction("Bulk-add All", mw) # create menu item
    do_add_everything.triggered.connect(lambda: onAddAll(browser)) # call function when triggered
    browser.form.menuEdit.addAction(do_add_everything) # add action to the menu

def onAddAll(browser):
    addAllFiles(browser.selectedNotes()) # send note id:s as argument

addHook("browser.setupMenus", setupBrowserMenu)