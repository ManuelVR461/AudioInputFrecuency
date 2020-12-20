from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
import pyaudio
import time
import threading
import numpy as np
import struct
import wave


pg.setConfigOptions(antialias=True)

class Window(QMainWindow): 
    CHUNK = 4096
    RATE = 44100
    T = 1/RATE
    seguir = True
    frames = []
    WIDTH = 2
    CHANNELS = 2
    
    data_input_senal = pyqtSignal(np.ndarray)

    def __init__(self): 
        super().__init__() 
        self.p = pyaudio.PyAudio()
        self.setWindowTitle("Audio Master ") 
        self.setGeometry(100, 100, 400, 300)
        self.ejecutando = True
        self.setLayoutApp()
        self.initPlot()
        self.fps = 0
        self.timeAnt =  0
        self.timeTcpAnt = 0
        self.data_input_senal.connect(self.setDataPlotSenal)
        recorder = threading.Thread(name='Cronometro', target=self.openStream)
        recorder.start()
        self.show()


    def setLayoutApp(self):
        centralWidget = QWidget()
        p = centralWidget.palette()
        p.setColor(centralWidget.backgroundRole(), pg.mkColor('k'))
        centralWidget.setPalette(p)

        fcentral = QVBoxLayout()
        gcentral = QGroupBox("Forma de Onda")
        filas = QVBoxLayout()

        self.plt1 = pg.PlotWidget()
        filas.addWidget(self.plt1)

        gcentral.setLayout(filas)
        fcentral.addWidget(gcentral)
        centralWidget.setLayout(fcentral)
        self.setCentralWidget(centralWidget)
        
        
    def initPlot(self):
        self.plt1.setYRange(-10000, 10000)
        self.plt1.showAxis('bottom', False)
        self.plt1.showAxis('left', False)

    @pyqtSlot(np.ndarray)
    def setDataPlotSenal(self, data):
        self.plt1.plot(data,pen=(255,0,0),clear=True)


    def closeEvent(self, event):
        res = QMessageBox.question(self,"Salir ...","Seguro que quieres cerrar",QMessageBox.Yes|QMessageBox.No)
        if res==QMessageBox.Yes:
            self.ejecutando = False
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            QApplication.quit()

    def callback(self, in_data, frame_count, time_info, status):
    #     data = np.fromstring(in_data, dtype=np.int16)
    #     timeFact = time.time()
    #     freq = np.fft.rfft(data)
    #     n = int(len(data)/2)
    #     frecuencia = (2.0 / self.CHUNK) * np.abs(freq[range(n)])
    #     #Señal temporal
    #     self.data_input_senal.emit(data)
        print(in_data)
        return (in_data, pyaudio.paContinue)

    
    def openStream(self):
        wf = wave.open('output.wav', 'rb')
        
        self.stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        in_data = wf.readframes(self.CHUNK)

        while self.stream.is_active():
            self.stream.write(in_data)
            in_data = wf.readframes(self.CHUNK)
            data = np.frombuffer(in_data, dtype=np.int16)
            self.data_input_senal.emit(data)
            print(data)
            if self.ejecutando == False or len(data) == 0:
                break

            
App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())