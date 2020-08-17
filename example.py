# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 11:22:20 2020

@author: rogerselzler
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy import signal as sgn
from PyQt5 import QtCore, QtGui, QtWidgets


plt.close('all')
N=2000
QtWidgets.QApplication.closeAllWindows()
np.random.seed(N)
values=np.random.random(N)
values = values + np.asarray([np.mod(i,30)/10 for i in range(N)])

signal1_x = np.asarray([i for i in range(N)])
signal1_y = values+2
signal1_yf = sgn.filtfilt(np.ones(4)/4,1,signal1_y)

signal2_x = np.asarray([i+50 for i in range(N)])
signal2_y = values
signal2_yf = sgn.filtfilt(np.ones(4)/4,1,signal2_y)




import event_annotator
ea = event_annotator.Event_annotator()
ea.config['log']=True
ea.add_label('HighPeaks',label_type='points',filename_loc = 'D://RPeaksFilenameTst')
ea.add_label('LowPeaks',label_type='points',filename_loc = 'D://RPeaksFilenameTst2') 
ea.add_label('Kevin',label_type='points',filename_loc = 'D://RPeaksFilenameTst2') 
ea.add_label('GoodSegment',label_type='range',filename_loc = 'D://goodSegments')

ea.add_signal(signal1_x,signal1_y,signal1_yf,name='Ecg')
ea.add_signal(signal2_x,signal2_y,signal2_yf,name='Breathing')

ea.run()


