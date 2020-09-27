# -*- coding: utf-8 -*-

import sys, os, json
from aqt.qt import *
from anki.hooks import addHook
from aqt import mw
from aqt.utils import showInfo
from .download_audio import audioDownload
from .fetchSanseido import fetchDef

config = mw.addonManager.getConfig(__name__)
ResDir = os.path.join(os.path.dirname(__file__), "resources")

""" Config values """
srcFieldKanji = config['srcFieldKanji']
srcFieldKana = config['srcFieldKana']
dstFieldDef = config['dstFieldDef']


def getWordInfo(kanji_word):
    with open(os.path.join(ResDir, "final_dict.json"),"r",encoding='utf-8') as dict_file:
        data = json.load(dict_file)
    word_info_tuple = (data["reading"].get(kanji_word), \
                        data["vocabulary position"].get(kanji_word), \
                        data["translation"].get(kanji_word), \
                        data["frequency"].get(kanji_word), \
                        data["definition"].get(kanji_word))
    return word_info_tuple

def addDefinition(nids):
    mw.checkpoint("Download Def")
    mw.progress.start(max=len( nids ) , immediate=True) #Loading bar
    for (i, nid) in enumerate(nids):
        mw.progress.update( label='Generating Definitions...', value=i )
        note = mw.col.getNote(nid)

        if srcFieldKanji not in note:
            showInfo(f"No source field '{srcFieldKanji}' field found for kanji")
            continue # no source kanji field
     
        if dstFieldDef not in note:
            showInfo(f"No destination field '{dstFieldDef}' field found for definition")
            continue # no destination definition field
        
        if note[dstFieldDef]:
            continue # already contains data
        
        """ Daijisen """
        if "no_daijisen" not in note.tags:
            entry = getWordInfo(note[srcFieldKanji]) # get the actual definition
            if entry[4]:
                note[dstFieldDef] = entry[4] # add corresponding file name to field
            else:
                note.tags.append("no_daijisen")

        """ Sanseido """
        if "no_sanseido" not in note.tags and "no_daijisen" in note.tags:
            def_entry = fetchDef(note[srcFieldKanji]) 
            if def_entry:
                note[dstFieldDef] = def_entry
            else:
                note.tags.append("no_sanseido")
        note.flush()
    mw.progress.finish()
    mw.reset()

def setupBrowserMenu(browser):
    """ Add entry to browser window """
    do_add_def = QAction("Bulk-add Definitions", mw) # create menu item
    do_add_def.triggered.connect(lambda: onAddDef(browser)) # call function when triggered
    browser.form.menuEdit.addAction(do_add_def) # add action to the menu

def onAddDef(browser):
    addDefinition(browser.selectedNotes()) # send note id:s as argument
    mw.requireReset() # Require reset?

addHook("browser.setupMenus", setupBrowserMenu)