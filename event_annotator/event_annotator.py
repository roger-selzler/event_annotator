# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 14:32:22 2020
@author: rogerselzler
"""
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
import datetime
import sys
import os
from pprint import pprint as p
from PyQt5 import QtCore, QtGui, QtWidgets
# from scipy import signal as sgn
import warnings
import io

mpl.use('qt5agg')

###########################################################################
##############                 MAIN CLASS               ###################
###########################################################################
class Event_annotator():
    def __init__(self):
        self.config= dict()
        self.__set_default_configurations()
        self._app_created = False
        self.app = None
        self._signals = dict()
        self._tools = []
        self._labels = []
        self._active_signal = None
        self._active_tool = None
        self._active_label = None
        self._data_to_plot = 'original' # 
        self._data_to_plot_options = ['original','filtered','both']
        self._figure_created=False
        self.__create_default_tools()
        self._axvspan = dict()
        self._xlimits = [0, 1]
        
    def __assert_data_required(self):
        if len(self.signals())==0: raise ValueError('Need to add at least one signal')
        if len(self.labels()) == 0: raise ValueError('Need to add at least one label')
        
    def __set_default_configurations(self):
        self.add_configuration(log=False,
                               # available_tools = ['max','min','max_segment','min_segment','middle','range'],
                               # range_tools = ['range'] 
                               )
    
    def __create_default_tools(self):
        def select_middle_point(data):
            active_data = self._active_signal.data
            active_data_selected = active_data[(active_data.x>=np.min(data)) & (active_data.x<=np.max(data))]
            middle_value = (active_data_selected.x.max() - active_data_selected.x.min()) / 2 + active_data_selected.x.min()
            value_to_append = active_data_selected.iloc[(active_data_selected.x-middle_value).abs().argmin()].x
            return value_to_append
        
        self.add_tool(name='Selected Points',function=np.argmin,tool_type = 'multi_point')        
        self.add_tool(name='Max',function=np.max,tool_type = 'single_point')
        self.add_tool(name='Min',function=np.min,tool_type = 'single_point')
        self.add_tool(name='Middle',function = lambda x: select_middle_point(x),tool_type='single_point',target_variable='x')        
        self.add_tool(name='Segment max',function=np.max,tool_type = 'segment_point')
        self.add_tool(name='Segment min',function=np.min,tool_type = 'segment_point')
        self.add_tool(name='Range',function=np.argmin,tool_type = 'range')
        
        
        # ['range','single_point','segment_point','multi_point']
        
    def __create_figure(self):
        if self._figure_created: plt.close(self.fig)
        self.figure_canvas = mpl.backends.backend_qt5agg.FigureCanvas(mpl.figure.Figure())
        # self.figure_canvas.mpl_connect('resize_event',self.__on_figure_resize)
        self.fig = self.figure_canvas.figure
        self.create_lines()
        
        
        
    def __figure_connect(self):
        self.fig.canvas.mpl_connect('resize_event',self.__on_figure_resize)
        self.fig.canvas.mpl_connect('axes_enter_event',self.__on_enter_axes)
        for ax in self.ax:
            ax.rectangle_selector = mpl.widgets.RectangleSelector(   ax,
                                                                  self.__rectangle_on_select,
                                                                  drawtype='box',
                                                                  button=1,
                                                                  rectprops = dict(color='green',alpha=0.2))
            ax.rectangle_deleter = mpl.widgets.RectangleSelector(   ax,
                                                                  self.__rectangle_on_select,
                                                                  drawtype='box',
                                                                  button=3,
                                                                  rectprops = dict(color='red',alpha=0.2))
            ax.callbacks.connect('xlim_changed',self.__on_axis_xlim_change)
        self.fig.canvas.mpl_connect('scroll_event',self.__on_scroll)
        
    def __on_enter_axes(self,event):
        self._active_signal = self.signal(event.inaxes.index)        
        if self.config['log']: print(self._active_signal._name)
        
    def __on_axis_xlim_change(self,event):
        self.update_ylimit()
        self.fig.canvas.draw()
        
    def __on_figure_resize(self,event):
        if self.config['log']: print('function __on_figure_resize')
        self.fig.tight_layout()
        self.fig.canvas.draw()
        if self.config['log']: print('finished __on_figure_resize')
                            
    def __on_scroll(self,event):
        if self.config['log']: print('function __on_scroll')  
        if len(self.ax) > 0:
            limits = self.ax[0].get_xlim()
            newlimits = None
            if event.button == 'down':
                newlimits = ((limits[1]-limits[0]) * 0.8 + limits[0],(limits[1]-limits[0]) * 0.8 + limits[1])
            elif event.button== 'up':
                newlimits = ( limits[0] - (limits[1]-limits[0]) * 0.8 ,limits[1] - (limits[1]-limits[0]) * 0.8)
            # self.xlimit=newlimits
            if newlimits is not None:
                self.update_xlimit(newlimits)
        
        if self.config['log']: print('finished __on_scroll')  
        
    def __rectangle_on_select(self,eclick,erelease):
        if self.config['log']:
            print("function __rectangle_on_select with signal '{}'".format(self._active_signal._name))            
            print('eclick: \n{}\nerelese: \n{}\n'.format(eclick.__dict__,erelease.__dict__))
            print('startposition: (%f, %f)' % (eclick.xdata, eclick.ydata))
            print('endposition  : (%f, %f)' % (erelease.xdata, erelease.ydata))
            print('used button  : ', eclick.button)
        if eclick.button == 1: action = 'add'
        elif eclick.button == 3: action = 'remove'
        
        x_selection = [min([eclick.xdata,erelease.xdata]),max([eclick.xdata,erelease.xdata])]
        y_selection = [min([eclick.ydata,erelease.ydata]),max([eclick.ydata,erelease.ydata])]
        # self._active_signal.data
        # if action == 'remove' and self._active_label._label_type == 'points':
        #     tooli = [tool_i for tool_i,tool in enumerate(self._tools) if tool._name.lower() == 'selected points'][0]
        #     tool = self._tools[tooli]
        # else:
        #     tool=self._active_tool
        tool=self._active_tool
        label = self.active_label
        values_to_append = tool.apply(x_selection[0],x_selection[1],y_selection[0],y_selection[1])
        if label._label_type == 'points':
            for value_to_append in values_to_append:
                if action == 'add':
                    label.add_point(value_to_append)
                elif action == 'remove':
                    label.remove_point(value_to_append)
        elif label._label_type == 'range':
            for value_to_append in values_to_append:
                if action == 'add':
                    label.add_range(value_to_append)
                    self.update_axvspan()
                elif action == 'remove':
                    label.remove_range(value_to_append)
                    self.update_axvspan()
        self.update_scatter()
        self.update_scatter_visibility()
        self.fig.canvas.draw()
        if self.config['log']: print("finished __rectangle_on_select with signal '{}'".format(self._active_signal._name))            
                
                
    def add_configuration(self,**kwargs):
        for key in kwargs.keys():
            self.config[key] = kwargs[key]
            
    def add_signal(self,x,y=None,yf=None,name=''):
        signal = Signal(x,y,yf,name)
        self._signals[len(self._signals)] = signal
        # if self._xlimits[0] < signal.data.x.min():
        #     self._xlimits[0]= signal.data.x.min()
        # if self._xlimits[1] > signal.data.x.max():
        #     self._xlimits[1]= signal.data.x.max()        
        # if len(self._signals) == 1: xlimits = (signal.data.x.min(),signal.data.x.max())
        if self._active_signal is None: self._active_signal = signal
        return signal
    
    def add_tool(self,name,function,tool_type='original',target_variable='y'):
        tool = Tool(self,name=name,function=function,tool_type=tool_type,target_variable=target_variable)
        if len(self._tools) == 0: self._active_tool = tool
        self._tools.append(tool)
        return tool
    
    def add_label(self,name,label_type='points',filename_loc=None):
        label = Label(self,label_name = name,label_type = label_type,filename_loc=filename_loc)
        if len(self._labels)==0: self.active_label = label
        self._labels.append(label)
        return label
    
    def create_lines(self):
        n_lines = len(self.signals()) if len(self.signals())>0 else 1
        ax = self.fig.subplots(n_lines,1,sharex=True)
        self.ax = np.asarray([ax]) if n_lines==1 else ax
        self._scatter={}
        self._axvspan = {}
        
        self._lines = [[] for i in range(len(self.signals()))]
        # markers = ['.','x','+','1','X','P','*','p','8','v','D', 'd' ]        
        
        for signal_i,signal in enumerate(self.signals()):
            if signal_i not in self._scatter.keys(): self._scatter[signal_i] = {}
            self.ax[signal_i].index = signal_i
            self._lines[signal_i].append(self.ax[signal_i].plot(signal.data.x,
                                                                signal.data.y,
                                                                color= 'black',
                                                                alpha=0.7))
            self._lines[signal_i].append(self.ax[signal_i].plot(signal.data.x,
                                                                signal.data.yf,
                                                                color='red',
                                                                alpha=0.7))
            self.ax[signal_i].set_title(signal._name)
        
            
        for signal_i,signal in enumerate(self.signals()):            
            old_label = self._active_label
            for label in self.labels():
                # label.load()
                self._active_label = label
                if label._label_type=='points':
                    self.update_scatter()
                elif label._label_type == 'range':
                    self.update_axvspan()
            self._active_label = old_label
        self.__figure_connect()
        self.fig.tight_layout()
    def get_configuration(self):
        return self.config
    
    @property
    def data_to_plot(self):
        return self._data_to_plot
    
    @data_to_plot.setter
    def data_to_plot(self,data_to_plot):
        _data_to_plot = data_to_plot.lower()
        if _data_to_plot not in self._data_to_plot_options: 
            raise ValueError('{} is not a valid value. Valid values are: {}'.format(_data_to_plot,self._data_to_plot_options))
        self._data_to_plot = _data_to_plot
    
    @property
    def active_label(self):
        return self._active_label
    
    @active_label.setter
    def active_label(self,label):
        self._active_label = label
        if self._app_created: 
            self.app.update_available_tools()
        
    def label(self,index):
        return self._labels[index]
    
    def labels(self):
        return self._labels
    
            
    def signal(self,index):
        return self._signals[index]
    
    def signals(self):
        return [self._signals[i] for i in self._signals.keys()]
    
    def run(self):
        # self.__assert_data_required()
        self.__create_figure()
        self.app = Main_window(self)
        self.app.show()
        self.app.update_available_tools()
        # self.__create_figure()
        self.update_line_visibility()
        self.update_scatter_visibility()
        self.update_ylimit()
        xlimit = [s.data.x.min() for s in self.signals()]
        if xlimit == []:
            xlimit= (0,1)
        else:
            xlimit.extend([s.data.x.max() for s in self.signals()])
        self.update_xlimit([np.min(xlimit), np.max(xlimit)])
        
    def summary(self):
        print('Configuration: ')
        print(self.config)
        if len(self.signals())>0:
            print('\nSignals: ')
            for signal_i,signal in enumerate(self.signals()):
                print('{:>3}: {:<20}'.format(signal_i, signal._name))
        if len(self.labels())>0:
            print('\nLabels:')
            for label in self.labels():
                print('{:>3}: {:<20} type: {:<7} filename and location: {}'.format(label._label_index,label._name,label._label_type,label._filename_loc))
        if len(self._tools)>0:
            print('\nTools:')
            for tool in self._tools:
                print('{:>3}: {:<20} type: {:<15}'.format(tool._tool_index,tool._name,tool._tool_type))
    
    def update_axvspan(self):
        if self.config['log']:print('function update_axvspan')
        if self._active_label._label_type == 'range':
            range_labels = [l for l in self.labels() if l._label_type == 'range']
            if len(range_labels)>0:
                N = len(range_labels)
                Ni = [i+1 for i,label in enumerate(range_labels) if label == self._active_label][0]
                if self._active_label._label_index not in self._axvspan.keys(): self._axvspan[self._active_label._label_index] = []
                for axvspan in self._axvspan[self._active_label._label_index]:
                    axvspan.remove()
                self._axvspan[self._active_label._label_index] = []
                
                for ax in self.ax:
                    for i,row in self._active_label.data.iterrows():
                        self._axvspan[self._active_label._label_index].append(ax.axvspan(row['x_start'],
                                                                                         row['x_end'],
                                                                                         facecolor=mpl.colors.to_hex(mpl.cm.hot(Ni/N*0.8)),
                                                                                         edgecolor='black',
                                                                                         alpha=0.5,
                                                                                         label = self._active_label._name))
                self.fig.canvas.draw()
        if self.config['log']:print('finished update_axvspan')
        
    def update_line_visibility(self):
        if self.config['log']:print('function update_line_visibility')
        for signal_i,signal in enumerate(self.signals()):
            if self.config['log']:print('signal_i: {}, signal: {}'.format(signal_i,signal))
            if self._data_to_plot == 'original' or self._data_to_plot == 'both':
                self._lines[signal_i][0][0].set_visible(True)
            else:
                self._lines[signal_i][0][0].set_visible(False)
            if self._data_to_plot == 'filtered' or self._data_to_plot == 'both':
                self._lines[signal_i][1][0].set_visible(True)
            else:
                self._lines[signal_i][1][0].set_visible(False)
        if self.config['log']:print('finished update_line_visibility')
    
    def update_scatter_visibility(self):
        if self.config['log']:print('function update_line_visibility')
        for signal_i,signal in enumerate(self.signals()):
            for label in self.labels():
                if label._label_type == 'points':
                    if self.config['log']:print('signal_i: {}, signal: {},label: {}'.format(signal_i,signal,label))
                    if self._data_to_plot == 'original' or self._data_to_plot == 'both':
                        self._scatter[signal_i][label._label_index][0].set_visible(True)
                    else:
                        self._scatter[signal_i][label._label_index][0].set_visible(False)
                        
                    if self._data_to_plot == 'filtered' or self._data_to_plot == 'both':
                        self._scatter[signal_i][label._label_index][1].set_visible(True)
                    else:
                        self._scatter[signal_i][label._label_index][1].set_visible(False)
        # self.fig.canvas.draw()
        if self.config['log']:print('finished update_line_visibility')
    
    def update_scatter(self):
        if self.config['log']: print('function update_scatter')
        for signal_i,signal in enumerate(self.signals()):
            # for label in self.labels():
            label = self._active_label
            point_labels = [l for l in self.labels() if l._label_type == 'points']
            N = len(point_labels)
            Ni = [i for i,label in enumerate(point_labels) if label == self._active_label]
            Ni = Ni[0] if len(Ni)>0 else 0
            if label._label_index not in self._scatter[signal_i].keys():
                self._scatter[signal_i][label._label_index ] = []
            if label._label_type == 'points':
                dataf = signal.data[signal.data.x.isin(label.data.x.values)]
                if len(self._scatter[signal_i][label._label_index]) == 0:
                    markers = ['.','x','+','1','X','P','*','p','8','v','D', 'd' ]
                    self._scatter[signal_i][label._label_index].append(self.ax[signal_i].scatter(dataf.x,
                                                                                                  dataf.y,
                                                                                                  color='black',
                                                                                                  marker=markers[np.mod(Ni,len(markers))],
                                                                                                  label=label._name
                                                                                                  ))
                    self._scatter[signal_i][label._label_index].append(self.ax[signal_i].scatter(dataf.x,
                                                                                                  dataf.yf,
                                                                                                  color='black',
                                                                                                  marker=markers[np.mod(Ni,len(markers))],
                                                                                                  label=label._name
                                                                                                  ))
                else:
                    scatter = self._scatter[signal_i][label._label_index]
                    scatter[0].set_offsets(np.vstack((dataf.x.values,dataf.y.values)).T)
                    scatter[1].set_offsets(np.vstack((dataf.x.values,dataf.yf.values)).T)
        # self.fig.canvas.draw()
        if self.config['log']: print('finished update_scatter')
        
    def update_ylimit(self):
        if self.config['log']: print('function update_ylimit')
        if len(self.ax) > 0:
            xlimit = self.ax[0].get_xlim()
            for signal_i, signal in enumerate(self.signals()):
                dataf = signal.data[(signal.data.x >= xlimit[0]) & signal.data.x <= xlimit[1]]
                if len(dataf)>1:
                    if self._data_to_plot == 'original':
                        min_value,max_value=dataf.y.min(),dataf.y.max()
                    elif self._data_to_plot == 'filtered':
                        min_value,max_value=dataf.yf.min(),dataf.yf.max()
                    elif self._data_to_plot == 'both':
                        min_value,max_value=np.min([dataf.y.min(),dataf.yf.min()]),np.max([dataf.y.max(),dataf.yf.max()])
                    self.ax[signal_i].set_ylim(min_value - (max_value - min_value) * 0.2,max_value + (max_value - min_value) * 0.2)
            # self.fig.canvas.draw()
        if self.config['log']: print('finished update_ylimit')
    
    def update_xlimit(self,limit):
        for ax in self.ax:
            ax.set_xlim(limit[0],limit[1])
            # self.ax[0].set_major_formatter
        
###########################################################################
##############                   TOOLS                  ###################
###########################################################################
class Tool(object):
    def __init__(self,
                 event_annotator,
                 name,
                 function,
                 tool_type='single_point',
                 target_variable='y'):
        self.config = dict()
        self.config['tool_types']= ['range','single_point','segment_point','multi_point']
        self.__assert_tool_type(tool_type)
        
        self.__ea = event_annotator
        self._tool_type = tool_type
        self._tool_index = len(self.__ea._tools)
        self._name = name
        self._function = function
        self._target_variable = target_variable
        
    
    def get_filtered_data(self):
        print('TODO')
    
    def __assert_tool_type(self,tool_type):
        if tool_type not in self.config['tool_types']: raise TypeError('tool_type ({}) is not valid. Valid types are: {}'.format(tool_type,self.config['tool_types']))
        else: pass
    
    def __get_segments(self,indexes):
        a_idx = [i for i,a in enumerate(np.diff(indexes)) if a != 1]
        if a_idx == []: return [indexes]
        seg = []
        for i,idx in enumerate(a_idx):
            pseg=[]
            if i==0:
                pseg = indexes[0:idx+1]
            elif i > 0:
                pseg = indexes[a_idx[i-1]+1:idx+1]
            seg.append(pseg)
            if i == len(a_idx)-1:
                pseg = indexes[idx+1:]
                seg.append(pseg)
        return seg
    
    
    def __get_value_to_append(self,data,target_variable= 'y'):
        value = [self._function(data[target_variable].values)]
        if target_variable == 'y':
            value_to_append = data[data[target_variable].isin(value)].x.values
        elif target_variable == 'x':
            data = self.__ea._active_signal.data
            value_to_append = data[data.x.isin(value)].x.values        
        else: value_to_append = []
        return value_to_append
            
    def apply(self,x0,x1,y0,y1):
        '''data: data structure filtered by the rectangle selection'''
        values_to_return = []
        active_data = self.__ea._active_signal.data
        
        if self.__ea._data_to_plot == 'original':
            data_list = [pd.DataFrame(dict(x=active_data.x,y=active_data.y),index=active_data.index)]
        if self.__ea._data_to_plot == 'filtered':
            data_list = [pd.DataFrame(dict(x=active_data.x,y=active_data.yf),index=active_data.index)]
        if self.__ea._data_to_plot == 'both':
            data_list = [pd.DataFrame(dict(x=active_data.x,y=active_data.y), index=active_data.index),
                         pd.DataFrame(dict(x=active_data.x,y=active_data.yf),index=active_data.index)]
        
        for data in data_list:
            if self._tool_type == 'segment_point':
                data = data[(data.x>=x0)&(data.x<=x1)&(data.y>=y0)&(data.y<=y1)]
                segment_indexes = self.__get_segments(data.index.values)
                for segment in segment_indexes:
                    dataf = data[data.index.isin(segment)]
                    if len(dataf)>0:
                        value_to_append = self.__get_value_to_append(dataf,target_variable=self._target_variable)
                        for value_to_appendN in value_to_append:
                            if value_to_appendN not in values_to_return:                        
                                values_to_return.append(value_to_appendN)
                            
            elif self._tool_type == 'single_point':
                data = data[(data.x>=x0)&(data.x<=x1)&(data.y>=y0)&(data.y<=y1)]
                if len(data)>0:
                    value_to_append = self.__get_value_to_append(data,target_variable=self._target_variable)
                    for value_to_appendN in value_to_append:
                            if value_to_appendN not in values_to_return:                        
                                values_to_return.append(value_to_appendN)
                            
            elif self._tool_type == 'multi_point':
                data = data[(data.x>=x0)&(data.x<=x1)&(data.y>=y0)&(data.y<=y1)]
                if len(data)>0:
                    value_to_append = data.x.values
                    for value_to_appendN in value_to_append:
                            if value_to_appendN not in values_to_return:                        
                                values_to_return.append(value_to_appendN)
                            
            elif self._tool_type == 'range':
                data = self.__ea._active_signal.data
                data = data[(data.x>=x0)&(data.x<=x1)]
                if len(data)>0:
                    value_to_append = [data.x.min(), data.x.max()]   
                    if value_to_append[0] != value_to_append[1]:
                        values_to_return.append(value_to_append)
        if self.__ea.config['log']: print('Values to return: {}'.format(str(values_to_return)))
        return values_to_return
                
        
        
        
###########################################################################
##############                  SIGNALS                 ###################
###########################################################################    
class Signal(object):
    def __init__(self,x,y=None,yf=None,name='',signal_type='single_point'):
        def assert_lenght(a,b):
            return True if len(a) == len(b) else False
        
        if y is not None: 
            if not assert_lenght(x,y): 
                raise ValueError('Lengths of signal should be the same')
            else: pass
        else:
            y=x
            x=[i for i in range(len(y))]
        if yf is not None: 
            if not assert_lenght(x,yf): raise ValueError('Lengths of signal should be the same') 
        else: 
            yf = y
        self.data = pd.DataFrame(dict(x=x,y=y,yf=yf))
        self._name = name
        

###########################################################################
##############                  LABELS                 ###################
###########################################################################    
class Label(object):
    def __init__(self,event_annotator,label_name,label_type='points',filename_loc=None):
        self.__ea = event_annotator        
        self._label_type = self.__assert_label_type(label_type)
        self._name = self.__assert_label_name(label_name)
        self._filename_loc = self.__assert_filename_loc(filename_loc)
        self._label_index = len(self.__ea._labels)
        self.data = self.__create_initial_data()
        
    def __assert_label_type(self,label_type):
        valid_values=['points','range']
        if label_type not in valid_values: raise ValueError('Wrong label_type. Valid values are: {}'.format(valid_values))
        else: pass
        return label_type
        
        
    def __assert_label_name(self,label_name):
        for label in self.__ea._labels:
            if label_name == label._name: raise ValueError('{} name already exist'.format(label_name))
            else: pass
        if label_name == '':
            label_name = 'Signal {}'.format(len(self.__ea.labels()))
        return label_name
        
    def __assert_filename_loc(self,filename_loc):
        if filename_loc == '' or filename_loc is None:
            filename_loc = os.path.join(os.getcwd(),self._name)
        if not os.path.isdir(os.path.split(filename_loc)[0]):
            filename_loc = os.path.join(os.getcwd(),filename_loc)
        loc = os.path.split(filename_loc)[0]
        filename = os.path.split(filename_loc)[1]
        if not os.path.isdir(loc): raise ValueError('{} path does not exist.'.format(loc))
        if os.path.isfile(filename_loc): warnings.warn("'{}' file already exist. By saving the file it will overwrite existing data.".format(filename),ImportWarning)
        return filename_loc
                
    def __create_initial_data(self):
        if self._label_type == 'points':
           data = pd.DataFrame(dict(x=[]))
        elif self._label_type == 'range':
            data = pd.DataFrame(dict(x_start=[],x_end=[]))
        return data
    
    def add_point(self,x_value):
        if self._label_type != 'points': raise TypeError('x_value should be a point fro label_type points')
        self.data = self.data.append(dict(x=x_value),ignore_index=True).sort_values('x').reset_index(drop=True)
    
    def add_range(self,x_value):
        if len(x_value) != 2: raise ValueError('x_value should be of length 2, but it was {}'.format(len(x_value)))
        dataf1 = self.data[(self.data.x_start >= x_value[0]) & (self.data.x_start <= x_value[1])]
        dataf2 = self.data[(self.data.x_start <= x_value[0]) & (self.data.x_end >= x_value[0])]
        if (len(dataf1)>0) | (len(dataf2)>0):
            if self.__ea.config['log']: print('invalid range due to intersection range')
        else: 
            self.data = self.data.append(dict(x_start=x_value[0],x_end=x_value[1]),ignore_index=True).sort_values('x_start').reset_index(drop=True)
         
    def label(self,id):
        return self._labels[id]
    
    def labels(self):
        return self._labels
    
    def load(self,from_csv=False):
        if self.__ea.config['log']: print('function load')
        if from_csv:
            filename_loc = os.path.splitext(self._filename_loc)[0] + '.csv'
            if os.path.isfile(filename_loc):
                self.data = pd.read_csv(filename_loc,index_col=0)
        else:
            filename_loc = os.path.splitext(self._filename_loc)[0] + '.pkl'
            if os.path.isfile(filename_loc):
                self.data = pd.read_pickle(filename_loc)
        if self.__ea.config['log']: print('finished load')
        
    def remove_point(self,x_value):
        self.data = self.data[~self.data.x.isin([x_value])]
        
    def remove_range(self,x_value):
        if len(x_value) != 2: raise ValueError('x_value should be of length 2, but it was {}'.format(len(x_value)))
        self.data = self.data[~( (self.data.x_start >= x_value[0]) & (self.data.x_end <= x_value[1]) )]
                
    def save(self,to_csv=False,to_pkl = False):
        if not(to_csv or to_pkl):to_pkl = True
        if self.__ea.config['log']: print('function save')
        if len(self.data)>0:  
            if to_csv:
                filename_loc = os.path.splitext(self._filename_loc)[0] + '.csv'
                self.data.to_csv(filename_loc)
            if to_pkl:
                filename_loc = os.path.splitext(self._filename_loc)[0] + '.pkl'                    
                self.data.to_pickle(filename_loc)
        if self.__ea.config['log']: print('finished save')

###########################################################################
##############                APPLICATION               ###################
###########################################################################
class Main_window(QtWidgets.QWidget,object):
    def __init__(self,event_annotator):
        super().__init__()
        self.__ea = event_annotator
        if self.__ea.config['log']: print('__control_pannel __init__')
        self.initUI()
        self.__ea._app_created = True
        # self.app = QtWidgets.QApplication([])
        # self.window = QtWidgets.QWidget()
        # self.layout = QtWidgets.QVBoxLayout()
    def initUI(self):
        print(self.__dict__)
        self.max_tool_width = 90
        self.setWindowTitle('Event Annotator')
        self.main_area = QtWidgets.QVBoxLayout(self)      
        # self.main_area.setStretch(0,1)
        self.main_box = QtWidgets.QHBoxLayout(self)
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.menu_file = self.menu_bar.addMenu('File')
        # Save
        self.menu_save = self.menu_file.addMenu('Save')
        self.action_save_pkl = QtWidgets.QAction('pickle')
        self.action_save_pkl.triggered.connect(lambda: self.__save(to_pkl=True))
        self.menu_save_pkl_action = self.menu_save.addAction(self.action_save_pkl)
        self.action_save_csv = QtWidgets.QAction('csv')
        self.action_save_csv.triggered.connect(lambda: self.__save(to_csv=True))
        self.menu_save_csv_action = self.menu_save.addAction(self.action_save_csv)
        self.action_save_pkl_csv = QtWidgets.QAction('pickle and csv')
        self.action_save_pkl_csv.triggered.connect(lambda: self.__save(to_csv=True,to_pkl=True))
        self.menu_save_pkl_csv_action = self.menu_save.addAction(self.action_save_pkl_csv)
        # Load
        self.menu_load = self.menu_file.addMenu('Load')
        self.action_load_pkl = QtWidgets.QAction('pickle')
        self.action_load_pkl.triggered.connect(lambda: self.__load(from_csv=False))
        self.menu_load_pkl_action = self.menu_load.addAction(self.action_load_pkl)
        self.action_load_csv = QtWidgets.QAction('csv')
        self.action_load_csv.triggered.connect(lambda: self.__load(from_csv=True))
        self.menu_load_csv_action = self.menu_load.addAction(self.action_load_csv)
        # Add Label        
        self.action_add_label = QtWidgets.QAction('Add label',self)
        self.action_add_label.triggered.connect(self.__add_label)
        self.menu_add_label = self.menu_file.addAction(self.action_add_label)
        self.action_add_signal = QtWidgets.QAction('Add signal',self)
        self.action_add_signal.triggered.connect(self.__add_signal)
        self.menu_add_signal = self.menu_file.addAction(self.action_add_signal)
        
        # self.action_add_label = QtWidgets
        # self.main_area.addWidget(self.main_area_widget)
        # wdg = QtWidgets.QWidget(self)
        # wdg.setStyleSheet('background-color: blue;')
        # wdg.setLayout(self.main_box)
        # self.main_area.addWidget(wdg)
        self.main_area.addLayout(self.main_box)
        self.main_tool_layout = QtWidgets.QVBoxLayout() 
        self.main_right_box = QtWidgets.QVBoxLayout()
        for box in [self.main_box,self.main_tool_layout,self.main_right_box]:
            box.setAlignment(QtCore.Qt.AlignTop)
            
        self.main_box.addLayout(self.main_tool_layout)
        # wdg = QtWidgets.QWidget(self)
        # # wdg.setStyleSheet('background-color: white;')
        # wdg.setLayout(self.main_right_box)
        
        # self.main_tool_layout.setStretch(0,1)
        
        # self.main_box.addWidget(wdg)
        self.main_box.addLayout(self.main_right_box)
        self.main_tool_layout.addWidget(QtWidgets.QLabel('Signal to Plot'))
        self._button_group_data_to_plot = QtWidgets.QButtonGroup()
        self._button_group_data_to_plot.buttonClicked[int].connect(self.__data_to_plot_on_click)
        for signal_to_ploti,signal_to_plot in enumerate(['original', 'filtered', 'both']):
            btn = QtWidgets.QPushButton(signal_to_plot.capitalize())
            btn.setCheckable(True)
            btn.setMaximumWidth(self.max_tool_width)
            if signal_to_plot == self.__ea._data_to_plot: btn.setChecked(True)
            else: btn.setChecked(False)
            self._button_group_data_to_plot.addButton(btn,signal_to_ploti)
            self.main_tool_layout.addWidget(btn)
            
        self.main_tool_layout.addWidget(QtWidgets.QLabel('Tools'))
        self._button_group_tools = QtWidgets.QButtonGroup()
        self._button_group_tools.buttonClicked[int].connect(self.__tool_on_click)
        for tooli,tool in enumerate(self.__ea._tools):
            btn = QtWidgets.QPushButton(tool._name)
            btn.setCheckable(True)
            btn.setMaximumWidth(self.max_tool_width)
            if tool == self.__ea._active_tool: btn.setChecked(True)
            else: btn.setChecked(False)
            self._button_group_tools.addButton(btn,tooli)
            self.main_tool_layout.addWidget(btn)
            
        self.main_tool_layout.addWidget(QtWidgets.QLabel('Labels'))
        self.label_list = QtWidgets.QListWidget(self)
        self.label_list.setMaximumWidth(self.max_tool_width)
        self.label_list.itemClicked.connect(self.__label_on_click)        
        for label in self.__ea.labels():
            self.add_label_list_item(label)
        self.main_tool_layout.addWidget(self.label_list)
        #Figure
        self.figure_toolbar = mpl.backends.backend_qt5agg.NavigationToolbar2QT(self.__ea.figure_canvas,self)
        self.__ea.figure_canvas.figure.tight_layout()
        
        self.main_right_box.addWidget(self.figure_toolbar)
        self.main_right_box.addWidget(self.__ea.figure_canvas)
        
        
        self.main_area.setMenuBar(self.menu_bar)
        
        self.main_right_box.setStretch(0,1)
        self.setLayout(self.main_area)
        # self.main_window.setLayout(main_area)
    
    def __add_label(self):
        self.add_label = Add_label(self,self.__ea)
    def __add_signal(self):
        self.add_signal = Add_signal(self,self.__ea)
        
    def __data_to_plot_on_click(self,id):
        if self.__ea.config['log']:print('function __data_to_plot_on_click')
        self.__ea._data_to_plot = self.__ea._data_to_plot_options[id]
        self.__ea.update_line_visibility()
        self.__ea.update_scatter_visibility()
        self.__ea.update_ylimit()
        self.__ea.fig.canvas.draw()        
        if self.__ea.config['log']:print('finished __data_to_plot_on_click')
        
    def __on_figure_resize(self,event):
        for axi,ax in enumerate(self.ax):
            ax.plot(np.random.random(100)+axi)
        self.figure_canvas.figure.tight_layout()
    def __label_on_click(self,item):
        label_index = [label._label_index for label in self.__ea.labels() if label._name == item.text()]
        if len(label_index) > 0: label_index = label_index[0]
        self.__ea.active_label = self.__ea.label(label_index)
        self.app.update_available_tools()
    
    def __load(self,from_csv=False):
        old_label = self.__ea._active_label
        for label in self.__ea.labels():
            label.load(from_csv=from_csv)
            self.__ea._active_label = label
            self.__ea.update_axvspan()
            self.__ea.update_scatter()            
        self.__ea._active_label = old_label
        
    def __save(self,to_csv=False,to_pkl=False):
        print('save from app')
        for label in self.__ea.labels():
            label.save(to_csv = to_csv,to_pkl=to_pkl)
            
    def __tool_on_click(self,id):
        self.__ea._active_tool = self.__ea._tools[id]
    
        
    def add_label_list_item(self,label):
        item=QtWidgets.QListWidgetItem(label._name,self.label_list)
        if label == self.__ea.active_label: item.setSelected(True)
        else: item.setSelected(False)
            
    def update_available_tools(self):
        if self.__ea._active_label is not None:
            if self.__ea.active_label._label_type == 'points':
                change_tool = False if self.__ea._active_tool._tool_type in ['single_point','segment_point','multi_point'] else True
                label_type = 'points'
            elif self.__ea.active_label._label_type == 'range':
                change_tool = False if self.__ea._active_tool._tool_type in ['range'] else True
                label_type = 'range'
        else: 
            change_tool = False
            label_type = None
        # tool_buttons
        tool_buttons = self._button_group_tools.buttons()
        for tool in self.__ea._tools:
            if label_type is None:
                tool_buttons[tool._tool_index].setDisabled(True)
            elif label_type == 'points':
                if tool._tool_type in ['single_point','segment_point','multi_point']:
                    tool_buttons[tool._tool_index].setDisabled(False)
                    if change_tool:
                        self.__ea._active_tool = tool
                        tool_buttons[tool._tool_index].setChecked(True)
                        change_tool = False
                else:
                    tool_buttons[tool._tool_index].setDisabled(True)
            elif label_type == 'range':
                if tool._tool_type in ['range']:
                    tool_buttons[tool._tool_index].setDisabled(False)
                    if change_tool:
                        self.__ea._active_tool = tool
                        tool_buttons[tool._tool_index].setChecked(True)
                        change_tool = False
                else:
                    tool_buttons[tool._tool_index].setDisabled(True)

class Add_signal(QtWidgets.QWidget,object):
    def __init__(self,main_window,event_annotator):
        super().__init__()
        self.app = main_window
        self.__ea = event_annotator
        self.initUI()
        
    def initUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(QtWidgets.QLabel('Signal name'))
        self.edit_signal_name = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.edit_signal_name)
        self.layout.addWidget(QtWidgets.QLabel('Signal location'))
        hlayout = QtWidgets.QHBoxLayout(self)
        self.edit_fileloc = QtWidgets.QLineEdit(self)
        hlayout.addWidget(self.edit_fileloc)
        self.button_select_folder = QtWidgets.QPushButton('...',self)
        self.button_select_folder.clicked.connect(self.__get_file)
        hlayout.addWidget(self.button_select_folder)
        self.layout.addLayout(hlayout)
        self.button_add_signal = QtWidgets.QPushButton('Add signal')
        self.button_add_signal.clicked.connect(self.__add_signal)
        self.layout.addWidget(self.button_add_signal)
        self.setLayout(self.layout)
        self.show()
        
    def __add_signal(self):
        filename = self.edit_fileloc.text()
        signal_name = self.edit_signal_name.text()
        error_dialog = QtWidgets.QErrorMessage(self)
        if not os.path.exists(filename):
            error_dialog.showMessage('File does not exist')
            return
        if signal_name == "":
            signal_names = [signal._name for signal in self.__ea.signals()]
            for i in range(len(signal_names)+1):
                signal_name = 'Signal {}'.format(i+1)
                print(signal_name)
                if signal_name not in signal_names:
                    break
        print('Signal: {}, filename_loc: {}'.format(signal_name,filename))
        try:
            data = pd.read_csv(filename,index_col=0)
            self.__ea.add_signal(data.x,data.y,data.yf,name=signal_name)
            self.__ea.fig.clf()
            self.__ea.create_lines()
            self.__ea.fig.canvas.draw()
            
        except Exception as e:
            print(e)
        self.close()
        # self.__ea.update
        
            # for signal in self.__ea.signals():
                
    def __get_file(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self,"Signal file",'.pkl')
        print(filename)
        self.edit_fileloc.setText(filename[0])
        
class Add_label(QtWidgets.QWidget,object):
    def __init__(self,main_window,event_annotator):
        super().__init__()
        self.app = main_window
        self.__ea = event_annotator
        self.initUI()
        
    def initUI(self):        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(QtWidgets.QLabel('Label name'))
        self.edit_label_name =QtWidgets.QLineEdit(self) 
        self.layout.addWidget(self.edit_label_name)
        self.layout.addWidget(QtWidgets.QLabel('Label type'))
        self.combo_label_type = QtWidgets.QComboBox(self)
        self.combo_label_type.addItem('points')
        self.combo_label_type.addItem('range')
        self.layout.addWidget(self.combo_label_type)
        self.layout.addWidget(QtWidgets.QLabel('Filename'))
        self.edit_filename = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.edit_filename)
        
        hlayout = QtWidgets.QHBoxLayout(self)
        self.edit_fileloc = QtWidgets.QLineEdit(self)
        hlayout.addWidget(self.edit_fileloc)
        self.button_select_folder = QtWidgets.QPushButton(self)
        self.button_select_folder.clicked.connect(self.__get_directory)
        hlayout.addWidget(self.button_select_folder)
        self.layout.addLayout(hlayout)
        
        self.button_add_label = QtWidgets.QPushButton('Add label')
        self.button_add_label.clicked.connect(self.__add_label)
        self.layout.addWidget(self.button_add_label)
        self.setLayout(self.layout)
        self.show()
        
    def __add_label(self):
        print('__add_label')
        label_name = self.edit_label_name.text()
        label_type = self.combo_label_type.currentText()
        fileloc = self.edit_fileloc.text()
        filename = self.edit_filename.text()
        buffer=io.StringIO()
        error_dialog = QtWidgets.QErrorMessage(self)
        if label_name == '': 
            error_dialog.showMessage('Label name is required')
            return
        if filename == '':
            filename_loc = ''
        else:
            if fileloc == '':
                fileloc=os.getcwd()
            else:
                if not os.path.isdir(fileloc):
                    error_dialog.showMessage('Location invalid')
                    return
            filename_loc = os.path.join(fileloc,filename)
        label = self.__ea.add_label(label_name,label_type,filename_loc)
        self.app.add_label_list_item(label)
        buffer.write("Label created\nName: {}\nType: {}\nFile: '{}'".format(label._name,label._label_type,label._filename_loc))
        dialog = QtWidgets.QMessageBox(self)
        dialog.setText(buffer.getvalue().strip())
        dialog.show()
        if label_type == 'range':
            self.__ea.update_axvspan()
        self.close()
        print(label)
    
    def __get_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory()
        self.edit_fileloc.setText(directory)
        
        
        
        
# def utils():
    # def __init__(self):
    #     self.ecgdata = self.load_csv_data('ecg_data.csv')
    
def load_csv_data(data):
    valid_data = ['ecg','accel']    
    if data not in valid_data:
        print('Invalid data. Options are: {}'.format(valid_data))
        return 
    filenames = dict(ecg='ecg_data.csv',
                     accel='accel_data.csv')
    filename = filenames[data]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename_loc = os.path.join(dir_path,filename)
    if os.path.isfile(filename_loc):
        return pd.read_csv(filename_loc,index_col=0)
    else: return None
        

if __name__ == '__main__':
    plt.close('all')
    print()
    QtWidgets.QApplication.closeAllWindows()
    N=2000
    np.random.seed(N)
    ea  = Event_annotator()
    # ea.config['log']=True 
    ea.add_signal([i+30 for i in range(N)],np.random.random(N),np.random.random(N),name='Sample Signal 1')
    # val = np.random.random(N)
    # ea.add_signal([i*1.2 for i in range(N)],val,val+3,name='Sample Signal 2')
    # ea.add_signal([i+50 for i in range(N)],val,val+3,name='Sample Signal 3')
    
    # start = pd.Timestamp('2015-07-01')
    # end = pd.Timestamp('2015-08-01')
    # x_val = np.linspace(start.value,end.value,N)
    # ea.add_signal(x_val,np.random.random(N),np.random.random(N),name='Sample Signal 1')
    # val = np.random.random(N)
    # ea.add_signal(x_val,val,val+3,name='Sample Signal 2')
    # ea.add_signal(x_val,val,val+3,name='Sample Signal 3')
    
    ea.add_label('High Peaks',label_type='points')
    # ea.add_label('High Peaks',label_type='points',filename_loc = 'D://HighPeaksFilenameTst.pkl')
    # ea.add_label('Low Peaks',label_type='points',filename_loc = 'D://LowPeaksFilenameTst')
    # ea.add_label('High Peaks1',label_type='points',filename_loc = 'D://HighPeaksFilenameTst.pkl')
    # ea.add_label('Low Peaks1',label_type='points',filename_loc = 'D://LowPeaksFilenameTst')
    # ea.add_label('High Peaks2',label_type='points',filename_loc = 'D://HighPeaksFilenameTst.pkl')
    # ea.add_label('Low Peaks2',label_type='points',filename_loc = 'D://LowPeaksFilenameTst')
    # ea.add_label('High Peaks3',label_type='points',filename_loc = 'D://HighPeaksFilenameTst.pkl')
    # ea.add_label('Low Peaks3',label_type='points',filename_loc = 'D://LowPeaksFilenameTst')
    # ea.add_label('High Peaks4',label_type='points',filename_loc = 'D://HighPeaksFilenameTst.pkl')
    # ea.add_label('Low Peaks4',label_type='points',filename_loc = 'D://LowPeaksFilenameTst')
    # ea.add_label('Activities',label_type='range',filename_loc = 'D://ActivitiesFilenameTst')
    # ea.add_label('Activities2',label_type='range',filename_loc = 'D://Activities2FilenameTst')
    
    

    ea.run()
    
    
        