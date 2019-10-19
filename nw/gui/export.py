# -*- coding: utf-8 -*-
"""novelWriter GUI Export Tools

 novelWriter – GUI Export Tools
================================
 Tool for exporting project files to other formats

 File History:
 Created: 2019-10-13 [0.2.3]

"""

import logging
import time
import json
import nw

from os import path

from PyQt5.QtCore    import Qt, QSize
from PyQt5.QtSvg     import QSvgWidget
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QWidget, QTabWidget, QGridLayout, QGroupBox, QCheckBox,
    QLabel, QComboBox, QLineEdit, QPushButton, QFileDialog, QProgressBar
)

from nw.project.document import NWDoc
from nw.tools.translate  import numberToWord
from nw.convert.textfile import TextFile
from nw.common           import checkString, checkBool, checkInt
from nw.constants        import nwFiles
from nw.enum             import nwItemType

logger = logging.getLogger(__name__)

class GuiExport(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiExport ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.optState   = ExportLastState(self.theProject)

        self.outerBox   = QHBoxLayout()
        self.innerBox   = QVBoxLayout()
        self.setWindowTitle("Export Project")
        self.setLayout(self.outerBox)

        self.gradPath = path.abspath(path.join(self.mainConf.appPath,"graphics","export.svg"))
        self.svgGradient = QSvgWidget(self.gradPath)
        self.svgGradient.setFixedSize(QSize(64,64))

        self.theProject.countStatus()
        self.tabMain   = GuiExportMain(self.theParent, self.theProject, self.optState)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.tabMain, "Settings")

        self.outerBox.addWidget(self.svgGradient, 0, Qt.AlignTop)
        self.outerBox.addLayout(self.innerBox)

        self.doExportForm = QGridLayout()
        self.doExportForm.setContentsMargins(10,5,0,10)

        self.exportButton = QPushButton("Export")
        self.exportButton.clicked.connect(self._doExport)

        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self._doClose)

        self.exportStatus   = QLabel("Ready ...")
        self.exportProgress = QProgressBar(self)

        self.doExportForm.addWidget(self.exportStatus,   0, 0, 1, 3)
        self.doExportForm.addWidget(self.exportProgress, 1, 0)
        self.doExportForm.addWidget(self.exportButton,   1, 1)
        self.doExportForm.addWidget(self.closeButton,    1, 2)

        self.innerBox.addWidget(self.tabWidget)
        self.innerBox.addLayout(self.doExportForm)

        self.rejected.connect(self._doClose)
        self.show()

        logger.debug("GuiExport initialisation complete")

        return

    ##
    #  Buttons
    ##

    def _doExport(self):

        logger.verbose("GuiExport export button clicked")

        wNovel    = self.tabMain.expNovel.isChecked()
        wNotes    = self.tabMain.expNotes.isChecked()
        eFormat   = self.tabMain.outputFormat.currentData()
        wComments = self.tabMain.outputComments.isChecked()
        chFormat  = self.tabMain.chapterFormat.text()
        unFormat  = self.tabMain.unnumFormat.text()
        scFormat  = self.tabMain.sceneFormat.text()
        seFormat  = self.tabMain.sectionFormat.text()
        saveTo    = self.tabMain.exportPath.text()

        nItems = len(self.theProject.treeOrder)
        self.exportProgress.setMinimum(0)
        self.exportProgress.setMaximum(nItems)
        self.exportProgress.setValue(0)

        if not wNovel and not wNotes:
            self.exportStatus.setText("Nothing to export ...")
            return False

        outFile = None
        if eFormat == GuiExportMain.FMT_TXT:
            outFile = TextFile(self.theProject, self.theParent)

        if outFile is None:
            return False

        if outFile.openFile(saveTo):
            outFile.setComments(wComments)
            outFile.setExportNovel(wNovel)
            outFile.setExportNotes(wNotes)
            outFile.setChapterFormat(chFormat)
            outFile.setUnNumberedFormat(unFormat)
            outFile.setSceneFormat(scFormat)
            outFile.setSectionFormat(seFormat)
        else:
            self.exportStatus.setText("Failed to open file for writing ...")
            return False

        nDone = 0
        for tHandle in self.theProject.treeOrder:

            time.sleep(0.1)

            self.exportProgress.setValue(nDone)
            tItem = self.theProject.getItem(tHandle)

            self.exportStatus.setText("Exporting: %s" % tItem.itemName)
            logger.verbose("Exporting: %s" % tItem.itemName)

            if tItem is not None and tItem.itemType == nwItemType.FILE:
                outFile.addText(tHandle)

            nDone += 1

        outFile.closeFile()

        self.exportProgress.setValue(nDone)
        self.exportStatus.setText("Export to %s complete" % outFile.fileName)
        logger.verbose("Export to %s complete" % outFile.fileName)

        return

    def _doClose(self):

        logger.verbose("GuiExport close button clicked")

        wNovel    = self.tabMain.expNovel.isChecked()
        wNotes    = self.tabMain.expNotes.isChecked()
        wTOC      = self.tabMain.expTOC.isChecked()
        eFormat   = self.tabMain.outputFormat.currentData()
        wComments = self.tabMain.outputComments.isChecked()
        chFormat  = self.tabMain.chapterFormat.text()
        unFormat  = self.tabMain.unnumFormat.text()
        scFormat  = self.tabMain.sceneFormat.text()
        seFormat  = self.tabMain.sectionFormat.text()
        saveTo    = self.tabMain.exportPath.text()

        self.optState.setSetting("wNovel",   wNovel)
        self.optState.setSetting("wNotes",   wNotes)
        self.optState.setSetting("wTOC",     wTOC)
        self.optState.setSetting("eFormat",  eFormat)
        self.optState.setSetting("wComments",wComments)
        self.optState.setSetting("chFormat", chFormat)
        self.optState.setSetting("unFormat", unFormat)
        self.optState.setSetting("scFormat", scFormat)
        self.optState.setSetting("seFormat", seFormat)
        self.optState.setSetting("saveTo",   saveTo)

        self.optState.saveSettings()
        self.close()

        return

# END Class GuiExport

class GuiExportMain(QWidget):

    FMT_TXT   = 1
    FMT_MD    = 2
    FMT_HTML  = 3
    FMT_EBOOK = 4
    FMT_ODT   = 5
    FMT_TEX   = 6
    FMT_EXT   = {
        FMT_TXT   : ".txt",
        FMT_MD    : ".md",
        FMT_HTML  : ".htm",
        FMT_EBOOK : ".htm",
        FMT_ODT   : ".odt",
        FMT_TEX   : ".tex",
    }
    FMT_HELP  = {
        FMT_TXT : (
            "Exports a plain text file. "
            "All formatting is stripped and comments are in square brackets."
        ),
        FMT_MD : (
            "Exports a standard markdown file. "
            "Comments are converted to preformatted text blocks."
        ),
        FMT_HTML : (
            "Exports a plain html5 file. "
            "Comments are converted to preformatted text blocks."
        ),
        FMT_EBOOK : (
            "Exports an html5 file that can be converted to eBook with Calibre. "
            "Comments are not exported in this format."
        ),
        FMT_ODT : (
            "Exports an open document file that can be read by office applications. "
            "Comments are exported as grey text."
        ),
        FMT_TEX : (
            "Exports a LaTeX file that can be compiled to PDF using for instance PDFLaTeX. "
            "Comments are exported as LaTeX comments."
        ),
    }

    def __init__(self, theParent, theProject, optState):
        QWidget.__init__(self, theParent)

        self.theParent  = theParent
        self.theProject = theProject
        self.theTheme   = theParent.theTheme
        self.outerBox   = QGridLayout()
        self.optState   = optState
        self.currFormat = self.FMT_TXT

        # Select Files
        self.guiFiles     = QGroupBox("Export Files", self)
        self.guiFilesForm = QGridLayout(self)
        self.guiFiles.setLayout(self.guiFilesForm)

        self.expNovel = QCheckBox(self)
        self.expNotes = QCheckBox(self)
        self.expTOC   = QCheckBox(self)
        self.expNovel.setToolTip("Include all novel files in the exported document")
        self.expNotes.setToolTip("Include all note files in the exported document")
        self.expTOC.setToolTip("Generate a Table of Contents (ToC)")
        self.expNovel.setChecked(self.optState.getSetting("wNovel"))
        self.expNotes.setChecked(self.optState.getSetting("wNotes"))
        self.expTOC.setChecked(self.optState.getSetting("wTOC"))

        self.guiFilesForm.addWidget(QLabel("Novel files"), 0, 0)
        self.guiFilesForm.addWidget(self.expNovel,         0, 1)
        self.guiFilesForm.addWidget(QLabel("Note files"),  1, 0)
        self.guiFilesForm.addWidget(self.expNotes,         1, 1)
        self.guiFilesForm.addWidget(QLabel("ToC"),         2, 0)
        self.guiFilesForm.addWidget(self.expTOC,           2, 1)

        # Chapter Settings
        self.guiChapters     = QGroupBox("Chapter Headings", self)
        self.guiChaptersForm = QGridLayout(self)
        self.guiChapters.setLayout(self.guiChaptersForm)

        self.chapterFormat = QLineEdit()
        self.chapterFormat.setText(self.optState.getSetting("chFormat"))
        self.chapterFormat.setToolTip("Available formats: %num%, %numword%, %title%")
        self.chapterFormat.setMinimumWidth(250)

        self.unnumFormat = QLineEdit()
        self.unnumFormat.setText(self.optState.getSetting("unFormat"))
        self.unnumFormat.setToolTip("Available formats: %title%")
        self.unnumFormat.setMinimumWidth(250)

        self.guiChaptersForm.addWidget(QLabel("Numbered"),   0, 0)
        self.guiChaptersForm.addWidget(self.chapterFormat,   0, 1)
        self.guiChaptersForm.addWidget(QLabel("Unnumbered"), 1, 0)
        self.guiChaptersForm.addWidget(self.unnumFormat,     1, 1)

        # Scene and Section Settings
        self.guiScenes     = QGroupBox("Other Headings", self)
        self.guiScenesForm = QGridLayout(self)
        self.guiScenes.setLayout(self.guiScenesForm)

        self.sceneFormat = QLineEdit()
        self.sceneFormat.setText(self.optState.getSetting("scFormat"))
        self.sceneFormat.setToolTip("Available formats: %title%")
        self.sceneFormat.setMinimumWidth(100)

        self.sectionFormat = QLineEdit()
        self.sectionFormat.setText(self.optState.getSetting("seFormat"))
        self.sectionFormat.setToolTip("Available formats: %title%")
        self.sectionFormat.setMinimumWidth(100)

        self.guiScenesForm.addWidget(QLabel("Scenes"),   0, 0)
        self.guiScenesForm.addWidget(self.sceneFormat,   0, 1)
        self.guiScenesForm.addWidget(QLabel("Sections"), 1, 0)
        self.guiScenesForm.addWidget(self.sectionFormat, 1, 1)

        # Output Path
        self.exportTo     = QGroupBox("Export Folder", self)
        self.exportToForm = QGridLayout(self)
        self.exportTo.setLayout(self.exportToForm)

        self.exportPath = QLineEdit(self.optState.getSetting("saveTo"))

        self.exportGetPath = QPushButton(self.theTheme.getIcon("folder"),"")
        self.exportGetPath.clicked.connect(self._exportFolder)

        self.exportToForm.addWidget(QLabel("Save to"),  0, 0)
        self.exportToForm.addWidget(self.exportPath,    0, 1)
        self.exportToForm.addWidget(self.exportGetPath, 0, 2)

        # Output Format
        self.guiOutput     = QGroupBox("Output", self)
        self.guiOutputForm = QGridLayout(self)
        self.guiOutput.setLayout(self.guiOutputForm)

        self.outputComments = QCheckBox("include comments", self)
        self.outputComments.setChecked(self.optState.getSetting("wComments"))

        self.outputHelp = QLabel("")
        self.outputHelp.setWordWrap(True)
        self.outputHelp.setMinimumHeight(55)
        self.outputHelp.setAlignment(Qt.AlignTop)

        self.outputFormat = QComboBox(self)
        self.outputFormat.addItem("Plain Text",    self.FMT_TXT)
        # self.outputFormat.addItem("Markdown",      self.FMT_MD)
        # self.outputFormat.addItem("HTML5 (Plain)", self.FMT_HTML)
        # self.outputFormat.addItem("HTML5 (eBook)", self.FMT_EBOOK)
        # self.outputFormat.addItem("Open Document", self.FMT_ODT)
        # self.outputFormat.addItem("LaTeX (PDF)",   self.FMT_TEX)
        self.outputFormat.currentIndexChanged.connect(self._updateFormat)

        optIdx = self.outputFormat.findData(self.optState.getSetting("eFormat"))
        if optIdx != -1:
            self.outputFormat.setCurrentIndex(optIdx)
            self._updateFormat(optIdx)

        self.guiOutputForm.addWidget(QLabel("Export format"), 0, 0)
        self.guiOutputForm.addWidget(self.outputFormat,       0, 1)
        self.guiOutputForm.addWidget(self.outputComments,     0, 2)
        self.guiOutputForm.addWidget(self.outputHelp,         1, 0, 1, 3)
        self.guiOutputForm.setColumnStretch(2, 1)

        # Assemble
        self.outerBox.addWidget(self.guiFiles,    0, 0)
        self.outerBox.addWidget(self.guiOutput,   0, 1, 1, 2)
        self.outerBox.addWidget(self.guiChapters, 1, 0, 1, 2)
        self.outerBox.addWidget(self.guiScenes,   1, 2)
        self.outerBox.addWidget(self.exportTo,    2, 0, 1, 3)
        self.outerBox.setColumnStretch(0, 1)
        self.outerBox.setColumnStretch(1, 1)
        self.outerBox.setColumnStretch(2, 1)
        self.setLayout(self.outerBox)

        return

    ##
    #  Internal Functions
    ##

    def _updateFormat(self, currIdx):
        """Update help text under output format selection and file extension in file box
        """
        if currIdx == -1:
            self.outputHelp.setText("")
        else:
            self.currFormat = self.outputFormat.itemData(currIdx)
            self.outputHelp.setText("<i>%s</i>" % self.FMT_HELP[self.currFormat])
            self._checkFileExtension()
        return

    def _exportFolder(self):

        currDir = self.exportPath.text()
        if not path.isdir(currDir):
            currDir = ""

        extFilter = [
            "Text files (*.txt)",
            "Markdown files (*.md)",
            "HTML files (*.htm *.html)",
            "Open document files (*.odt)",
            "LaTeX files (*.tex)",
        ]

        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.ShowDirsOnly
        dlgOpt |= QFileDialog.DontUseNativeDialog
        saveTo  = QFileDialog.getSaveFileName(
            self,"Export File",self.exportPath.text(),options=dlgOpt,filter=";;".join(extFilter)
        )
        if saveTo:
            self.exportPath.setText(saveTo[0])
            self._checkFileExtension()
            return True

        return False

    def _checkFileExtension(self):
        saveTo   = self.exportPath.text()
        fileBits = path.splitext(saveTo)
        if self.currFormat > 0:
            saveTo = fileBits[0]+self.FMT_EXT[self.currFormat]
        self.exportPath.setText(saveTo)
        return

# END Class GuiExportMain

class ExportLastState():

    def __init__(self, theProject):
        self.theProject = theProject
        self.theState   = {
            "wNovel"    : True,
            "wNotes"    : False,
            "wTOC"      : True,
            "eFormat"   : 2,
            "wComments" : False,
            "chFormat"  : "Chapter %numword%",
            "unFormat"  : "%title%",
            "scFormat"  : "* * *",
            "seFormat"  : "",
            "saveTo"    : "",
        }
        self.stringOpt = ("chFormat","unFormat","scFormat","seFormat","saveTo")
        self.boolOpt   = ("wNovel","wNotes","wTOC","wComments")
        self.intOpt    = ("eFormat")
        self.loadSettings()
        return

    def loadSettings(self):
        stateFile = path.join(self.theProject.projMeta, nwFiles.EXPORT_OPT)
        theState  = {}
        if path.isfile(stateFile):
            logger.debug("Loading export options file")
            try:
                with open(stateFile,mode="r") as inFile:
                    theJson = inFile.read()
                theState = json.loads(theJson)
            except Exception as e:
                logger.error("Failed to load export options file")
                logger.error(str(e))
                return False
        for anOpt in theState:
            self.theState[anOpt] = theState[anOpt]
        return True

    def saveSettings(self):
        stateFile = path.join(self.theProject.projMeta, nwFiles.EXPORT_OPT)
        logger.debug("Saving export options file")
        try:
            with open(stateFile,mode="w+") as outFile:
                outFile.write(json.dumps(self.theState, indent=2))
        except Exception as e:
            logger.error("Failed to save export options file")
            logger.error(str(e))
            return False
        return True

    def setSetting(self, setName, setValue):
        if setName in self.theState:
            self.theState[setName] = setValue
        else:
            return False
        return True

    def getSetting(self, setName):
        if setName in self.stringOpt:
            return checkString(self.theState[setName],self.theState[setName],False)
        elif setName in self.boolOpt:
            return checkBool(self.theState[setName],self.theState[setName],False)
        elif setName in self.intOpt:
            return checkInt(self.theState[setName],self.theState[setName],False)
        return None

# END Class ExportLastState
