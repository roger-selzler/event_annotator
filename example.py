# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 11:22:20 2020

@author: rogerselzler
"""
import event_annotator
ea = event_annotator.Event_annotator()

#load sample data
ecg_data = event_annotator.load_csv_data('ecg')

# add signals to ea through code
ea.add_signal(x=ecg_data.x,y=ecg_data.y,yf=ecg_data.yf,name='Ecg')

# add labels to ea through code
ea.add_label('RComplex',label_type='points',filename_loc = 'tst')
# ea.add_label('LowPeaks',label_type='points',filename_loc = 'D://RPeaksFilenameTst2') 
ea.add_label('Bad Ecg signal',label_type='range',filename_loc = 'bad ecg segment')

# run the application
ea.run()


