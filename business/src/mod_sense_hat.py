import time
from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED

# Array dei canali 
channels = [1, 2]

G = [0, 127, 0]  # Green
R = [127, 0, 0]  # Red

# Segno verde: visualizzato al termine del programma
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

exit_flag = (0)
calib_temp = None
sense = None

class SenseManager(object):
    def __init__(self, channel):
        global sense
        self.channel = channel
        sense = SenseHat()
        self.show_green_sign()
        pass

    def read_channel(self):

        val = None
        
        # Verifico se ho premuto il pulsante di stop
        sense.stick.direction_middle = self.pushed_middle

        # Lettura dai sensori del SenseHat acquisizione Temperatura, Pressione, Humidity
        if (self.channel == 1):
            val = sense.get_temperature()
        else:
            val = sense.get_pressure()

        # Arrotondamento ad una cifra decimale
        val = round(val, 2)

        return val

    
# ------------------------------------------------------------------------------------------------
#  METODI DEDICATI PER IL SENSE-HAT
# ------------------------------------------------------------------------------------------------

    # Alla pressione del pulsante del sense-hat il programma termina
    def pushed_middle(self, event):
        global exit_flag
        if event.action == ACTION_PRESSED:
            print("Button pressed")
            exit_flag = 1

    # Alla pressione del pulsante del sense-hat il programma termina
    def show_green_sign(self):
        sense.set_pixels(green_sign)

    # Metdodo per la colorazione del display del sensehat
    def show_temperature(self, temp_value):

        global calib_temp

        # Calcolo il livello di colore (tra 1 e 255) proporzionale alla temperatura rilevata
        pixel_light = int( (((temp_value - calib_temp.pmin) / (calib_temp.pmax - calib_temp.pmin)) * 255) // 1)
        if (pixel_light > 255):
            pixel_light = 255
        if (pixel_light < 0):
            pixel_light = 0

        # Creo il codice colore di riferimento:
        # Blu = freddo; Rosso = caldo
        X = [pixel_light, 0, 255 - pixel_light]

        # Matrice "tinta unita"
        one_level = [
        X, X, X, X, X, X, X, X,
        X, X, X, X, X, X, X, X,
        X, X, X, X, X, X, X, X,
        X, X, X, X, X, X, X, X,
        X, X, X, X, X, X, X, X,
        X, X, X, X, X, X, X, X,
        X, X, X, X, X, X, X, X,
        X, X, X, X, X, X, X, X
        ]
        
        # Coloro il display in tinta unita
        sense.set_pixels(one_level)

    def calibrate(self, sensor, pcycles=5, pmin=0, pmax=100):

        avg_temp = 0
        calib = 1

        # Avvio fase di calibrazione iniziale: la temperatura media risulta
        # da una media di 5 rilevazioni della temperatura ambiente
        print("Calibrating Sensor: <" + sensor + ">")

        while (calib <= pcycles):
            avg_temp = avg_temp + sense.get_temperature()
            print ("Calibration [" + str(calib) + "]: <" + str(avg_temp / calib) + ">")
            calib = calib + 1
            time.sleep(1)

        avg_temp = avg_temp / pcycles
        print ("Avg: <" + str(avg_temp)+ ">")

        # Fisso i valori di riferimento del range di temperatura
        # (+/- 1C rispetto alla temperatura di calibrazione)
        pmax = avg_temp + 1
        pmin = avg_temp - 1
        print ("Min: <" + str(pmin)+ ">; Max: <" +str(pmax)+ ">")