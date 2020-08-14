# event_annotator

event_annotator is a tool for annotating events in time series data written in python. The user can add signals and labels both programmaticaly or using a graphical interface. 
There are available tools to select either points or ranges. By selecting points on the plotted graphs, the user can add values or ranges to the labels, and save them to a file to use later on. The user can use tools from the toolbar to navigate through the signals. Scrooling inside an axis will forward the signals by 80% or backward the signals by 80% by using the up or down mouse scrool respectively.

The tool is great to select points of interest from a given signal. For example, points label can be used to extract the 'R' complex of a 'QRS' segment of ECG signals. The user can add both original signal and filtered version, to facilitate the selection on the graph. By using the tool *Max segment*, multiple R segments can be selected simultaneously.

Another great example would be to know which parts of the signals cannot be used due to bad quality. A label could be created with the name *bad segments* of type range. By selecting the bad segments (start-end), the user can later on delete them from the data analysis.
```
import EventAnnotator
ea = EventAnnotator.Event_annotator()
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
The code detects the jumps in indexes and breaks the selected signal in segments. For each of these segments, the 'x' value of the maximum value of the segment will be stored on the label.

##### Min segment: 
Same as Max segment, but selecting the minimum values.

#### Single point
##### Max:
Selects the maximum point of the selected values from the axis and stores it to the label.

##### Min:
Selects the minimum value of the selected points from the axis and stores it to the label.


# Example
```python
# libraries for creating the signals
import numpy as np
from scipy import signal

# EventAnnotator library
import EventAnnotator

# create signal
N=2000
x = np.arange(0,N,1)
y = np.random.random(N)
yf = signal.filtfilt(np.ones(10)/10,1,y)

#create the event anotator object
ea = EventAnnotator.Event_annotator()

# add the signals
ea.add_signal(x,     y,   yf, name='Signal 1')
ea.add_signal(x*1.2, y+2, yf, name='Modified signal')

# create the labels
ea.add_label(name='peaks',         label_type='points', filename_loc='C://peaks.pkl')
ea.add_label(name='good_segments', label_type='range' , filename_loc='C://good_segments.pkl')

# execute the application
ea.run()


```

