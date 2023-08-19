#COMMANDS API (DEPRECATED)
    # "c" - Calibrate
    # "v" Values Array - usage: (0, 1, 2, 3) 0=ldr%, 1=dht(C), 2=ds18b20(C), 3=moisture% (rangestart), (rangeend), (0, 1) 0=led, 1= notification, rgb led values/notification text - again" - example: "v0;50;80;0;255,255,255-1;30;40;1;bildirim metni buuu"
    # "r" - Required Light Required Moisture - example: "r60r45"
    #
 

#                                                  IMPORTS
import _thread
import dht
from machine import Pin, ADC, I2C
import onewire
import ds18x20
import ssd1306
from time import sleep
import json
import math
import ble_minecopy
from machine import WDT

#                                                   CLaSSeS-------------------------------------------------------------
class LDR:
    def __init__(self, pin, min_value=0, max_value=100):
        if min_value >= max_value:
            raise Exception('Min value is greater or equal to max value')
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)
        self.min_value = min_value
        self.max_value = max_value
    def read(self):
        return self.adc.read()
    def value(self):
        return self.read()#(self.max_value - self.min_value) * self.read() / 4095

#                                     VaRiAbLeS ------------------------------------------------------------------
tempds = -1.0
temp = -1.0
soilmoist = -1.0
ldrVal = -1.0
ledState = ""
servoState = ""
actionsParsed = [] #[(0,50,80,0,(255,255,255))]
extremeTemp = (-30, 70)
sendToRasitAbi = False

#                                   INItIaLIzATIoNS ----------------------------------------------------------------
ldr = LDR(34)             #LDR
relay = Pin(4, Pin.OUT)   #RELAY
ledRed=Pin(5,Pin.OUT)     #LEDS
ledGreen=Pin(17,Pin.OUT)
ledBlue=Pin(16,Pin.OUT)

wdt = WDT(timeout = 15000)  # Wait 10 seconds to reset the system.
wdt.feed()

try:
    i2c = I2C(-1, scl=Pin(22), sda=Pin(21)) #OLED
    oled_width = 128
    oled_height = 64
    oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
except Exception as e:
    print("Oled is not connected: {}".format(e))
ds_pin=Pin(33)  #DS18B20
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()
capmoist = ADC(Pin(32)) #SOIL MOISTURE SENSOR
capmoist.atten(ADC.ATTN_11DB)
sensor = dht.DHT22(Pin(18)) #DHT SENSOR

#------------------------------------------------Calibration Start--------------------------------------------
try: #Check if file exists
    f = open("values.txt", "r")
    f.close()
except OSError:
    try:
        oled.fill(0) #-----------LDR Max Value
        oled.text("Calibration is starting...", 0, 0)
        oled.show()
        sleep(1)
        oled.fill(0)
        oled.text("Put your LDR", 0, 0)
        oled.text("under max light", 0, 10)
        oled.text("3", 31, 20)
        print("Put your LDR under MAX light.")
        oled.show()
        sleep(1)
        oled.fill(0)
        oled.text("Put your LDR", 0, 0)
        oled.text("under max light", 0, 10)
        oled.text("2", 31, 20)
        oled.show()
        sleep(1)
        oled.fill(0)
        oled.text("Put your LDR", 0, 0)
        oled.text("under max light", 0, 10)
        oled.text("1", 31, 20)
        oled.show()
        sleep(1)
        oled.fill(0)
        oled.text("LDR Max value is:", 0, 0)
        maxLDR = ldr.value()
        oled.text(str(maxLDR), 0, 10)
        oled.show()
        sleep(3)
        oled.fill(0) #----------LDR Min value
        oled.text("Put your LDR", 0, 0)
        oled.text("in the dark", 0, 10)
        oled.text("3", 31, 20)
        print("Put your LDR under MIN light.")
        oled.show()
        sleep(1)
        oled.fill(0)
        oled.text("Put your LDR", 0, 0)
        oled.text("in the dark", 0, 10)
        oled.text("2", 31, 20)
        oled.show()
        sleep(1)
        oled.fill(0)
        oled.text("Put your LDR", 0, 0)
        oled.text("in the dark", 0, 10)
        oled.text("1", 31, 20)
        oled.show()
        sleep(1)
        oled.fill(0)
        oled.text("LDR Min value is:", 0, 0)
        minLDR = ldr.value()
        oled.text(str(minLDR), 0, 10)
        oled.show()
        sleep(3)
        oled.fill(0) #-----------Moisture Max Value
        oled.text("Calibration is starting...", 0, 0)
        oled.show()
        sleep(1)
        oled.fill(0)
        oled.text("Put your Moisture sensor", 0, 0)
        oled.text("in the water", 0, 10)
        oled.text("3", 31, 20)
        oled.show()
        sleep(1)
        oled.fill(0)
        oled.text("Put your Moisture sensor", 0, 0)
        oled.text("in the water", 0, 10)
        oled.text("2", 31, 20)
        oled.show()
        sleep(1)
        oled.fill(0)
        oled.text("Put your Moisture sensor", 0, 0)
        oled.text("in the water", 0, 10)
        oled.text("1", 31, 20)
        oled.show()
        sleep(1)
        oled.fill(0)
        oled.text("Moisture Max value is:", 0, 0)
        maxMoist = capmoist.read()
        oled.text(str(maxMoist), 0, 10)
        oled.show()
        sleep(3)
        oled.fill(0) #----------Moisture Min value
        oled.text("Dry your Moisture sensor", 0, 0)
        oled.text("3", 31, 10)
        oled.show()
        sleep(1)
        oled.fill(0)
        oled.text("Dry your Moisture sensor", 0, 0)
        oled.text("2", 31, 10)
        oled.show()
        sleep(1)
        oled.fill(0)
        oled.text("Dry your Moisture sensor", 0, 0)
        oled.text("1", 31, 10)
        oled.show()
        sleep(1)
        oled.fill(0)
        oled.text("Moisture Min value is:", 0, 0)
        minMoist = capmoist.read()
        oled.text(str(minMoist), 0, 10)
        oled.show()
        sleep(3)
        oled.fill(0) #---------Calibration Save
        oled.text("Calibration is being saved...", 0, 0)
        oled.show()
        
        calibrationData = {
        'maxLDR':maxLDR,
        'minLDR':minLDR,
        'maxMoist':maxMoist,
        'minMoist':minMoist,
        'reqLight':80,
        'reqMoist':70,
        'values':"0;80;300;1;Light rate is above 80%."}
        
        with open("values.txt", "w") as saveFile:
            json.dump(calibrationData, saveFile)
    except Exception as e:
        print("OLED NOT CONNECTED-CALIBRATION FAILED: {}".format(e))
        print("USING DEFAULT VALUES")
        with open("values.txt", "w") as saveFile:
            saveFile.write('{"reqLight": 80, "minLDR": 706, "minMoist": 254, "maxLDR": 3568, "maxMoist": 592, "values": "0;0;30;0;255,0,0-0;30;60;0;0,255,0-0;60;120;0;0,0,255", "reqMoist": 70}')

        
        
#-------------------------------------------------Calibration Done---------------------------------------------
with open('values.txt') as f:
    data = f.read()
req_values = json.loads(data)

#                                                    FuNCtIOnS ------------------------------------------------
def translate(value, leftMin, leftMax, rightMin, rightMax):
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    try:
        valueScaled = float(value - leftMin) / float(leftSpan)#Covert value to 0-1
        return rightMin + (valueScaled * rightSpan)#Convert 0-1 to final value
    except Exception as e:
        return value
        saveException("(193) Exc: {}".format(e))
    
def changeServo(state):
    global servoState
    if state == "On":
        servoState = "On"
        relay.value(0)
    elif state == "Off":
        servoState = "Off"
        relay.value(1)
        
def saveException(exc):
    with open("log.txt", "a") as saveFile:
        saveFile.write(exc + "\n")
        print(exc)
    
def changeRGBLed(rgbLedRed, rgbLedGreen, rgbLedBlue):
    try:
#             print(translate(int(rgbLedColor[0]), 0, 255, 0, 1))
#             print(translate(int(rgbLedColor[1]), 0, 255, 0, 1))
#             print(translate(int(rgbLedColor[2]), 0, 255, 0, 1))
#             print(" ")
        ledRed.value(translate(int(rgbLedRed), 0, 255, 1, 0))
        ledGreen.value(translate(int(rgbLedGreen), 0, 255, 1, 0))
        ledBlue.value(translate(int(rgbLedBlue), 0, 255, 1, 0))
#             ledRed.value(float(0.1))
#             ledGreen.value(1)
#             ledBlue.value(float(0.1))
    except Exception as e:
        saveException("(229) Exc: {}".format(e))

    
def parseActions():
    try:
        global actionsParsed
        actionsParsed = [] #[(0,50,80,0,(255,255,255))]
        
        valuesRaww = req_values.get("values")
        if (len(valuesRaww) > 0):
            actionsPartSeperated = valuesRaww.split("-")
        
            for itemUnparsed in actionsPartSeperated:
                item = itemUnparsed.split(";")
                actionsParsed.append(tuple([item[0], item[1], item[2], item[3], item[4]]))
            
            print(actionsParsed)
    except Exception as e:
        saveException("(265) Exc: {}".format(e))
        
        
def sensorThread():
    global ldrVal
    global tempds
    global soilmoist
    global ledState
    global servoState
    global temp
    global actionsParsed
    while True:
        try:                                        #MEASUREMENTS
            soilmoist = translate(capmoist.read(), req_values.get("minMoist"), req_values.get("maxMoist"), 0, 100)
        except Exception as e:
            saveException("(277) Exc: {}".format(e))
            
        try:
            ldrVal = ldr.value()
        except Exception as e:
            saveException("(282) Exc: {}".format(e))
            
        try:
            ds_sensor.convert_temp()
            sleep(0.75)
            for rom in roms:
                #print(rom)
                temptemp = ds_sensor.read_temp(rom)
                if (temptemp < extremeTemp[1] and temptemp > extremeTemp[0]):
                    tempds = temptemp
        except Exception as e:
            saveException("(293) Exc: {}".format(e))
        
        try:
            sensor.measure()
            temppp = sensor.temperature()
            if (temppp < extremeTemp[1] and temppp > extremeTemp[0]):
                temp = temppp
        except Exception as e:
            #saveException("(299) Exc: {}".format(e))
            print("299")
        
        

def BLEThingsThread():
    global sendToRasitAbi
    wdtble = WDT(timeout = 15000)  # Wait 10 seconds to reset the system.
    while True:
        wdtble.feed()

        try:
            command = ble_minecopy.get_command()
        except Exception as e:
            saveException("(323) Exc: {}".format(e))
        
        if not (command == False):
            #global actionsParsed
            newActions = {}
            
            if (len(command) > 0):
                try:
                    newActions = json.loads(command)  #Expected JSON = {"command":"c"} {"command":"r", "reqLight":80, "reqMoist":70} {"command":"v", "type":"light/moist", "min":50, "max":60, "action":"notification/led", "param":"255,255,0/notification text"} {"command":"get", "type":"LDR/Moist/Temp/SoilTemp"}
                    commandType = newActions.get("command")
                except Exception as e:
                    saveException("(333) Exc: {}".format(e))
        
                if (commandType == "c"):
                    try:
                        import os
                        os.remove("values.txt")
                    except Exception as e:
                        saveException("(341) Exc: {}".format(e))
                    import sys
                    sys.exit()
                    while True:
                        sleep(10)
                    import machine
                    machine.reset()
                elif (commandType == "r"):
                    try:
                        #print(new_req_values)
                        req_values["reqLight"] = newActions.get("reqLight")
                        req_values["reqMoist"] = newActions.get("reqMoist")
                        with open("values.txt", "w") as saveFile:
                            json.dump(req_values, saveFile)
                    except Exception as e:
                        saveException("(451) Exc: {}".format(e))
                elif (commandType == "v"):
                    try:
    #{"command":"v", "type":"light/moist", "min":50, "max":60, "action":"led/notification", "param":"255,255,0/notification text"}
    #(Deprecated) "v" Values Array - usage: (0, 1, 2, 3) 0=ldr%, 1=dht(C), 2=ds18b20(C), 3=moisture% (rangestart), (rangeend), (0, 1) 0=led, 1= notification, rgb led values/notification text - again" - example: "v0;50;80;0;255,255,255-1;30;40;1;bildirim metni buuu"
                        if (req_values["values"] == ""):
                            stringToWrite = ""
                        else:
                            stringToWrite = "-"
                            
                        dataType = newActions.get("type")
                        if (dataType == "light"):
                            stringToWrite += "0"
                        elif (dataType == "dht"):
                            stringToWrite += "1"
                        elif (dataType == "ds"):
                            stringToWrite += "2"
                        elif (dataType == "moist"):
                            stringToWrite += "3"
                        else:
                            ble_minecopy.send_command("false") #If type not found
                            continue
                            
                        stringToWrite += ";" + newActions.get("min")
                        stringToWrite += ";" + newActions.get("max")
                        
                        actionType = newActions.get("action")
                        if (actionType == "led"):
                            stringToWrite += ";0"
                        elif (actionType == "notify"):
                            stringToWrite += ";1"
                        else:
                            ble_minecopy.send_command("false") #If type not found
                            continue
                        
                        stringToWrite += ";" + newActions.get("param")
                        
                        req_values["values"] = req_values["values"] + stringToWrite
                        with open("values.txt", "w") as saveFile:
                            json.dump(req_values, saveFile)
                        parseActions()
                    except Exception as e:
                        saveException("(398) Exc: {}".format(e))
                elif (commandType == "clear"):
                    try:
                        req_values["values"] = ""
                        with open("values.txt", "w") as saveFile:
                            json.dump(req_values, saveFile)
                        parseActions()
                    except Exception as e:
                        saveException("(406) Exc: {}".format(e))
                elif (commandType == "get"):
                    try: #{"command":"get", "type":"LDR/Moist/Temp/SoilTemp"}
                        typeToSend = newActions.get("type")
                        
                        if (typeToSend == "LDR"):
                            ble_minecopy.send_command("LDR: {0}".format(ldrVal))
                        elif (typeToSend == "Temp"):
                            ble_minecopy.send_command("TempDHT: {0}".format(temp))
                        elif (typeToSend == "Moist"):
                            ble_minecopy.send_command("Soil Moist: {0}".format(soilmoist))
                        elif (typeToSend == "SoilTemp"):
                            ble_minecopy.send_command("TempDS: {0}".format(tempds))
                        else:
                            ble_minecopy.send_command("No Type")
                    except Exception as e:
                        saveException("(422) Exc: {}".format(e))
                elif (commandType == "getAll"):
                    sendToRasitAbi = True

parseActions()

def BLESender():
    global sendToRasitAbi
    while True:
        try:
            if (sendToRasitAbi == True):
                ble_minecopy.send_command("LDR: {0}".format(ldrVal))
                ble_minecopy.send_command("TempDHT: {0}".format(temp))
                ble_minecopy.send_command("TempDS: {0}".format(tempds))
                ble_minecopy.send_command("ServoState: {0}".format(servoState))
                ble_minecopy.send_command("Soil Moist: {0}".format(soilmoist))
                sendToRasitAbi = False
        except Exception as e:
            saveException("(432) Exc: {}".format(e))
        sleep(0.1)
    
try:
    _thread.start_new_thread(sensorThread, ())
except Exception as e:
    saveException("(438) Exc: {}".format(e))
    
try:
    _thread.start_new_thread(BLEThingsThread, ())
except Exception as e:
    saveException("(443) Exc: {}".format(e))

try:
    _thread.start_new_thread(BLESender, ())
except Exception as e:
    saveException("(448) Exc: {}".format(e))
    
while True:
    try:                                         # REQUIRED ACTIONS
        try:
            if soilmoist < req_values["reqMoist"] or ldrVal < req_values['reqLight']:
                for i in range(15): #SAD
                    oled.pixel(24 + i, 12, 1) #Left Eye
                    oled.pixel(74 + i, 12, 1) #Right Eye
                    oled.pixel(39 + i, 50 - math.floor(i / 2), 1) #Mouth go up
                    oled.pixel(54 + i, 43 + math.floor(i / 2), 1) #Mouth go down
                oled.show()
            else:
                for i in range(15): #HAPPY
                    oled.pixel(24 + i, 15 - math.floor(i / 2), 1) #Eyes go up
                    oled.pixel(74 + i, 15 - math.floor(i / 2), 1)
                    oled.pixel(39 + i, 8 + math.floor(i / 2), 1) #Eyes go down
                    oled.pixel(89 + i, 8 + math.floor(i / 2), 1)
                    oled.pixel(39 + i, 40 + math.floor(i / 2), 1) #Mouth go down
                    oled.pixel(54 + i, 47 - math.floor(i / 2), 1) #Mouth go up
                oled.show()
        
        except Exception as e:
            print("(456) Exc: {}".format(e))
            
        try:
            if soilmoist < req_values["reqMoist"]:
                changeServo("On")
            else:
                changeServo("Off")
                
        except Exception as e:
            saveException("(465) Exc: {}".format(e))
            
        try:                                        # USER DEFINED FUNCTIONS
            for item in actionsParsed:
                try:
                    if (item[0] == "0"):   #LDR
                        if (translate(ldrVal, req_values.get("minLDR"), req_values.get("maxLDR"), 0, 100) < int(item[2]) and translate(ldrVal, req_values.get("minLDR"), req_values.get("maxLDR"), 0, 100) > int(item[1])):
                            if (item[3] == "0"):   #LED
                                ledParsed = item[4].split(",")
                                changeRGBLed(ledParsed[0], ledParsed[1], ledParsed[2])
                            elif (item[3] == "1"):   #NOTIFICATION
                                #ble_minecopy.send_command("n{}".format(item[4]))
                                saveException("n{}".format(item[4]))
                    elif (item[0] == "1"):   #DHT22
                        if (temp < int(item[2]) and temp > int(item[1])):
                            if (item[3] == "0"):   #LED
                                ledParsed = item[4].split(",")
                                changeRGBLed(ledParsed[0], ledParsed[1], ledParsed[2])
                            elif (item[3] == "1"):   #NOTIFICATION
                                #ble_minecopy.send_command("n{}".format(item[4]))
                                saveException("n{}".format(item[4]))
                    elif (item[0] == "2"):   #DS18B20
                        if (tempds < int(item[2]) and tempds > int(item[1])):
                            if (item[3] == "0"):   #LED
                                ledParsed = item[4].split(",")
                                changeRGBLed(ledParsed[0], ledParsed[1], ledParsed[2])
                            elif (item[3] == "1"):   #NOTIFICATION
                                #ble_minecopy.send_command("n{}".format(item[4]))
                                saveException("n{}".format(item[4]))
                    elif (item[0] == "3"):   #soilmoist
                        if (soilmoist < int(item[2]) and soilmoist > int(item[1])):
                            if (item[3] == "0"):   #LED
                                ledParsed = item[4].split(",")
                                changeRGBLed(ledParsed[0], ledParsed[1], ledParsed[2])
                            elif (item[3] == "1"):   #NOTIFICATION
                                #ble_minecopy.send_command("n{}".format(item[4]))
                                saveException("n{}".format(item[4]))
                except Exception as e:
                    saveException("(496) Exc: {}".format(e))
            
        except Exception as e:
            saveException("(499) Exc: {}".format(e))
    except Exception as e:
        saveException("(507) Exc: {}".format(e))
    wdt.feed()                    
    sleep(0.5)