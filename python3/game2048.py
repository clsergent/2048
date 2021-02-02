#-*- coding: utf-8 -*-

#clone of the 2048 game

__app_name__ = '2048'
__version__ = '1.0'
__author__ = 'clsergent'
__license__ = 'EUPL 1.2'

import sys
from PySide2 import QtGui, QtCore, QtWidgets
import enum
import random
from math import cos

# Environment values
COLOR_SEED = 100
GRID_SIZE = 4
RATIO_2_ON_4 = 3

# TEXT
LOST_TITLE = 'You lost'
LOST_MESSAGE = 'You lost with a score of {score}\nDo you want to play again'
ABOUT_TITLE = 'A propos'
ABOUT_MESSAGE = f'{__app_name__}\nVersion: {__version__}\nAuthor: {__author__}\nLicense: {__license__}'


class Move(enum.Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3


class Engine(object):
    """ Game core """
    def __init__(self, size=4):
        self.gridSize = size
        self.start()

    @property
    def score(self):
        return self._score

    def _compose(self, x: int, y: int, side: Move):
        if side is None or side is Move.LEFT:
            return x, y
        if side is Move.RIGHT:
            return self.gridSize - 1 - x, y
        elif side is Move.UP:
            return self.gridSize - 1 - y, x
        elif side is Move.DOWN:
            return y, self.gridSize - 1 - x

    def getGridItem(self, x, y, side=None) -> int:
        x, y = self._compose(x, y, side)

        if (0 <= x <= self.gridSize - 1) and (0 <= y <= self.gridSize - 1):
            return self._grid[x][y]
        raise OverflowError
    
    def setGridItem(self, x, y, value: int, side=None):
        x, y = self._compose(x, y, side)

        if (0 <= x <= self.gridSize - 1) and (0 <= y <= self.gridSize - 1):
            self._grid[x][y]= value
        else:
            raise OverflowError
            
    def newGridItem(self):
        """ add a new square"""
        empty_squares = []

        for x in range(self.gridSize):
            for y in range(self.gridSize):
                square= self.getGridItem(x, y)
                if square == 0:
                    empty_squares.append((x,y))

        if len(empty_squares) > 0:
            square = random.choice(empty_squares)
            self.setGridItem(square[0], square[1], random.choice((2,) * RATIO_2_ON_4 + (4,)))
            return True
        else:
            return False
    
    def start(self):
        self._score = 0
        self._grid = [[0] * self.gridSize for i in range(self.gridSize)]
        self.newGridItem()

    def testEnd(self):
        # test whether the game is over or not (which happens if no 0 remains)
        for move in Move:
            if self.moveGridItems(move, apply=False) or self.sumGridItems(move, apply=False):
                return False
        return True
    
    def moveGridItems(self, side, apply=True):
        """ move items depending on the side, and return whether the grid was modified or not """
        touched= False
        for y in range(self.gridSize):
            row = list()
            for x in range(self.gridSize):
                row.append(self.getGridItem(x, y, side))
            oldRow = list(row)
            while 0 in row:
                row.remove(0)
            row += [0]*(self.gridSize - len(row))
            
            if oldRow != row:
                touched= True

            if apply is True:
                for x in range(self.gridSize):
                    self.setGridItem(x, y, row[x], side)
        return touched
                
    def sumGridItems(self, side, apply=True):
        """ sum identical squares depending on the side, and return whether the grid was modified or not """
        touched = False
        for y in range(self.gridSize):
            row = list()
            for x in range(self.gridSize):
                row.append(self.getGridItem(x, y, side))

            oldRow= [i for i in row]
            xx = 0
            while xx < len(row)-1:
                if row[xx] == row[xx+1]:
                    row[xx] *= 2
                    row.pop(xx + 1)
                    self._score += row[xx]
                xx += 1
            
            row+=[0]*(self.gridSize - len(row))
            if oldRow != row:
                touched= True

            if apply is True:
                for x in range(self.gridSize):
                    self.setGridItem(x, y, row[x], side)
        return touched


class Square(QtWidgets.QGraphicsItem):
    """ A graphic square """
    def __init__(self, parent: QtWidgets.QGraphicsView, x: int, y: int):
        QtWidgets.QGraphicsItem.__init__(self)
        self.parent= parent
        self.x = x
        self.y = y
        self._value = 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def color(self):
        """ return a RGB color based on the square value"""
        # return int(abs(cos(value) * 256**3) + abs(sin(value+seed) * 256**2) + abs(tan(value+seed) * 256))
        return int(abs(cos(self.value + COLOR_SEED) * 256 ** 3))
        
    def boundingRect(self):
        size= self.parent.squareSize()
        return QtCore.QRectF(self.x*size[0], self.y*size[1], size[0], size[1])

    def innerRect(self):
        size = self.parent.squareSize()
        return QtCore.QRectF(self.x * size[0]+2, self.y * size[1]+2, size[0]-2, size[1]-2)

    def paint(self, painter, option, widget):
        size = self.parent.squareSize()
        # paint the square
        painter.setOpacity(0.5)
        painter.setBrush(QtGui.QColor(self.color))
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        painter.drawRoundedRect(self.innerRect(), 10, 10)

        # paint text
        painter.setOpacity(1)
        painter.setFont(QtGui.QFont("Arial", (size[0] + size[1])//6))
        painter.drawText(self.x * size[0] + 1, self.y * size[1] + 1,
                         size[0] - 1, size[1] - 1,
                         QtCore.Qt.AlignCenter, str(self.value))


class Frame(QtWidgets.QGraphicsView):
    """ Game main window """
    def __init__(self, parent=None, scene=None, grid_size=4):
        QtWidgets.QGraphicsView.__init__(self, parent)
        # attributes
        self.application = QtWidgets.QApplication.instance()
        self.scene= QtWidgets.QGraphicsScene()
        self.setScene(self.scene)
        self.engine = Engine(grid_size)
        self.squares = [[Square] * self.engine.gridSize for i in range(self.engine.gridSize)]

        for x in range(self.engine.gridSize):
            for y in range(self.engine.gridSize):
                self.squares[x][y]= Square(self, x, y)
                self.scene.addItem(self.squares[x][y])

        # window settings
        self.setWindowFlags(QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        #self.setStyleSheet('background-color: transparent;')
        self.setBackgroundBrush(QtGui.QColor(QtCore.Qt.transparent))
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setWindowTitle("2048")

        # layout and scrollbars
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

        # size
        self.setMinimumSize(100*self.engine.gridSize,75*self.engine.gridSize)
        self.resize(100*self.engine.gridSize,75*self.engine.gridSize)

        # Action settings
        self._menuBar = QtWidgets.QMenuBar(self)
        self._fileMenu = self._menuBar.addMenu('&File')
        self._aboutAction = QtWidgets.QAction('&About', self)
        self._aboutAction.triggered.connect(self.about)
        self._fileMenu.addAction(self._aboutAction)
        
        self._up= QtWidgets.QAction(self)
        self._up.setShortcut('Up')
        self._up.triggered.connect(lambda: self.move(Move.UP))
        self.addAction(self._up)
        
        self._down= QtWidgets.QAction(self)
        self._down.setShortcut('Down')
        self._down.triggered.connect(lambda: self.move(Move.DOWN))
        self.addAction(self._down)
        
        self._left= QtWidgets.QAction(self)
        self._left.setShortcut('Left')

        self._left.triggered.connect(lambda: self.move(Move.LEFT))
        self.addAction(self._left)
        
        self._right= QtWidgets.QAction(self)
        self._right.setShortcut('Right')
        self._right.triggered.connect(lambda: self.move(Move.RIGHT))
        self.addAction(self._right)

        self.update()
        self.show()

    def update(self):
        for x in range(self.engine.gridSize):
            for y in range(self.engine.gridSize):
                self.squares[x][y].value = self.engine.getGridItem(x, y)
        self.scene.update()
        self.updateIcon()
        self.application.sendPostedEvents()
        self.application.processEvents()
        self.scene.update()

    def updateTitle(self):
        if self.engine.score > 0:
            self.setWindowTitle("2048 - %i" % self.engine.score)
        else:
            self.setWindowTitle("2048")

    def updateIcon(self):
        px = self.grab(self.rect())
        self.application.setWindowIcon(QtGui.QIcon(px))
    
    def squareSize(self):
        """ return the graphic size of a square """
        return self.width() // self.engine.gridSize, self.height() // self.engine.gridSize
    
    def move(self, side: Move):
        """ move the elements according to the given side """
        if self.engine.moveGridItems(side) | self.engine.sumGridItems(side):
            self.engine.newGridItem()

        if self.engine.testEnd():
            reply = QtWidgets.QMessageBox.information(self,LOST_TITLE, LOST_MESSAGE.format(score=self.engine.score),
                                                      QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No,
                                                      QtWidgets.QMessageBox.Yes)

            if reply == QtWidgets.QMessageBox.Yes:
                self.engine.start()
            else:
                self.application.quit()
        self.updateTitle()

        self.update()
    
    def about(self, event= None) -> None:
        """  provide information about the application """
        QtWidgets.QMessageBox.about(self, ABOUT_TITLE, ABOUT_MESSAGE)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w= Frame(grid_size=GRID_SIZE)
    sys.exit(app.exec_())
