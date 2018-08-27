# coding=utf-8
import time
import mod_log
import mod_measure_list
from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED

# Array dei canali 
channels = [1, 2]

G = [0, 127, 0]  # Green
R = [127, 0, 0]  # Red
X = [0, 0, 0]  # Off

# Segno verde: visualizzato all'avvio e al termine del programma
green_sign = [
G, G, G, G, G, G, G, G,
G, G, G, R, R, G, G, G,
G, G, R, G, G, R, G, G,
G, R, G, G, G, G, R, G,
G, R, G, G, G, G, R, G,
G, G, R, G, G, R, G, G,
G, G, G, R, R, G, G, G,
G, G, G, G, G, G, G, G
]

# Segno verde: visualizzato all'avvio e al termine del programma
display_off = [
X, X, X, X, X, X, X, X,
X, X, X, X, X, X, X, X,
X, X, X, X, X, X, X, X,
X, X, X, X, X, X, X, X,
X, X, X, X, X, X, X, X,
X, X, X, X, X, X, X, X,
X, X, X, X, X, X, X, X,
X, X, X, X, X, X, X, X
]

exit_flag = False
calib_temp = None

x = 0
y = 0

class SenseManager(object):
    def __init__(self, log_mgr, channel, send):

        self.log_mgr = log_mgr
        self.channel = channel
        self.sense = SenseHat()
        self.turn_off_display()
        self.name = "sense_hat"
        self.qos = mod_measure_list.QOS()
        self.send = send

        self.log_mgr.info(self.__class__.__name__, "SenseManager initialized", 2)

    # Acquire single measure from single channel
    def read_channel(self):

        val = None
        qos = None

        # Get timestamp
        ts = time.time()
        
        try: # Acquiring from SenseHat sensors: Temperature, Pressure, Humidity

            if(self.channel == 1):
                val = float(self.sense.get_temperature())
            elif(self.channel == 2):
                val = float(self.sense.get_pressure())
            else:
                val = float(self.sense.get_humidity())
            
            qos = self.qos.ONLINE
            self.light_up_pixel()

        except:
            qos = self.qos.ANOMALY
            self.log_mgr.fatal("Error processing channel:<" + str(self.channel) + ">", 3)

        meas_sh = mod_measure_list.Measure(self.channel, val, ts, qos, self.send)

        return meas_sh

    def get_name(self):
        return self.name

    def close(self):
        self.log_mgr.info(self.__class__.__name__, "SenseManager closed", 2)
        try:
            self.turn_off_display()
            self.sense.clear()
            self.sense = None
        except:
            self.log_mgr.fatal("Error closing sense_hat", 1)
        self.channel = None

# ------------------------------------------------------------------------------------------------
#  METODI DEDICATI PER IL SENSE-HAT
# ------------------------------------------------------------------------------------------------

    # Alla pressione del pulsante del sense-hat il programma termina
    def show_green_sign(self):
        self.sense.set_pixels(green_sign)

    # Alla pressione del pulsante del sense-hat il programma termina
    def turn_off_display(self):
        self.sense.set_pixels(display_off)

    def light_up_pixel (self):

        meas_color = []
        pix = []

        if(self.channel == 1):
            meas_color = [127, 0, 0]
        elif(self.channel == 2):
            meas_color = [0, 127, 0]
        else:
            meas_color = [0, 0, 127]

        pix = self.next_pixel()
        self.sense.set_pixel(pix[0], pix[1], meas_color)

    def next_pixel(self):

        global X
        x = 0
        y = 0

        pix = []

        while (self.sense.get_pixel(x, y) != X):

            x = x + 1

            if (x == 8):
                x = 0
                y = y + 1

            if (y == 8):
                self.turn_off_display()
                x = 0
                y = 0

        pix.append(x)
        pix.append(y)

        return pix
