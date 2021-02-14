#!/usr/bin/python
#-*- coding: utf-8 -*-

#clone of the 2048 game

__app_name__= u'2048'
__version__= u'0.1.0b'
__author__= u'clsergent'

from PySide import QtGui, QtCore
import sys
import random
from math import cos, sin, tan

def TEST(*args, **kwds):
    print "### test: ###", args, kwds


class Engine(object):
    #what makes the game work
    LEFT= 0
    RIGHT= 1
    UP= 2
    DOWN= 3
    def __init__(self, size= 4):
        self._size= size
        self.start()
    
    def get(self, x, y):
        if (0 <= x <= self._size-1) and (0 <= y <= self._size-1):
            return self._grid[x][y]
        raise OverflowError
    
    def set(self, x, y, value):
        if (0 <= x <= self._size-1) and (0 <= y <= self._size-1):
            self._grid[x][y]= value
            return
        raise OverflowError
            
    def add(self):
        empty_squares= []
        for x in xrange(self._size):
            for y in xrange(self._size):
                square= self.get(x,y)
                if square == 0:
                    empty_squares.append((x,y))
        else:
            square= random.choice(empty_squares)
            self.set(square[0], square[1], random.choice((2,2,2,2,2,2,2,2,4)))
    
    def start(self):
        self._score= 0
        self._grid= [[0]*self._size for i in xrange(self._size)]
        self.add()
    
    def get_score(self):
        return self._score
    
    def end(self):
        #test wether the game is over or not (which happends if no 0 remains)
        for x in xrange(self._size):
            if 0 in self._grid[x]:
                return False
        return True
    
    def _composed_get(self, x, y, side):
            if side is Engine.LEFT:
                return self.get(x, y)
            elif side is Engine.RIGHT:
                return self.get(self._size-1-x, y)
            elif side is Engine.UP:
                return self.get(self._size-1-y, x)
            elif side is Engine.DOWN:
                return self.get(y, self._size-1-x)
            
    def _composed_set(self, x, y, value, side):
        if side is Engine.LEFT:
            return self.set(x, y, value)
        elif side is Engine.RIGHT:
            return self.set(self._size-1-x, y, value)
        elif side is Engine.UP:
            return self.set(self._size-1-y, x, value)
        elif side is Engine.DOWN:
            return self.set(y, self._size-1-x, value)
    
    def slide(self, side):
        #slide squares depending on the side
        #return wether the grid was modified or not
        touched= False
        for y in xrange(self._size):
            row=[]
            for x in xrange(self._size):
                row.append(self._composed_get(x, y, side))
            old_row= [i for i in row]
            while 0 in row:
                row.remove(0)
            row+=[0]*(self._size-len(row))
            
            if old_row != row:
                touched= True
                
            for x in xrange(self._size):
                self._composed_set(x, y, row[x], side)
        return touched
                
    def sum(self, side):
        #sum identical squares depending on the side
        #return wether the grid was modified or not
        touched= False
        for y in xrange(self._size):
            row=[]
            for x in xrange(self._size):
                row.append(self._composed_get(x, y, side))
            xx= 0
            old_row= [i for i in row]
            while xx < len(row)-1:
                if row[xx] == row[xx+1]:
                    row[xx]*=2
                    row.pop(xx+1)
                    self._score+=row[xx]
                xx+=1
            
            row+=[0]*(self._size-len(row))
            if old_row != row:
                touched= True
                
            for x in xrange(self._size):
                self._composed_set(x, y, row[x], side)
        return touched
                        
    def get_size(self):
        return self._size
    
    def print_(self, compose= 0):
        #for debbugging via terminal
        print '-'*23
        for y in xrange(self._size):
            print '|',
            for x in xrange(self._size):
                print str(self._composed_get(x, y, compose)).rjust(4),
            print '|'
        print '-'*23
    size= property(get_size)
    score= property(get_score)

class Square(QtGui.QGraphicsItem):
    #one of the 16 squares that compose the game
    class coordinnates(object):
        def __init__(self, x, y):
            self.x= x
            self.y= y
        
    def __init__(self, parent, x, y):
        self._parent= parent
        self.coords= Square.coordinnates(x, y)
        QtGui.QGraphicsItem.__init__(self, scene= self._parent.scene)
    
    def get_value(self):
        #return the value for the square
        value= self._parent.engine.get(self.coords.x, self.coords.y)
        if value > 0:
            return str(value)
        return ''
    
    def get_color(self):
        value= self._parent.engine.get(self.coords.x, self.coords.y)
        return int(abs(cos(value)*256**3) + abs(sin(value +123)*256**2) + abs(tan(value + 123)*256))
        #return int(abs(sin(value)*256**3) + abs(cos(value +123)*256**2) + abs(tan(value + 123)*256))
        #return int(abs(cos(value+123)*256**3) + abs(tan(value+123)*256**2) + abs(sin(value)*256))
        
    def boundingRect(self):
        size= self._parent.square_size()
        return QtCore.QRectF(self.coords.x*size[0], self.coords.y*size[1], size[0], size[1])
    
    def paint(self, painter, option, widget):
        size= self._parent.square_size()
        
        painter.setOpacity(0.7)
        painter.setBrush(QtGui.QColor(self.get_color()))
        painter.drawRoundedRect(self.coords.x*size[0]+2, self.coords.y*size[1]+2, size[0]-2, size[1]-2, 10, 10)
        
        painter.setOpacity(1)
        painter.setFont(QtGui.QFont("SansSerif", (size[0] + size[1])//4))
        painter.drawText(self.coords.x*size[0]+1, self.coords.y*size[1]+1, size[0]-1, size[1]-1,
                         QtCore.Qt.AlignCenter, self.get_value())
    
    
    
    
class Frame(QtGui.QGraphicsView):
    #main window
    def __init__(self, scene):
        QtGui.QGraphicsView.__init__(self)
        if type(scene) != QtGui.QGraphicsScene:
            self._scene= QtGui.QGraphicsScene()
        else:
            self._scene= scene
        self._engine= Engine()
        
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.setWindowTitle("2048")
        self.resize(400, 300)
        
        self._squares= [[0]*self._engine.size for i in xrange(self._engine.size)]
        
        for x in xrange(self._engine.size):
            for y in xrange(self._engine.size):
                self._squares[x][y]= Square(self, x, y)
                #self._scene.addItem(self._squares[x][y])
        
        self.setScene(self._scene)
        
        self._menubar = QtGui.QMenuBar(self)
        fileMenu = self._menubar.addMenu('&File')
        self._about_action = QtGui.QAction('&About', self)
        self._about_action.triggered.connect(self.about)
        fileMenu.addAction(self._about_action)
        
        self._up= QtGui.QAction(self)
        self._up.setShortcut('Up')
        self._up.triggered.connect(lambda: self.move(Engine.UP))
        
        self._down= QtGui.QAction(self)
        self._down.setShortcut('Down')
        self._down.triggered.connect(lambda: self.move(Engine.DOWN))
        
        self._left= QtGui.QAction(self)
        self._left.setShortcut('Left')
        self._left.triggered.connect(lambda: self.move(Engine.LEFT))
        
        self._right= QtGui.QAction(self)
        self._right.setShortcut('Right')
        self._right.triggered.connect(TEST)
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            self.move(Engine.UP)
        elif event.key() == QtCore.Qt.Key_Down:
            self.move(Engine.DOWN)
        elif event.key() == QtCore.Qt.Key_Left:
            self.move(Engine.LEFT)
        elif event.key() == QtCore.Qt.Key_Right:
            self.move(Engine.RIGHT)
        else:
            super(Frame, self).keyPressEvent(event)
    
    def update_title(self):
        if self._engine.score > 0:
            self.setWindowTitle("2048 - %i" %self._engine.score)
        else:
            self.setWindowTitle("2048")
    
    def square_size(self):
        #return the (length, height) that any square should have
        return self.width()//self._engine.size, self.height()//self._engine.size
    
    def move(self, side):
        #move the elements according to the given side
        add= self.engine.slide(side)
        add|= self._engine.sum(side)
        if add is True:
            self._engine.add()
        if self._engine.end() is True:
            reply = QtGui.QMessageBox.information(self, 'Perdu...', u"Vous avez perdu avec le score de %i.\nVoulez-vous recommencer" %self._engine.score,
                                           QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)

            if reply == QtGui.QMessageBox.Yes:
                self._engine.start()
            else:
                QtCore.QCoreApplication.instance().quit()
        self.update_title()

        self.update()
    
    def about(self, event= None):
        #return info about the application
        reply = QtGui.QMessageBox.about(self, u'A propos',
                                        u"%s\nVersion %s\n Copyright %s\nGPL License v3"
                                        %(__app_name__, __version__, __author__))
    
    
    def get_scene(self):
        return self._scene
    
    def get_engine(self):
        return self._engine
    
    scene= property(get_scene)
    engine= property(get_engine)

    


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w= Frame(None)
    w.show()
    print 'ready'
    sys.exit(app.exec_())
