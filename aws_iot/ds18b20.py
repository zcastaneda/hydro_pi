import subprocess
import re


class pyds18b20:
    def __init__(self) -> None:
        self.__get_devices()
        pass

    def init_one_wire(self,GPIO_PIN):
        #setup one wire

        bash_cmd = f'sudo dtoverlay w1-gpio gpiopin={GPIO_PIN} pullup=0'
        print(bash_cmd)
        process = subprocess.Popen(bash_cmd.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        print(output,error)

    def __get_devices(self):
        #refresh the list of devices available
        bash_cmd = f'ls /sys/bus/w1/devices/'
        process = subprocess.Popen(bash_cmd.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        device_list = output.decode('utf-8').split('\n')
        r = re.compile('^28-.{12}')
        self.device_list = list(filter(r.match, device_list))
        print(device_list)

    
    def get_temp(self, sensor_name):
        bash_cmd = f'cat /sys/bus/w1/devices/{sensor_name}/temperature'
        process = subprocess.Popen(bash_cmd.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        t_celsius = re.sub('\n','',output.decode('utf-8'))
        t_celsius = round(float(t_celsius[0:len(t_celsius)-3]+'.'+t_celsius[-3:len(t_celsius)]),3)
        t_farenheit = round((9/5)*t_celsius+32,3)
        print(t_farenheit)
        return t_farenheit
        


if __name__ == "__main__":
    t_sensor = pyds18b20()
    t_sensor.init_one_wire(GPIO_PIN='17')
    t_sensor.get_temp(sensor_name = t_sensor.device_list[0])