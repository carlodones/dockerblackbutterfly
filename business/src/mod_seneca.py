#!/usr/bin/env python3
import time
import tMODBUS
#from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED

# Array dei canali 
channels = [1, 2]

exit_flag = (0)
calib_temp = None
modbus = None

class ModbusManager(object):
    def __init__(self, channel):
        global modbus
        self.channel = channel
        #modbus = tMODUBUS()
        pass

    def read_channel(self):

        val = None
        
        # Verifico se ho premuto il pulsante di stop
        # modbus.stick.direction_middle = self.pushed_middle
        #val = modbus.temperature()
        val = tMODBUS.modbus(self,1)
        print (val)
        # Lettura dai sensori del SenseHat acquisizione Temperatura, Pressione, Humidity
        
        #if (self.channel == 1):
        #    val = modbus.temperature()
        #else:
        #    val = modbus.pressure()

        # Arrotondamento ad una cifra decimale
        val = round(val, 2)

        return val

    
# ------------------------------------------------------------------------------------------------
#  METODI DEDICATI PER IL SENSE-HAT
# ------------------------------------------------------------------------------------------------

    # Alla pressione di "q" il programma termina
    def pushed_middle(self):
        global exit_flag      
        while True:
            value = input("\nenter press q to exit: ")          
            if value == "q":
    	        print("exit")
    	        exit_flag = 1
                #break
                           

    def calibrate(self, sensor, pcycles=5, pmin=0, pmax=100):

        avg_temp = 0
        calib = 1

        # Avvio fase di calibrazione iniziale: la temperatura media risulta
        # da una media di 5 rilevazioni della temperatura ambiente
        print("Calibrating Sensor: <" + sensor + ">")

        while (calib <= pcycles):
            avg_temp = avg_temp + tMODBUS.modbus(self,1)
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

if __name__ == '__main__':
    
#    ModbusManager.pushed_middle(0)
#    tMODBUS.modbus(6)
#    self=ModbusManager(modbus)
#    self.channel=3
#    ModbusManager.read_channel(self)
    ModbusManager.calibrate(5, -50, 100)
    ModbusManager.calibrate()

