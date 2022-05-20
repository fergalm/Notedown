from ipdb import set_trace as idebug 

import PyQt5.QtWidgets as QtWidget
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

from glob import glob 
import mistune
import os

import syntax 
from  frmbase.flogger import log

Qt = QtCore.Qt

TEMPLATE = """
# Title

## Attendees

## Minutes

## Action Items
**Write** this app
"""

HEADER = """
<HTML>
<HEAD>
</HEAD>
<BODY>
"""

FOOTER = """
<P></P>
</BODY>
</HTML>
"""

class MarkDown(QtWidget.QWidget):
    """
    Todo:

    x Autosave2    x Ctrl Q to quit
    x [Ctrl] + [N] for new file
    o Set tabstop to 4 (currently 16?)
    o Auto indent? Interpret shift + tab
    o Interpret - [ ] as a checkbox
    o Add [Ctrl] + [F] for find in file
    o Add [Ctrl] + [?] for search
    o Don't save an unedited template
    o Adjust panel sizes
    x Syntax highlighting for editor
    o Choose editor syntax highlighting colours
    o Stylesheet for view
    o Mathmode
    o New folder
    o Drag and drop
    o Autocompletions for bullet lists
    o File manager
    o Menu bar
    o Search
    o Tags
    o Combined View/Edit
    o Delete note
    
    """
    def __init__(self):

        self.rootPath = "/home/fergal/all/markdown/notes"
        self.currentFile = None

        QtWidget.QWidget.__init__(self)
        # self.keyReleaseEvent = self.quit
        self.initLayout()
        self.filenameEdit.editingFinished.connect(self.updateFilename)

        self.configureShortcutKeys()
        self.createNewNote()
        self.editor.textChanged.connect(self.updateViewer)
        setTabWidth(self.editor, 4)

    def initLayout(self):
        self.tree = self.createFileList(self.rootPath)
        self.editor = QtWidget.QTextEdit()
        # self.viewer = QtWidget.QTextEdit()  
        # self.editor = MyQTextEdit()
        self.viewer = QtWidget.QTextBrowser()
        self.filenameEdit = QtWidget.QLineEdit()

        self.highlighter = syntax.MarkdownHighlighter(self.editor.document())
        self.viewer.setReadOnly(True)

        layout0 = QtWidget.QHBoxLayout(self)
        layout1 = QtWidget.QVBoxLayout(self)
        layout2 = QtWidget.QVBoxLayout(self)

        layout1.addWidget(self.filenameEdit)
        layout1.addWidget(self.editor)

        layout2.addWidget(QtWidget.QLabel("Search goes here"))
        layout2.addWidget(self.viewer)


        layout0.addWidget(self.tree)
        layout0.addLayout(layout1)
        layout0.addLayout(layout2)


    def configureShortcutKeys(self):
        self.quitSc = QtWidget.QShortcut(QtGui.QKeySequence("Ctrl+q"), self)
        self.quitSc.activated.connect(self.quit)

        self.newSc = QtWidget.QShortcut(QtGui.QKeySequence("Ctrl+n"), self)
        self.newSc.activated.connect(self.createNewNote)

        self.saveSc = QtWidget.QShortcut(QtGui.QKeySequence("Ctrl+s"), self)
        self.newSc.activated.connect(self.saveCurrentNote)

    def createFileList(self, path):
        fileSystem = QtWidget.QFileSystemModel()
        fileSystem.setRootPath(path)
        # fileSystem.setFilter("*.md")

        tree = QtWidget.QTreeView()
        tree.setModel(fileSystem)
        tree.setRootIndex(fileSystem.index(path))
        tree.setColumnHidden(1, True)
        tree.setColumnHidden(2, True)
        tree.setColumnHidden(3, True)

        #tree.selectionModel().currentRowChanged.connect(self.replaceNote)
        tree.selectionModel().selectionChanged.connect(self.replaceNote)
        # tree.setSizeAdjustPolicy(QtWidget.QAbstractScrollArea.AdjustToContents)

        return tree


    def createNewNote(self):
        log.info("Creating new note")
        self.saveCurrentNote()
        fn  = chooseNewFilename(self.rootPath)
        path = os.path.join(self.rootPath, fn)
        with open(path, 'w') as fp:
            fp.write(TEMPLATE)
        
        path = os.path.join(self.rootPath, fn)
        index = self.tree.model().index(path, 0)
        log.info(f"Index of new note is: {index.isValid()} {index.data()}")
        self.selectNote(fn)

        #Update the file viewer too!
        self.updateTreeView(fn)
        self.filenameEdit.setText(fn)

    def updateTreeView(self, fn):
        """Set the currently highlighted file to fn"""
        index = self.tree.model().index(fn)
        self.tree.setCurrentIndex(index)

    def replaceNote(self, dummy):
        """Save current note, load new one into editor
        
        """
        log.info(f"In replace note with {dummy}")
        try:
            index = self.tree.selectedIndexes()[0]
        except IndexError:
            return     
        path = self.tree.model().fileInfo(index).absoluteFilePath()

        log.info(f"Changing note from {self.currentFile} to {path}")
        self.saveCurrentNote()
        self.selectNote(path)
        self.filenameEdit.setText(path)

    def saveCurrentNote(self):
        if self.currentFile == None:
            return 

        log.info(f"Saving {self.currentFile}")
        text = self.editor.toPlainText()

        # print(text)
        # if text == TEMPLATE:
        #     log.info("File unchanged, not saving"
        #     )
        #     os.unlink(self.currentFile)
        #     return 
        with open(self.currentFile, 'w') as fp:
            fp.write(text)

    def selectNote(self, filepath):
        log.info(f"Selecting {filepath}")
        self.currentFile = filepath
        # with open(os.path.join(self.rootPath, filepath)) as fp:
        with open(filepath) as fp:
            text = fp.read()
        self.editor.setText(text)

    def updateViewer(self):
        log.info(f"Updating viewer")
        markdown = mistune.html(self.editor.toPlainText())
        html = HEADER + markdown + FOOTER
        self.viewer.setHtml(html)

        # linenum = self.getEditCursorLinePosition()
        linenum = self.editor.textCursor().blockNumber()

        # print(linenum, lin2)
        self.setCursorPosition(self.viewer, linenum)

    def updateFilename(self):
        oldfn = self.currentFile
        log.info(f"old {oldfn}")
        newfn = str(self.filenameEdit.text())
        log.info(f"new {newfn}")
        if newfn[-3:] != ".md":
            newfn = newfn + ".md"

        log.info(f"Changing filename from {oldfn} to {newfn}")

        self.currentFile = newfn 
        self.saveCurrentNote()
        # os.unlink(os.path.join(self.rootPath, oldfn))
        os.unlink(oldfn)

    def setCursorPosition(self, qTextEdit, row):
        log.info(f"Setting cursor position to {row}")
        cursor = qTextEdit.textCursor()
        cursor.movePosition(cursor.Start)
        
        for i in range(row):
            cursor.movePosition(cursor.NextBlock)
            # print(cursor.position())
        
        qTextEdit.setTextCursor(cursor)

    def quit(self):
        self.saveCurrentNote()
        self.hide()



def chooseNewFilename(rootPath):
    flist = glob(os.path.join(rootPath, "Untitled*.md"))
    num = len(flist) + 1
    fn = "Untitled%02i.md" %(num)
    return os.path.join(rootPath, fn)


def setTabWidth(textEditor, size):
    fontMetric = QtGui.QFontMetrics(textEditor.currentCharFormat().font())
    fontWidth = fontMetric.averageCharWidth()
    textEditor.setTabStopWidth(size * fontWidth)



    
def main():
    m = MarkDown()
    m.show()
    return m
