import RPi.GPIO as GPIO
import time
import numpy as np
from gpiozero import TonalBuzzer
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero.tones import Tone

#GPIO.cleanup()

#キーのピン配置設定
GPIO_LIST = [
    [17,27,261],
    [22,23,293],
]

KEY_STATUS = np.zeros(len(GPIO_LIST),dtype="int8")

LED_OUT_CH = 18
BUZZER_FLAG = 0

#データの平均化処理用
MEDIAN_ELEMNT_N = 10
dataList = np.ones((len(GPIO_LIST),MEDIAN_ELEMNT_N),dtype="int16")

#GPIOの初期化
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_OUT_CH , GPIO.OUT)
GPIO.output(LED_OUT_CH, GPIO.LOW)

for OUT_CH, IN_CH,_ in GPIO_LIST:    
    GPIO.setup(OUT_CH, GPIO.OUT)    
    GPIO.setup(IN_CH, GPIO.IN)
    GPIO.output(OUT_CH, GPIO.LOW)

#ブザー初期化
BUZZER_PIN = 14
factory = PiGPIOFactory()
buzzer = TonalBuzzer(BUZZER_PIN, pin_factory=factory)

while True:
    for i,(OUT_CH, IN_CH, freq) in enumerate(GPIO_LIST):
        try:
            count = 0  
            GPIO.output(OUT_CH, GPIO.HIGH)  

            while True:            
                channelIsOn = GPIO.input(IN_CH)
                count+=1
                if channelIsOn==1:
                    break
                
            time.sleep(0.005)

            dataList[i] = np.roll(dataList[i], -1)
            dataList[i][-1] = count

            #print(dataList)

            if np.median(dataList[i]) > 3:
                KEY_STATUS[i] = 1
            else:
                KEY_STATUS[i] = 0

            GPIO.output(OUT_CH, GPIO.LOW)
            time.sleep(0.001)

        except KeyboardInterrupt:
            print("stop")
            GPIO.cleanup()
            break
    
    if (KEY_STATUS.sum()) and (not KEY_STATUS.prod()):
            btn = np.argmax(KEY_STATUS)
            if not BUZZER_FLAG:
                buzzer.play(Tone(GPIO_LIST[btn][2]))
                BUZZER_FLAG = 1
            GPIO.output(LED_OUT_CH, GPIO.LOW)
            
    else:
        buzzer.stop()
        BUZZER_FLAG = 0
        GPIO.output(LED_OUT_CH, GPIO.HIGH)
        #print(KEY_STATUS)
        
            
