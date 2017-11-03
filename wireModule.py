import time
import RPi.GPIO as GPIO
import random
import sys
import pygame

pygame.init()
pygame.mixer.init(frequency=22050, size=0, channels=2, buffer=512)
class WireModule:


    disarmed = False
    failed = False
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.OUT) #redled
    GPIO.setup(21, GPIO.OUT) #greenled
    GPIO.setup(26, GPIO.IN)
    GPIO.setup(19, GPIO.IN)
    GPIO.setup(13, GPIO.IN)

    wires = [26,19,13]

    chosenPin=0

    def __init__(self):
        self.disarmed = False
        self.failed = False
        self.wires = [26,19,13]
        self.chosenPin = self.selectWire()
        self.positiveFeedback = pygame.mixer.Sound('NotificationPositive.wav')
        self.positiveDisarmed = pygame.mixer.Sound ('CompletedPositive.wav')
        self.negativeFeedback = pygame.mixer.Sound('Buzz_Negative.wav')
        print("Should cut" + str(self.chosenPin))

    def blinkPattern(self): #defines output for leds while bmob is armed
        if self.chosenPin == 26:
            GPIO.output(20,True)
            GPIO.output(21,True)
            time.sleep(.3)
            GPIO.output(21,False)
            time.sleep(.3)
            GPIO.output(20,True)
            GPIO.output(21,True)
            #red solid green blinking
        if self.chosenPin == 19:
            GPIO.output(21,True)
            GPIO.output(20,True)
            time.sleep(.3)
            GPIO.output(20,False)
            time.sleep(.3)
            GPIO.output(21,True)
            GPIO.output(20,True)
            #green solid red blinking
        if self.chosenPin == 13:
            GPIO.output(20,True)
            GPIO.output(21,True)
            time.sleep(.3)
            GPIO.output(21,False)
            GPIO.output(20,False)
            time.sleep(.3)
            GPIO.output(21,True)
            GPIO.output(20,True)
            #both blinking

    def selectWire(self): #selects the correct wire to cut
        self.selected = random.randint(1,3)
        GPIO.output(21, True) #greenled
        GPIO.output(20, True) #redled
        if self.selected ==1:
            self.chosenPin=26
            return self.chosenPin
        elif self.selected == 2:
            self.chosenPin=19
            return self.chosenPin
        else:
            self.chosenPin=13
            return self.chosenPin

    def checkConnection(self,pinNumber): #checks a given pin number for open or closed
        button_status=GPIO.input(pinNumber)
        print(pinNumber)
        if button_status == True:
            print ("pin is high, circuit open")
            cut = True
            return cut
        else:
            print ("pin is low, circuit closed")
            cut = False
            return cut

    def evalWire(self,wireNum): #checks if the wire is cut if it should be cut
        cut = self.checkConnection(wireNum)
        if cut == True:
            if self.chosenPin == wireNum:
                print ("DISARMED")
                self.disarmed = True
                self.positiveDisarmed.play()
                cutModStatus = "Done"
                GPIO.output(20, False)
                return cutModStatus
            else:
                print ("BOOM!!")
                self.failed = True
                cutModStatus = "Done"
                GPIO.output(21, False)
                return cutModStatus
        elif cut == False:
            print ("BOMBLIVE")
            cutModStatus = "Active"
            return cutModStatus

    def loopingWires(self): # repeats wire checking until it's broken out
        if not self.disarmed:
            cutModStatus = "Active"
            while cutModStatus == "Active":
                self.blinkPattern()
                for wire in self.wires:
                    status = self.evalWire(wire)
                    if status == "Done":
                        cutModStatus = "Done"
                        break      
#time.sleep(10)
#GPIO.cleanup()
#print "Goodbye"
