import RPi.GPIO as GPIO
import time
import numpy as np

#キーのピン配置設定
GPIO_LIST = {
    "key1": [17,27],
    "key2": [22,23],
    }

LED_OUT_CH = 18

#データの平均化処理用
MEDIAN_ELEMNT_N = 5
dataList = np.ones((len(GPIO_LIST),MEDIAN_ELEMNT_N),dtype="int8")

#GPIOの初期化
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_OUT_CH , GPIO.OUT)
GPIO.output(LED_OUT_CH, GPIO.LOW)

for OUT_CH, IN_CH in GPIO_LIST.values():    
    GPIO.setup(OUT_CH, GPIO.OUT)    
    GPIO.setup(IN_CH, GPIO.IN)
    GPIO.output(OUT_CH, GPIO.LOW)
    

while True:
    for i,(OUT_CH, IN_CH) in enumerate(GPIO_LIST.values()):
        try:
            count = 0  
            GPIO.output(OUT_CH, GPIO.HIGH)  

            while True:            
                channelIsOn = GPIO.input(IN_CH)
                count+=1
                if channelIsOn==1:
                    break
                
            time.sleep(0.005)

            #print(count)

            dataList[i] = np.roll(dataList[i], -1)
            dataList[i][-1] = count

            if i==1:
                print(f"{i}::{np.median(dataList[i])}")

            if np.median(dataList[i]) > 3:
                GPIO.output(LED_OUT_CH, GPIO.HIGH)
            else:
                GPIO.output(LED_OUT_CH, GPIO.LOW)

            GPIO.output(OUT_CH, GPIO.LOW)
            time.sleep(0.005)

        except KeyboardInterrupt:
            print("stop")
            GPIO.cleanup()
            break