from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
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

pg.setConfigOptions(antialias=True)

class Window(QMainWindow): 
    CHUNK = 4096 #chunk
    RATE = 44100
    T = 1/RATE
    seguir = True
    frames = []
    WIDTH = 2
    CHANNELS = 2
    
    data_input_senal = pyqtSignal(np.ndarray)
    data_input_frecuencia = pyqtSignal(np.ndarray)

    def __init__(self): 
        super().__init__() 
        self.p = pyaudio.PyAudio()
        self.setWindowTitle("Audio Master ") 
        self.setGeometry(100, 100, 800, 600)
        self.ejecutando = True
        self.setLayoutApp()
        self.initPlot()
        self.fps = 0
        self.timeAnt =  0
        self.timeTcpAnt = 0
        self.data_input_senal.connect(self.setDataPlotSenal)
        self.data_input_frecuencia.connect(self.setDataPlotFrecuencia)
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
        self.plt2 = pg.PlotWidget()
        filas.addWidget(self.plt1)
        filas.addWidget(self.plt2)

        gcentral.setLayout(filas)
        fcentral.addWidget(gcentral)
        centralWidget.setLayout(fcentral)
        self.setCentralWidget(centralWidget)
        
        
    def initPlot(self):
        self.plt1.setYRange(-20000, 20000)
        self.plt1.getPlotItem().setTitle(title="Representación temporal")
        self.plt1.getAxis('bottom').setLabel('Tiempo')
        self.plt1.getAxis('left').setLabel('Nivel')
        self.plt2.setYRange(0, 2000)
        self.plt2.getPlotItem().setTitle(title="Representación frecuencial (FFT)")
        self.plt2.getAxis('bottom').setLabel('Frecuencia', units='Hz')
        self.plt2.getAxis('bottom').enableAutoSIPrefix(enable=True)
        self.plt2.getAxis('left').setLabel('Nivel')

    @pyqtSlot(np.ndarray)
    def setDataPlotSenal(self,data):
        self.plt1.plot(data,pen=(255,0,0),clear=True)

    @pyqtSlot(np.ndarray)
    def setDataPlotFrecuencia(self,data):
        self.plt2.plot(data,pen=(255,0,0),clear=True)

    def closeEvent(self, event):
        res = QMessageBox.question(self,"Salir ...","Seguro que quieres cerrar",QMessageBox.Yes|QMessageBox.No)
        if res==QMessageBox.Yes:
            self.ejecutando = False
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            QApplication.quit()

    def callback(self, in_data, frame_count, time_info, status):
        data = np.fromstring(in_data, dtype=np.int16)
        timeFact = time.time()
        freq = np.fft.rfft(data)
        n = int(len(data)/2)
        frecuencia = (2.0 / self.CHUNK) * np.abs(freq[range(n)])
        #Señal temporal
        self.data_input_senal.emit(data)
        #Frecuencia
        self.data_input_frecuencia.emit(frecuencia)

        return (in_data, pyaudio.paContinue)

    
    def openStream(self):
        self.stream = self.p.open(format=self.p.get_format_from_width(self.WIDTH),
                            channels=self.CHANNELS,
                            rate=self.RATE,
                            input=True,
                            output=True,
                            frames_per_buffer=self.CHUNK,
                            stream_callback=self.callback)
        
        self.stream.start_stream()
        while self.stream.is_active():
            time.sleep(0.1)

            if self.ejecutando == False:
                break
        


App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())