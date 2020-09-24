# -*- coding: utf-8 -*-

import os, csv
from aqt.qt import *
from anki.hooks import addHook
from aqt import mw
from aqt.utils import showInfo
from .download_audio import audioDownload

config = mw.addonManager.getConfig(__name__)
ResDir = os.path.join(os.path.dirname(__file__), "resources")

""" Config values """
srcFieldKanji = config['srcFieldKanji']
dstFieldSentence = config["dstFieldSentence"]

def getWordSentence(word):
    with open(os.path.join(ResDir,'jpn_sentences.tsv'), encoding='utf-8') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            if word in row[2]:
                return row[2]
        return ""

def genSentences(nids):
    mw.checkpoint("Download Audio")
    mw.progress.start()
    for nid in nids:
        note = mw.col.getNote(nid)

        if srcFieldKanji not in note:
            showInfo(f"No source field '{srcFieldKanji}' field found for kanji")
            continue # no source kanji field
     
        if note[dstFieldSentence]:
            continue # already contains data
    
        sentence = getWordSentence(note[srcFieldKanji])

        if sentence:
            note[dstFieldSentence] = sentence
            note.flush()
        else:
            continue
    mw.progress.finish()
    mw.reset()

def setupBrowserMenu(browser):
    """ Add entry to browser window """
    do_gen_sentence = QAction("Generate Sentences", mw) # create menu item
    do_gen_sentence.triggered.connect(lambda: onGenSen(browser)) # call function when triggered
    browser.form.menuEdit.addSeparator() # add a separator to the menu
    browser.form.menuEdit.addAction(do_gen_sentence) # add action to the menu

def onGenSen(browser):
    genSentences(browser.selectedNotes()) # send note id:s as argument

addHook("browser.setupMenus", setupBrowserMenu)