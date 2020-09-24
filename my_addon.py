# -*- coding: utf-8 -*-

from aqt.qt import *
from anki.hooks import addHook
from aqt import mw
from aqt.utils import showInfo
from .download_audio_21 import audioDownload

def show_cardCount():
    cardCount = mw.col.cardCount()
    showInfo("Card count: %d" % cardCount)

def append_hello(nids):
    mw.checkpoint("Append Hello")
    mw.progress.start()
    for nid in nids:
        note = mw.col.getNote(nid)
        note['Vocabulary-Pos'] = 'hello?'
        note.flush()
    mw.progress.finish()
    mw.reset()

def add_audioTest(nids):
    mw.checkpoint("Download Audio")
    mw.progress.start()
    for nid in nids:
        note = mw.col.getNote(nid)
        (data, file_name) = audioDownload(note['Vocabulary-Kana'], note['Vocabulary-Kanji-Plain'])
        mw.col.media.writeData(file_name, data)
        note['Vocabulary-Audio'] = u'[sound:{}]'.format(file_name)
        note.flush()
    mw.progress.finish()
    mw.reset()

def setupBrowserMenu(browser):
    """ Add entry to browser window """
    do_show_cardCount = QAction("Show Card Count", mw) # create menu item
    do_show_cardCount.triggered.connect(show_cardCount) # call function when triggered
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(do_show_cardCount)

    """ Add entry to browser window """
    do_append_hello = QAction("Append Hello", mw) # create menu item
    do_append_hello.triggered.connect(lambda: onAppend(browser)) # call function when triggered
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(do_append_hello)

    """ Add entry to browser window """
    do_add_audio = QAction("Add Audio", mw) # create menu item
    do_add_audio.triggered.connect(lambda: onAddAudio(browser)) # call function when triggered
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(do_add_audio)

def onAppend(browser):
    append_hello(browser.selectedNotes())

def onAddAudio(browser):
    add_audioTest(browser.selectedNotes())

addHook("browser.setupMenus", setupBrowserMenu)