# Erika Yu (ejy25) and Joshua Diaz (jd794)
# import GPIO and pygame
# LEGEND : 1= BOWING HAND
#                  2= LEFT HAND
import pygame
import RPi.GPIO as GPIO
import time
import smbus
import os

### TFT SETUP
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

# setup pygame
pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((320,240))
pygame.mixer.init()
# setup GPIO and buttons
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# initialize variables for string, note, and playing condition
string_num = 0 #0:G 1:D 2:A 3:E
note_num = 0 # 0:Open 1:first_finger 2:second_finger 3:third_finger 4:forth_

string_playing = 0
note_playing = 0
playing = False

# define colors
BLACK = 0,0,0
WHITE = 255,255,255
GRAY = 120,120,120
BLUE = 0,0,255
CYAN = 0,255,255

# dictionaries for display
note_pos = {'1':70,'2':140,'3':210,'4':280}
string_pos = {'3':40,'2':80,'1':120,'0':160}

# import sound files for all 4 stirngs
note_G3 = pygame.mixer.Sound('../Final_PJ/Notes/G3.wav')
note_A3 = pygame.mixer.Sound('../Final_PJ/Notes/A3.wav')
note_B3 = pygame.mixer.Sound('../Final_PJ/Notes/B3.wav')
note_C4 = pygame.mixer.Sound('../Final_PJ/Notes/C4.wav')

note_D4 = pygame.mixer.Sound('../Final_PJ/Notes/D4.wav')
note_E4 = pygame.mixer.Sound('../Final_PJ/Notes/E4.wav')
note_F4 = pygame.mixer.Sound('../Final_PJ/Notes/F4.wav')
note_G4 = pygame.mixer.Sound('../Final_PJ/Notes/G4.wav')

note_A4 = pygame.mixer.Sound('../Final_PJ/Notes/A4.wav')
note_B4 = pygame.mixer.Sound('../Final_PJ/Notes/B4.wav')
note_C5 = pygame.mixer.Sound('../Final_PJ/Notes/C5.wav')
note_D5 = pygame.mixer.Sound('../Final_PJ/Notes/D5.wav')

note_E5 = pygame.mixer.Sound('../Final_PJ/Notes/E5.wav')
note_F5 = pygame.mixer.Sound('../Final_PJ/Notes/F5.wav')
note_G5 = pygame.mixer.Sound('../Final_PJ/Notes/G5.wav')
note_A5 = pygame.mixer.Sound('../Final_PJ/Notes/A5.wav')
note_B5 = pygame.mixer.Sound('../Final_PJ/Notes/B5.wav')

# Set string arrays as collections of notes
G_string = [note_G3, note_A3, note_B3, note_C4, note_D4 ]
D_string = [note_D4, note_E4, note_F4, note_G4, note_A4 ]
A_string = [note_A4, note_B4, note_C5, note_D5, note_E5 ]
E_string = [note_E5, note_F5, note_G5, note_A5, note_B5 ]

#Set violin array as collection of strings
violin = [G_string, D_string, A_string, E_string]

# Set up accelerometer
CHANNEL = 1

DEV_DEFAULT_ADDR = 0x1D
DEV_SECOND_ADDR = 0X1C

REG_CTRL1 = 0x2A
REG_XYZ_DATA_CFG = 0x0E
REG_STATUS = 0x00

REG_OFF_X= 0x2F
REG_OFF_Y = 0x30
REG_OFF_Z = 0x31

bus = smbus.SMBus(CHANNEL)
MODE_CONFIG = 0x01
DATA_CONFIG = 0x00

# function to prepare accelerometers
def get_ready(DEV_ADDR):
        bus.write_byte_data(DEV_ADDR, REG_CTRL1, MODE_CONFIG)
        bus.write_byte_data(DEV_ADDR, REG_XYZ_DATA_CFG, DATA_CONFIG)

# function to read data from one accelerometer given device address and initial x and z values
def read_accel(DEV_ADDR, init_accel_x, init_accel_z):
        data = bus.read_i2c_block_data(DEV_ADDR, REG_STATUS, 7)
        x_accel =((data[1] *256 + data[2]) >> 4) - init_accel_x
        if(x_accel > 2047):
                x_accel -= 4096
        y_accel = (data[3] *256 + data[4]) >> 4
        if(y_accel > 2047):
                y_accel -= 4096
        z_accel = ((data[5] *256 + data[6]) >> 4) - init_accel_z
        if(z_accel > 2047):
                z_accel -= 4096
        return {'x':x_accel, 'y':y_accel, 'z':z_accel}

# initialize variables for accelerometer data
counter = 0
init_accel_x1 = 0
init_accel_x2 = 0
init_accel_z2 = 0

small_move_x1 = False
big_move_x1 = False
offset_x1 = 0
offset_x2 = 0
offset_z2 = 0
false_bow_count = 0
volume = 1.0

screen.fill(BLACK)
# Polling loop
while(1):
        get_ready(DEV_DEFAULT_ADDR)
        get_ready(DEV_SECOND_ADDR)
        time.sleep(0.2)
        if( not GPIO.input(27)): # quit button
                break
        
        # poll for left finger presses
        if( not GPIO.input(6)):
                note_num = 4
        elif( not GPIO.input(13)):
                note_num = 3
        elif( not GPIO.input(19)):
                note_num = 2
        elif( not GPIO.input(26)):
                note_num = 1
        else:
                note_num = 0

        # small calibration period
        if(counter == 10):
                init_accel = read_accel(DEV_DEFAULT_ADDR,0,0)
                init_accel_x1 = init_accel['x']
                init_accel = read_accel(DEV_SECOND_ADDR,0,0)
                init_accel_x2 = init_accel['x']
                init_accel_z2 = init_accel['z']
                counter += 1
        # read both accelerometers
        elif(counter>10):
                accel = read_accel(DEV_DEFAULT_ADDR,init_accel_x1,0)
                x_acc = abs(accel['x'])
                accel = read_accel(DEV_SECOND_ADDR,init_accel_x2,init_accel_z2)
                x_acc2 = (accel['x'])
                z_acc2 = abs(accel['z'])

                # BOWING HAND ACCELEROMETER CHECKS
                #check for change in x1
                if(abs(x_acc-offset_x1) > 250):
                        small_move_x1 = False
                        big_move_x1 = True
                        volume = 1.0
                elif(abs(x_acc-offset_x1) > 30):
                        small_move_x1 = True
                        big_move_X1 = False
                        volume = 0.6
                else:
                        small_move_x1 = False
                        big_move_x1 = False

                # FINGERING HAND ACCELEROMETER CHECKS
                #check for change in x2 and in z2
                if(x_acc2 > 200): #E-STRING
                        string_num = 3
                elif(x_acc2 > 170): #DEAD ZONE
                        string_num = -1
                elif(x_acc2 > 20): #A-STRING
                        string_num = 2
                elif(x_acc2 > 0): #DEAD ZONE
                        string_num = -1
                elif(x_acc2 > -200): #D-STRING
                        string_num = 1
                elif(x_acc2 > -220): #DEAD ZONE
                        string_num = -1
                else: #G-STRING
                        string_num = 0
                #print(x_acc2)

                offset_x1 = x_acc
        else:
                counter += 1


        play_bool = small_move_x1 or big_move_x1
        if (play_bool and string_num != -1): # play sound
                playing = True
                false_bow_count = 0
                violin[string_num][note_num].set_volume(volume)
                violin[string_num][note_num].play(loops=-1)
                if(string_playing!=string_num or note_playing!=note_num):
                        violin[string_playing][note_playing].stop()
                string_playing = string_num
                note_playing = note_num
                pygame.draw.circle(screen, WHITE, [20,220], 15)

        # no movement, don't play sound
        else:
                pygame.draw.circle(screen, BLACK, [20,220], 15)

                false_bow_count += 1
                if(false_bow_count >= 2):
                        playing = False
                        pygame.mixer.fadeout(100)
    
        # draw and display TFT GUI
        for str_num, str_coord in string_pos.items():
                if(str(string_num) == str_num):
                        pygame.draw.line(screen, BLUE, [0, int(str_coord)], [320,int(str_coord)], 1)
                else:
                        pygame.draw.line(screen, GRAY, [0, int(str_coord)], [320,int(str_coord)], 1)
                for notes_num, note_coord in note_pos.items():
                        if(str(note_num) == notes_num) and (str(string_num) == str_num):
                                pygame.draw.circle(screen, CYAN, [int(note_coord), int(str_coord)], 10)
                        else:
                                pygame.draw.circle(screen, GRAY, [int(note_coord), int(str_coord)], 10)

        pygame.display.flip()