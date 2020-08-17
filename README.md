# event_annotator

event_annotator is a tool for annotating events in time series data written in python. The user can add signals and labels both programmaticaly or using a graphical interface. 
There are available tools to select either points or ranges. By selecting points on the plotted graphs, the user can add values or ranges to the labels, and save them to a file to use later on. The user can use tools from the toolbar to navigate through the signals. Scrooling inside an axis will forward the signals by 80% or backward the signals by 80% by using the up or down mouse scrool respectively.

The tool is great to select points of interest from a given signal. For example, points label can be used to extract the 'R' complex of a 'QRS' segment of ECG signals. The user can add both original signal and filtered version, to facilitate the selection on the graph. By using the tool *Max segment*, multiple R segments can be selected simultaneously.

Another great example would be to know which parts of the signals cannot be used due to bad quality. A label could be created with the name *bad segments* of type range. By selecting the bad segments (start-end), the user can later on delete them from the data analysis.
```
import EventAnnotator
ea = EventAnnotator.Event_annotator()
```

## Install
```
pip3 install --upgrade pip
pip3 install --upgrade PyQt5 setuptools wheel

git clone https://github.com/roger-selzler/event_annotator
cd event_annotator
pip3 install .
```

## signals
Signals contain the time series data to be plotted. 

```
# add the signals
ea.add_signal(x,     y,   yf, name='Signal 1')
ea.add_signal(x*1.2, y+2, yf, name='Modified signal')
```

## labels
The labels can be either points or range.

```
# create the labels
ea.add_label(name='peaks',         label_type='points', filename_loc='C://peaks.pkl')
ea.add_label(name='good_segments', label_type='range' , filename_loc='C://good_segments.pkl')
```

### points
The points labels will store the 'x' values of the points selected from the signals. Note: The values are not indexes, but they can be if the user set the 'x' values to be integers that reference indices. The advantage is that float values can be used, which can help, for example, with time values expressed in floats. 

### range
range values will store the 'x_start' and 'x_end' values of a selected range. This is very useful in tasks where the user wants to have 

## tools
The tools states how the values will be selected from the signals. Left click will add points with the selected tool while Right click will remove points with the selected tool.

### existing tools
#### Multi-point
##### Selected points
All points selected will be added to the label.

##### Max segment:

<div><img src="https://github.com/roger-selzler/event_annotator/blob/master/images/ea_max_segment.png" width="25%"></div>
The code detects the jumps in indexes and breaks the selected signal in segments. For each of these segments, the 'x' value of the maximum value of the segment will be stored on the label.

##### Min segment: 
<div><img src="https://github.com/roger-selzler/event_annotator/blob/master/images/ea_min_segment.png" width="25%"></div>
Same as Max segment, but selecting the minimum values.

#### Single point
##### Max:
<div><img src="https://github.com/roger-selzler/event_annotator/blob/master/images/ea_max.png" width="25%"></div>
Selects the maximum point of the selected values from the axis and stores it to the label.

##### Min:
<div><img src="https://github.com/roger-selzler/event_annotator/blob/master/images/ea_min.png" width="25%"></div>
Selects the minimum value of the selected points from the axis and stores it to the label.


# Example
```python
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

```

