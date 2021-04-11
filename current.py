import sys
import signal
import serial
import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QGridLayout,
                             QHBoxLayout, QVBoxLayout, QLCDNumber, QLabel)
import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import csv
import matplotlib.pyplot as plt
import time

diziArray=[]
temp=[]
temp1=[]
temp2=[]
class ApplicationWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFigure)

        self.initCanvas()

        self.lcd1 = QLCDNumber(self)
        self.lcd1.setStyleSheet("QWidget { background-color: rgb(100, 100, 255) }")

        self.lcd2 = QLCDNumber(self)
        self.lcd2.setStyleSheet("QWidget { background-color: rgb(100, 100, 255) }")

        self.lcd3 = QLCDNumber(self)
        self.lcd3.setStyleSheet("QWidget { background-color: rgb(100, 100, 255) }")

        startButton = QPushButton("Başla")
        startButton.clicked.connect(self.onStartButton)
        stopButton = QPushButton("Durdur")
        stopButton.clicked.connect(self.onStopButton)

        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setObjectName("progressBar")

        

        l1 = QVBoxLayout()
        l1.addWidget(self.progressBar)
        l1.addWidget(self.canvas)

        l2 = QVBoxLayout()
        l2.addWidget(startButton)
        l2.addWidget(stopButton)

        l3 = QGridLayout()
        l3.addWidget(QLabel("Süre:"), 0, 0)
        l3.addWidget(self.lcd1, 0, 1)
        l3.addWidget(QLabel("sn"), 0, 2)
        l3.addWidget(QLabel("Akım:"), 1, 0)
        l3.addWidget(self.lcd2, 1, 1)
        l3.addWidget(QLabel("mA"), 1, 2)
        l3.addWidget(QLabel("Sıcaklık:"), 2, 0)
        l3.addWidget(self.lcd3, 2, 1)
        l3.addWidget(QLabel("C"), 2, 2)

        l23 = QVBoxLayout()
        l23.addLayout(l2)
        l23.addLayout(l3)
        l23.addStretch(1)

        lMain = QHBoxLayout()
        lMain.addLayout(l1)
        lMain.addLayout(l23)

        self.setLayout(lMain)

        self.setWindowTitle("Batarya Yönetim Sistemi")

    def initCanvas(self):
        self.fig = mpl.figure.Figure(figsize=(6, 5), dpi=100)
        self.axes = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.initFigure()

    def initTime(self):
        #veri.write("*".encode())
        serData = veri.readline().decode('ascii')
        diziArray=serData.split(' , ')
        self.temp=diziArray[0]
        self.t0 = float(self.temp)

    def initFigure(self):
        self.t = np.zeros(100)
        self.y = np.zeros(100)
        self.sc = np.zeros(100)
        self.li, = self.axes.plot(self.t, self.y)
        self.axes.set_xlabel("Zaman[sn]")
        self.axes.set_ylabel("Akım[mA]")
        self.axes.set_ylim(-40, 40)

    def updateFigure(self):
        serData = veri.readline().decode('ascii')
        #print(serData)
        diziArray=serData.split(' , ')
        self.temp=diziArray[0]
        self.temp1=diziArray[1]
        self.temp2=diziArray[2]
        self.serT = self.getT()
        self.serY = self.getY()
        self.serZ = self.getZ()
        self.kp = self.kapasite()
        print(self.kp)
        
        self.progressBar.setValue(self.kp[-1])

        self.t = np.append(self.t, self.serT)
        self.t = np.delete(self.t, 0)
        self.y = np.append(self.y, self.serY)
        self.y = np.delete(self.y, 0)
        self.sc = np.append(self.sc, self.serZ)
        self.sc = np.delete(self.sc, 0)

        self.li.set_xdata(self.t)
        self.li.set_ydata(self.y)
        self.axes.set_xlim(min(self.t), max(self.t))

        self.canvas.draw()

        self.lcd1.display(self.t[99])
        self.lcd2.display(self.y[99])
        self.lcd3.display(self.sc[99])

    def kapasite(self):
        #time.sleep(11)
        soh=10000
        Csoh=1000
        ld=self.y
        print(ld)
        i=10
        
        for i in range(10,len(self.t),10):
            soh=soh-(1/Csoh)*((ld*i)-(ld*(i-10)))
            i = i+10
            Son=(100*soh)/10000
        return Son 
        

    def getT(self):
        
        return (float(self.temp))/1000

    def getY(self):
        return float(self.temp1)
        
    def getZ(self):
        return float(self.temp2)
        
        

    def onStartButton(self):
        self.initFigure()
        self.kapasite()
        self.initTime()        
        self.timer.start()

    def onStopButton(self):
        self.timer.stop()
        try:
            for i in range(len(self.data)):
                self.w.writerow(self.data[i])
            self.f.close()
        except:
            pass

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    veri = serial.Serial('com3',115200)
    app = QApplication(sys.argv)
    aw = ApplicationWindow()
    aw.show()
    app.exec_()