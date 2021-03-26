import re
import time
import datetime
# dependencies to install
import serial
import numpy as np

import PIL.Image as im


def sanitize(string):
    pattern = re.compile(r'[A-Z\r\n]', re.M)
    _type = re.findall(pattern, string)
    return _type[0], pattern.sub("", string)


class DataPoint:
    type: None
    buffer: None

    def __init__(self, string):
        _type, sanitized = sanitize(string)
        self.type = _type
        self.buffer = np.asarray(sanitized.split(",")).astype(np.float)


def reshape_into_matrix(array, cols):
    if array.size % cols != 0:
        raise ValueError("array size not be divisible by cols")
    rows, matrix = int(array.size / cols), 0 * np.ones(shape=(0, cols))
    for index in range(rows):
        matrix = np.insert(matrix, index, array[index * cols: (index + 1) * cols], 0)
    return matrix


def read_serial_data(port, baud, callback):
    arduino = serial.Serial(port, timeout=0, baudrate=baud)
    print("Arduino initialized!")
    axel, pressure = None, None

    while True:
        try:
            text = str(arduino.readline(), 'ascii')
            # print(text)
            if len(text) < 1 or text[0] == "_":
                continue
            datapoint = DataPoint(text)

            if datapoint.type == 'A':
                axel = datapoint.buffer
            elif datapoint.type == 'B':
                axel = np.append(axel, datapoint.buffer)
            elif datapoint.type == 'C':
                axel = np.append(axel, datapoint.buffer[0: 60])
                pressure = datapoint.buffer[60: 100]
            else:
                axel = np.append(axel, datapoint.buffer[0: 60])
                pressure = np.append(pressure, datapoint.buffer[60:100])

            if axel is not None and axel.size == 240 and callback is not None:
                callback(axel, pressure, datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S'))
        except Exception:
            print(Exception.__traceback__)


def on_data_compiled(axel, press, timestamp):
    matrix = reshape_into_matrix(axel, 6)
    image = im.fromarray(matrix)
    image.save(r'sample' + timestamp + ".tif")
    print("axel", matrix.size)
    print("press", press)
    print("timestamp", timestamp)


read_serial_data("COM6", 115200, on_data_compiled)
