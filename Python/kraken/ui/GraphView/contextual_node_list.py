#
# Copyright 2010-2015
#

import difflib

from PySide import QtGui, QtCore

from kraken.core.maths import Vec2
from kraken.core.kraken_system import KrakenSystem

from kraken.ui.undoredo.undo_redo_manager import UndoRedoManager
from graph_commands import ConstructComponentCommand


class NodeList(QtGui.QListWidget):

    def __init__(self, parent):
        # constructors of base classes
        QtGui.QListWidget.__init__(self, parent)
        self.setObjectName('contextNodeList')
        self.installEventFilter(self)


    def eventFilter(self, object, event):
        if event.type()== QtCore.QEvent.WindowDeactivate:
            self.parent().hide()
            return True
        elif event.type()== QtCore.QEvent.FocusOut:
            self.parent().hide()
            return True

        return False


class ContextualNodeList(QtGui.QWidget):

    def __init__(self, parent):
        super(ContextualNodeList, self).__init__(parent)

        self.setFixedSize(250, 200)

        self.searchLineEdit = QtGui.QLineEdit(parent)
        self.searchLineEdit.setObjectName('contextNodeListSearchLine')
        self.searchLineEdit.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.searchLineEdit.setFocus()

        self.nodesList = NodeList(self)

        self.ks = KrakenSystem.getInstance()
        self.ks.loadComponentModules()

        self.componentClassNames = []
        for componentClassName in self.ks.getComponentClassNames():
            cmpCls = self.ks.getComponentClass(componentClassName)
            if cmpCls.getComponentType() != 'Guide':
                continue

            self.componentClassNames.append(componentClassName)

        self.nodes = None
        self.showClosestNames()
        self.searchLineEdit.textEdited.connect(self.showClosestNames)
        self.nodesList.itemClicked.connect(self.createNode)

        self.setIndex(0)

        grid = QtGui.QGridLayout()
        grid.addWidget(self.searchLineEdit, 0, 0)
        grid.addWidget(self.nodesList, 1, 0)
        self.setLayout(grid)


    def showAtPos(self, pos, graphpos, graph):
        self.graph = graph
        posx = pos.x() - self.width() * 0.1
        self.move(posx, pos.y() - 20)
        self.pos = pos
        self.graphpos = graphpos
        self.searchLineEdit.setFocus()
        self.searchLineEdit.clear()
        self.showClosestNames()
        self.show()

    def createNode(self):
        if self.nodesList.currentItem() is not None:

            componentClassName = self.nodesList.currentItem().data(QtCore.Qt.UserRole)

            # construct
            # command = ConstructComponentCommand(self.graph, componentClassName, Vec2(self.graphpos.x(), self.graphpos.y()))
            # UndoRedoManager.getInstance().addCommand(command, invokeRedoOnAdd=True)

            componentClass = self.ks.getComponentClass( componentClassName )
            component = componentClass(parent=self.graph.getRig())
            component.setGraphPos(Vec2(self.graphpos.x(), self.graphpos.y()))
            from graph_view.node import Node
            self.node = self.graph.addNode(Node(self.graph, component) )


            if self.isVisible():
                self.hide()

    def showClosestNames(self):

        self.nodesList.clear()
        fuzzyText = self.searchLineEdit.text()

        for componentClassName in self.componentClassNames:
            shortName = componentClassName.rsplit('.', 1)[-1]

            if fuzzyText != '':
                if fuzzyText.lower() not in shortName.lower():
                    continue

            item = QtGui.QListWidgetItem(shortName)
            item.setData(QtCore.Qt.UserRole, componentClassName)
            self.nodesList.addItem(item)

        self.nodesList.resize(self.nodesList.frameSize().width(), 20 * self.nodesList.count())

        self.setIndex(0)

    def setIndex(self, index):

        if index > len(self.componentClassNames):
            return

        if index >= 0:
            self.index = index
            self.nodesList.setCurrentItem(self.nodesList.item(self.index))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            if self.isVisible():
                self.searchLineEdit.clear()
                self.hide()

        elif event.key() == QtCore.Qt.Key_Up or event.key() == QtCore.Qt.Key_Down:
            if event.key() == QtCore.Qt.Key_Up:
                newIndex = self.index - 1
                if newIndex not in range(self.nodesList.count()):
                    return

                self.setIndex(self.index-1)
            elif event.key() == QtCore.Qt.Key_Down:
                newIndex = self.index+1
                if newIndex not in range(self.nodesList.count()):
                    return

                self.setIndex(self.index+1)

        elif event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            if self.isVisible():
                self.createNode()
                self.hide()

        return False


class ContextualNewNodeWidget(QtGui.QWidget):

    def __init__(self, parent, graph, objectType, pos):
        super(ContextualNewNodeWidget, self).__init__(parent)

        self.graph = graph
        self.objectType = objectType
        # self.setFixedSize(350, 300)

        defaultPath = '.'.join(self.graph.getGraphPath().split('.')[0:-1]) + "."

        self.searchLineEdit = QtGui.QLineEdit(parent)
        self.searchLineEdit.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.searchLineEdit.setFocus()
        self.searchLineEdit.installEventFilter(self)
        self.searchLineEdit.setText(defaultPath)

        grid = QtGui.QGridLayout()
        grid.addWidget(self.searchLineEdit, 0, 0)
        self.setLayout(grid)

        posx = pos.x() - self.width() * 0.1
        self.move(posx, pos.y())
        self.pos = pos
        self.show()

    def eventFilter(self, object, event):
        if event.type()== QtCore.QEvent.WindowDeactivate:
            self.close()
            return True
        elif event.type()== QtCore.QEvent.FocusOut:
            self.close()
            return True
        return False

    def createNode(self):
        executablePath = self.searchLineEdit.text()


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            if self.isVisible():
                self.close()

        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            if self.isVisible():
                self.createNode()
                self.close()
            return True
