#!/bin/bash

import select
import sys
import random
import pygame
import time

import RPi.GPIO as GPIO
import payphoneModule
import rfidModule
import wireModule

pygame.init()
pygame.mixer.init(frequency=22050, size=0, channels=2, buffer=512)

explosionSound = pygame.mixer.Sound('ShrapnelExplosion.wav')
tickingSound = pygame.mixer.Sound('13Min.wav')
youWonSound = pygame.mixer.Sound('PeacefulPositive.wav')



def main():

    youWonSound.play()

 #Austin's student ID string is 14808538. This will be used to start one version of the game

    newGameToken = input("Put the right token on me to start a new game")
    
    rfid = rfidModule.RFIDModule(newGameToken)
    payphone = payphoneModule.PayphoneModule(newGameToken)
    wire = wireModule.WireModule()

    
    runRFID = True
    runPayphone = True
    runwireModule = True

    tickingSound.play()
    while (len(newGameToken) >= 8):
         
        # Each module is given a chance to update itself at each iteration of the game loop. The
        # modules manage their own internal state and will communicate out only by setting their
        # 'disarmed' or 'failed' flags, which the game loop can then check after they update.

        if runRFID == True:
            rfid.update()
            if rfid.disarmed:
                print("RFID module disarmed!")
                runRFID = False

        if runPayphone == True and runRFID == False:
            payphone.update()
            if payphone.disarmed:
                print("Payphone module disarmed!")
                runPayphone = False

        if runwireModule == True and runPayphone == False and runRFID == False:
            wire.loopingWires()
            if wire.disarmed:
                print("Wire module disarmed!")
                runwireModule = False
        
        # If *all* of the modules are disarmed, then the game ends
        if wire.disarmed:
            time.sleep(3)
            youWonSound.play()
            print ("You won!")
            time.sleep(10)
            GPIO.cleanup()
            break

        # If *any* of the modules fail, then the game ends as well
        if wire.failed or rfid.failed or payphone.failed:
            explosionSound.play()
            print("Bang!")
            time.sleep(10)
            GPIO.cleanup()
            break

    # End of the main game loop


# ==================================================================================================================
# This is the standard behavior modifying python module clause: if the file was run directly run the "main()"
# function, otherwise if it was imported in another module don't do anything.
if __name__ == '__main__':
    main()
