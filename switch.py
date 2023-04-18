import RPi.GPIO as GPIO
import time
import numpy as np
import pigpio
pi = pigpio.pi()

#周波数による音を出す関数
def tone(freq):
    #PWM_GPIO = 12
    PWM_DUTY = 50 # デューティ比[%]
    PWM_FREQ = freq # 周波数[Hz]

    gpio = BUZZER_PIN
    dutycycle = int(PWM_DUTY * 1000000 / 100.)
    frequency = int(PWM_FREQ)

    pi.hardware_PWM(gpio, frequency, dutycycle)

    return

#キーのピン配置設定
GPIO_LIST = [
    [17,27,261],
    [22,23,293],
    [24,25,329],
    [7,8,349],
    [9,10,391],
]

BUZZER_PIN = 12                                     #ブザーの番号
KEY_STATUS = np.zeros(len(GPIO_LIST),dtype="int8")  #押しているキーの状態を管理
BUZZER_FLAG = 0                                     #ブザーが鳴っていないときに0
LED_OUT_CH = 18

#データの平均化処理用
MEDIAN_ELEMNT_N = 20
dataList = np.ones((len(GPIO_LIST),MEDIAN_ELEMNT_N),dtype="int16")

#GPIOの初期化
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_OUT_CH , GPIO.OUT)
GPIO.output(LED_OUT_CH, GPIO.LOW)
for OUT_CH, IN_CH,_ in GPIO_LIST:    
    GPIO.setup(OUT_CH, GPIO.OUT)    
    GPIO.setup(IN_CH, GPIO.IN)
    GPIO.output(OUT_CH, GPIO.LOW)

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
                
            time.sleep(0.001)

            dataList[i] = np.roll(dataList[i], -1)
            dataList[i][-1] = count

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

    if 1 <= KEY_STATUS.sum() < 2:
        btn = np.argmax(KEY_STATUS)
        if not BUZZER_FLAG:
            tone(GPIO_LIST[btn][2])
            print(GPIO_LIST[btn][2])
            BUZZER_FLAG = 1
        GPIO.output(LED_OUT_CH, GPIO.LOW)
               
    else:
        pi.write(BUZZER_PIN, 0)
        BUZZER_FLAG = 0
        GPIO.output(LED_OUT_CH, GPIO.HIGH)
        print(KEY_STATUS)
        
            
