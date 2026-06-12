from gpiozero import Buzzer
from time import sleep

buzzer = Buzzer(10)

print("Buzzer Test Started!")
while True:
    buzzer.on()
    print("Buzzer on!")
    sleep(1)
    buzzer.off()
    print("Buzzer off!")
    sleep(1)
    
