from PyQt5 import QtGui, QtCore, uic
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit
from PyQt5.QtGui import QPixmap
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import pyqtSignal, QPoint
import sys
import qrcode
import socket
import select
from _thread import *
import threading
import os
from multiprocessing import Pipe, Process
import json
from access_points import get_scanner
from wireless import Wireless



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = 0
addr = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = (socket.gethostbyname(socket.gethostname()), 10004)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

uifile = 'final.ui'
form, base = uic.loadUiType(uifile)

mainuifile = 'mainwindow.ui'
form1, base1 = uic.loadUiType(mainuifile)

list_ = []


class Colour3:
    R = 0
    G = 0
    B = 0
    #CONSTRUCTOR
    def __init__(self):
        self.R = 0
        self.G = 0
        self.B = 0
    #CONSTRUCTOR - with the values to give it
    def __init__(self, nR, nG, nB):
        self.R = nR
        self.G = nG
        self.B = nB

class Point:
    #X Coordinate Value
    X = 0
    #Y Coordinate Value
    Y = 0
    #CONSTRUCTOR
    def __init__(self):
        self.X = 0
        self.Y = 0
    #CONSTRUCTOR - with the values to give it
    def __init__(self, nX, nY):
        self.X = nX
        self.Y = nY
    #So we can set both values at the same time
    def Set(self,nX, nY):
        self.X = nX
        self.Y = nY

class Shape:
    Location = Point(0,0)
    Width = 0.0
    Colour = Colour3(0,0,0)
    ShapeNumber = 0
    #CONSTRUCTOR - with the values to give it
    def __init__(self, L, W, C, S):
        self.Location = L
        self.Width = W
        self.Colour = C
        self.ShapeNumber = S


class Shapes:
    #Stores all the shapes
    __Shapes = []
    __hover = Point(0,0)
    def __init__(self):
        self.__Shapes = []
        self.__hover = Point(0,0)
    #Returns the number of shapes being stored.
    def NumberOfShapes(self):
        return len(self.__Shapes)
    #Add a shape to the database, recording its position,
    #width, colour and shape relation information
    def NewShape(self,L,W,C,S):
        Sh = Shape(L,W,C,S)
        self.__Shapes.append(Sh)
    def getHover(self):
        return self.__hover
    def SetHover(self,P):
        self.__hover = P
    #returns a shape of the requested data.
    def GetShape(self, Index):
        return self.__Shapes[Index]
    #Removes any point data within a certain threshold of a point.
    def RemoveShape(self, L, threshold):
        #do while so we can change the size of the list and it wont come back to bite me in the ass!!
        i = 0
        while True:
            if(i==len(self.__Shapes)):
                break
            #Finds if a point is within a certain distance of the point to remove.
            if((abs(L.X - self.__Shapes[i].Location.X) < threshold) and (abs(L.Y - self.__Shapes[i].Location.Y) < threshold)):
                #removes all data for that number
                del self.__Shapes[i]
                #goes through the rest of the data and adds an extra
                #1 to defined them as a seprate shape and shuffles on the effect.
                for n in range(len(self.__Shapes)-i):
                    self.__Shapes[n+i].ShapeNumber += 1
                #Go back a step so we dont miss a point.
                i -= 1
            i += 1


class Painter(QWidget):
    Dum = 0 #we'll remove this later
    ParentLink = 0
    MouseLoc = Point(0,0)
    LastPos = Point(0,0)
    def __init__(self,parent):
        super(Painter, self).__init__()
        self.ParentLink = parent
        self.MouseLoc = Point(0,0)
        self.LastPos = Point(0,0)
    def mousePressEvent(self, event):
        if(self.ParentLink.Brush == True):
            self.ParentLink.IsPainting = True
            self.ParentLink.ShapeNum += 1
            self.LastPos = Point(0,0)
        else:
            self.ParentLink.IsEraseing = True

    def mouseMoveEven(self, event):
        if(self.ParentLink.IsPainting == True):
            self.MouseLoc = Point(event.x(),event.y())
            if((self.LastPos.X != self.MouseLoc.X) and (self.LastPos.Y != self.MouseLoc.Y)):
                self.LastPos =  Point(event.x(),event.y())
                self.ParentLink.DrawingShapes.NewShape(self.LastPos,self.ParentLink.CurrentWidth,self.ParentLink.CurrentColour,self.ParentLink.ShapeNum)
            self.repaint()
        if(self.ParentLink.IsEraseing == True):
            self.MouseLoc = Point(event.x(),event.y())
            self.ParentLink.DrawingShapes.RemoveShape(self.MouseLoc,10)
            self.repaint()
        else :
            self.MouseLoc = Point(event.x(),event.y())
            self.ParentLink.DrawingShapes.SetHover(self.MouseLoc)
            print (self.MouseLoc.X)
            self.repaint()


    def mouseReleaseEvent(self, event):
        if(self.ParentLink.IsPainting == True):
            self.ParentLink.IsPainting = False
        if(self.ParentLink.IsEraseing == True):
            self.ParentLink.IsEraseing = False

    def paintEvent(self,event):
        painter = QtGui.QPainter()
        painter.begin(self)
        self.drawLines(event, painter)
        painter.end()

    def drawLines(self, event, painter):
        painter.setRenderHint(QtGui.QPainter.Antialiasing);

        if not self.ParentLink.IsPainting and not self.ParentLink.IsEraseing :
            p = self.ParentLink.DrawingShapes.getHover()
            q = QPoint(p.X,p.Y)
            painter.drawPoint(p.X,p.Y)

        for i in range(self.ParentLink.DrawingShapes.NumberOfShapes()-1):

            T = self.ParentLink.DrawingShapes.GetShape(i)
            T1 = self.ParentLink.DrawingShapes.GetShape(i+1)

            if(T.ShapeNumber == T1.ShapeNumber):
                pen = QtGui.QPen(QtGui.QColor(T.Colour.R,T.Colour.G,T.Colour.B), T.Width/2, QtCore.Qt.SolidLine)
                painter.setPen(pen)
                painter.drawLine(T.Location.X,T.Location.Y,T1.Location.X,T1.Location.Y)

class CreateNewUI(base1,form1):
    Qim = 0
    stop_thread_signal = pyqtSignal()
    write_thread = pyqtSignal(str)
    def __init__(self):
        super(base,self).__init__()
        self.setupUi(self)
        self.Qim = QLabel()
        self.Qim.setPixmap(self.generateQR())
        self.stackedWidget.insertWidget(1,self.Qim)
        self.fillCombo()
        self.dialog = CreateUI()
        self.lineEdit.setEchoMode(QLineEdit.Password)
        self.Establish_Connections()
    def fillCombo(self):
        self.comboBox.clear()
        wifi_scanner = get_scanner()
        list1 = wifi_scanner.get_access_points()
        for i in list1:
            self.comboBox.addItem(i["ssid"])
            #print (i["ssid"])
    def generateQR(self):
        img = qrcode.make(socket.gethostbyname(socket.gethostname()))
        qim = ImageQt(img)
        pix = QPixmap.fromImage(qim)
        pix = pix.scaledToWidth(430)
        return pix
    def showImage(self):
        data = self.lineEdit.text()
        text = self.comboBox.currentText()
        wireless = Wireless()
        wireless.connect(ssid=text,password=data)
        self.stackedWidget.setCurrentIndex(1)
        #p = Process(target=self.serverthread,args=())
        #p.start()
        start_new_thread(self.serverthread,())
        self.stop_thread_signal.connect(self.changeDisplay)


    def changeDisplay(self):
        #print ("Okkay")
        self.close()
        self.dialog.show()
        #start_new_thread(self.server2thread,())
        data = 0
        self.write_thread.connect(lambda p: self.dataStore(p))

    def dataStore(self,p):
        p = json.loads(p)
        x = p["x"]
        y = p["y"]
        p = QPoint(x*1.5,y*1.5)
        print (p)
        paint = self.dialog.returnPainter()
        paint.mouseMoveEven(p)

    def Establish_Connections(self):
        self.pushButton1.clicked.connect(self.showImage)
        self.pushButton2.clicked.connect(self.closing)

    def closing(self):
        self.close()
    def serverthread(self):
        while True:
            print('waiting for a connection')
            connection, client_address = sock.accept()
            self.stop_thread_signal.emit()
            try:
                print('connection from', client_address)
                data = connection.recv(240)
                while data:
                    data=data.decode('utf-8').split('\n')
                    if data[-1] == '':
                        del data[-1]
                    for d in data:
                        #print(d),
                        m = json.loads(d)
                        self.write_thread.emit(d)
                    data = connection.recv(240)
            finally:
                connection.close()









class CreateUI(base,form):
    Brush = True
    DrawingShapes = Shapes()
    IsPainting = False
    IsEraseing = False
    CurrentColour = Colour3(0,0,0)
    CurrentWidth = 10
    ShapeNum = 0
    IsMouseing = False
    PaintPanel = 0
    def __init__(self):
        super(base,self).__init__()
        self.setupUi(self)
        self.setObjectName('Rig Helper')
        self.PaintPanel = Painter(self)
        self.PaintPanel.close()
        self.DrawingFrame.insertWidget(0,self.PaintPanel)
        self.DrawingFrame.setCurrentWidget(self.PaintPanel)
        self.Establish_Connections()

    def EraseBrush(self):
        if(self.Brush == True):
            self.Brush = False

    def DrawBrush(self):
        if(self.Brush == False):
            self.Brush = True

    def ChangeColour(self,val):
        if val == 0:
            self.CurrentColour = Colour3(0,0,0)
        elif val == 1:
            self.CurrentColour = Colour3(0,0,255)
        elif val == 2:
            self.CurrentColour = Colour3(0,255,0)
        elif val == 3:
            self.CurrentColour = Colour3(255,0,0)
        elif val == 4:
            self.CurrentColour = Colour3(255,255,0)
    def ChangeThickness(self,num):
        self.CurrentWidth = num
    def ClearSlate(self):
        self.DrawingShapes = Shapes()
        self.PaintPanel.repaint()
    def Establish_Connections(self):
        self.BrushErase_Button.clicked.connect(self.EraseBrush)
        self.BrushPen_Button.clicked.connect(self.DrawBrush)
        self.Clear_Button.clicked.connect(self.ClearSlate)
        self.Thickness_Spinner.valueChanged.connect(self.ChangeThickness)
        self.ColorChange_Button.currentIndexChanged.connect(self.ChangeColour)
    def returnPainter(self):
        return self.PaintPanel




def main():
    global PyForm
    global variable
    app = QApplication(sys.argv)
    PyForm1 = CreateNewUI()
    PyForm1.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
