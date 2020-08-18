# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 11:22:20 2020

@author: rogerselzler
"""
import event_annotator
ea = event_annotator.Event_annotator()

# #load sample data
# ecg_data = event_annotator.load_csv_data('ecg')
# accel_data = event_annotator.load_csv_data('accel')

# # add signals to ea through code
# ea.add_signal(x=ecg_data.x,y=ecg_data.y,yf=ecg_data.yf,name='Ecg')
# ea.add_signal(x=accel_data.x,y=accel_data.y,yf=accel_data.yf,name='Accelerometer')


# # add labels to ea through code
# ea.add_label('RComplex',label_type='points',filename_loc = 'RComplex')
# ea.add_label('Movement',label_type='range',filename_loc = 'Movement')

# run the application
ea.run()


