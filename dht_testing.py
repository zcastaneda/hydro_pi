
import board
import time
import adafruit_dht

dht22_1 = adafruit_dht.DHT22(board.D4)
x=0
while True:
    try:
        temperature_c = dht22_1.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dht22_1.humidity
        print(temperature_f, humidity)
        x = x+1
        time.sleep(2)
    except Exception as e:
        print(f'error {e}')
