# ==================================================================================================================
# The PayphoneModule tracks the state of the code-entering payphone hardware.  It manages its own internal state, storing
# the sequence of buttons that has been pressed.  When the user presses down on the hook, it checks the code that's been
# entered against the disarm code (currently hardcoded to '1258'.  If it's correct, the module is disarmed.  If it's not,
# the entered sequence is reset and the module records that a failed attempt has happened.  After three unsuccessful
# attempts the module is failed.
#
# I fleshed this module out so that it more or less should be functional so you can see how the pieces might
# work.  Everything the module needs is contained to the instance of the class, so there's no global variables polluting
# the outer scope.  You can put this module in another file, for example, and mess around with it without causing
# any issues to the rest of the program or the other modules...it is totally self contained.

import payphone
import pygame

pygame.init()
pygame.mixer.init(frequency=22050, size=0, channels=2, buffer=512)

DEBUG = True

def dprint(obj):
    if DEBUG:
        print("DEBUG Payphone: {}".format(obj))

class PayphoneModule:
    def __init__(self, newGameToken):
        self.disarmed = False
        self.failed = False

        self.button0_sound = pygame.mixer.Sound('DTMF-0.wav')
        self.button1_sound = pygame.mixer.Sound('DTMF-1.wav')
        self.button2_sound = pygame.mixer.Sound('DTMF-2.wav')
        self.button3_sound = pygame.mixer.Sound('DTMF-3.wav')
        self.button4_sound = pygame.mixer.Sound('DTMF-4.wav')
        self.button5_sound = pygame.mixer.Sound('DTMF-5.wav')
        self.button6_sound = pygame.mixer.Sound('DTMF-6.wav')
        self.button7_sound = pygame.mixer.Sound('DTMF-7.wav')
        self.button8_sound = pygame.mixer.Sound('DTMF-8.wav')
        self.button9_sound = pygame.mixer.Sound('DTMF-9.wav')
        self.buttonStar_sound = pygame.mixer.Sound('DTMF-star.wav')
        self.buttonPound_sound = pygame.mixer.Sound('DTMF-pound.wav')

        self.positiveFeedback = pygame.mixer.Sound('NotificationPositive.wav')
        self.positiveDisarmed = pygame.mixer.Sound ('CompletedPositive.wav')
        self.negativeFeedback = pygame.mixer.Sound('Buzz_Negative.wav')

        
        if newGameToken == "14808538":
            self.defuse_sequence = ["1258", "4577", "50*2", "8824"]
        else:
            self.defuse_sequence = ["2158", "57*8"]
            
        self.reader = payphone.PayphoneReader(self.hook_pressed, self.button_pressed)
        self.entered_sequence = ""
        self.total_attempts = 0
        self.code_number = 0
        dprint("module initialized")
        dprint("defuse_sequence: {}".format(self.defuse_sequence))

    def button_pressed(self, button_code):
        # When we trap a button being pressed, we add its code to the self.entered_sequence field so that
        # we can keep track of what's been entered
        self.entered_sequence += button_code
        dprint("Currently entered sequence = {}".format(self.entered_sequence))

        if button_code == '0':
            self.button0_sound.play()
        elif button_code == '1':
            self.button1_sound.play()
        elif button_code == '2':
            self.button2_sound.play()
        elif button_code == '3':
            self.button3_sound.play()
        elif button_code == '4':
            self.button4_sound.play()
        elif button_code == '5':
            self.button5_sound.play()
        elif button_code == '6':
            self.button6_sound.play()
        elif button_code == '7':
            self.button7_sound.play()
        elif button_code == '8':
            self.button8_sound.play()
        elif button_code == '9':
            self.button9_sound.play()
        elif button_code == '*':
            self.buttonStar_sound.play()
        elif button_code == '#':
            self.buttonPound_sound.play()


    def hook_pressed(self, hook_state):
        if hook_state == True and self.entered_sequence:
            dprint("hook pressed")
            # We'll only process this on the down stroke of the hook, otherwise this code would run
            # twice every time the hook is pressed

            if self.entered_sequence == self.defuse_sequence[self.code_number]:
                # If they entered the correct code, we set the module to know that it's been
                # disarmed.
                self.code_number += 1
                self.positiveFeedback.play()
                dprint("Code {} entered successfully, {} more remaining".format(self.code_number, len(self.defuse_sequence)-self.code_number))
                self.entered_sequence = ""
                if self.code_number == len(self.defuse_sequence):
                    self.disarmed = True
                    self.positiveDisarmed.play()
                    dprint("module disarmed")
            else:
                # They entered the wrong code, so we reset the entered sequence and increment
                # the count of times they've tried
                
                self.total_attempts += 1
                self.negativeFeedback.play()
                dprint("failed sequence '{}', {} total attepts".format(self.entered_sequence, self.total_attempts))
                self.entered_sequence = ""

                # If they've messed up three times we set the module so it knows it's been failed
                if self.total_attempts == 3:
                    self.failed = True
                    dprint("module triggered")

    def update(self):
        # If it's already been disarmed we won't bother doing anything, otherwise we allow the PayphoneReader
        # to check its state and trigger one of the callbacks if they are relevant
        if not self.disarmed:
            self.reader.read()
