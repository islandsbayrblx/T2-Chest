import numpy as np
import win32gui, win32ui, win32con
from threading import Thread, Lock
from time import sleep, time
import pyautogui
import pydirectinput

import win32api

dc = win32gui.GetDC(0)
red = win32api.RGB(255, 0, 0)

class BotState:
    INITIALIZING = 0
    SEARCHING = 1
    MOVING = 2
    MINING = 3
    BACKTRACKING = 4

class Bot:

    # constants
    INITIALIZING_SECONDS = 6
    MINING_SECONDS = 14
    MOVEMENT_STOPPED_THRESHOLD = 0.975
    IGNORE_RADIUS = 130
    TOOLTIP_MATCH_THRESHOLD = 0.72

    #Pixel locations
    chatPixels = [  (70,14),
                    (76,14),
                    (70,26),
                    (76,26)]
    
    chestGrid = [   (481, 242),
                    (662, 242),
                    (481, 413),
                    (662, 413),
                    (571, 413),
                    (571, 242),
                    ]
    
    chestSlot = [   (572, 263),
                    (538, 263),
                    (527, 279),
                    (538, 279),
                    
                    (531, 260),
                    (527, 296),
                    (538, 296),
                    (532, 279)]
    
    #Previous chest locations
    rC = 0
    lC = 0

    # threading properties
    stopped = True
    lock = None

    # properties
    gatherItemTime = 0.6
    state = None
    targets = []
    screenshot = None
    timestamp = None
    movement_screenshot = None
    window_offset = (0,0)
    window_w = 0
    window_h = 0
    limestone_tooltip = None
    click_history = []

    hwndX       = 0
    hwndY       = 0

    #These wont be used
    #hwndWidth   = 1
    #hwndHeight  = 1

    # constructor
    def __init__(self, window_name=None):
        # create a thread lock object
        self.lock = Lock()

        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception('Window not found: {}'.format(window_name))
        
    # threading methods

    def update_targets(self, targets):
        self.lock.acquire()
        self.targets = targets
        self.lock.release()

    def update_screenshot(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def updateHWND(self,hwnd):
        rect = win32gui.GetWindowRect(hwnd)
        x, y, right, bottom = rect
        # width = right - x
        # height = bottom - y

        self.hwndX      = rect[0] + 8
        self.hwndY      = rect[1] + 30 + 1
        

        #These wont be used
        # self.hwndHeight = height - 30 - 8
        # self.hwndWidth  = width - 16


    def checkPixels(self,x, y,pixels,tC):
        for p in pixels:
            try:
                r,g,b =  pyautogui.pixel(x + p[0],y + p[1])

                #win32gui.SetPixel(dc,self.hwndX + p[0],self.hwndY + p[1], red)
                #print(r,g,b)

                if r != tC[0] or g != tC[1] or b != tC[2]:
                    return False
            except:
                return False

        return True

    #Check if the chest gui is visible

    def chestCheck(self):
        while True:
            sleep(0.01)
            exit = False

            if self.targets != None:
                for square in self.targets:
                    if (square[1] >= 256 and square[1] <= 300):
                        exit = True
            
            if exit:
                break

    def scrollChest(self,square):
        #get window relative position
        sx, sy, w, h = square

        midSquareX = round(sx + (w/2))

        pydirectinput.PAUSE = 0.003

        while True:
            pydirectinput.moveTo(self.hwndX + midSquareX,self.hwndY + sy - h)

            for i in range(1,24,2):
                pydirectinput.moveRel(1,i)
                pydirectinput.keyDown("f")
                pydirectinput.keyUp("f")

            #Put mouse in orgin so it does not cover chest GUI
            pydirectinput.moveTo(self.hwndX,self.hwndY)
            pydirectinput.moveRel(1,1)
            
            
            #Exit loop once chest GUI detected
            if self.checkPixels(self.hwndX,self.hwndY,self.chestGrid,(255, 242, 211)):
                pydirectinput.PAUSE = 0.1
                break
        pass
        
    #0 == right
    #1 == left
    def ChestDirection(self,x,y,direction):
        for square in self.targets:

            if direction == 0:
                if square[0] >= x and square[1] >= y:
                    self.scrollChest(square)
                    pass
            elif direction == 1:
                if square[0] <= x and square[1] >= y:
                    self.scrollChest(square)
                    pass

    def gatherItems(self):
        while True:
            if self.checkPixels(self.hwndX,self.hwndY,self.chestSlot,(255, 242, 211)) == False:

                if self.checkPixels(self.hwndX,self.hwndY,self.chestGrid,(255, 242, 211)) == False:
                    print("Chest GUI not detected! Skipping this step.")
                    break

                sleep(self.gatherItemTime)
                pydirectinput.moveTo(self.hwndX + 532  ,self.hwndY + 269)
                pydirectinput.click()
            else:
                break

    def clickOrigin(self):
        pydirectinput.moveTo(self.hwndX,self.hwndY)
        pydirectinput.moveRel(1,1)
        pydirectinput.click()
        
    def run(self):

        sleep(1)


        # TODO: you can write your own time/iterations calculation to determine how fast this is
        while not self.stopped:
            
            #Update Hwnd position
            self.updateHWND(self.hwnd)

            #Activate window
            self.clickOrigin()

            #Check chat toggle
            if self.checkPixels(self.hwndX,self.hwndY,self.chatPixels,(255,255,255)):
                pydirectinput.moveTo(self.hwndX + 74,self.hwndY + 18)
                pydirectinput.moveRel(1,1)

                pydirectinput.click()

            #Start moving
            pydirectinput.keyDown('s')

            #Trigger until the chest are horizontally related to the player.
            self.chestCheck()

            #Stop moving
            pydirectinput.keyUp('s')

            ####################################################################
            ####################Harvest Chest To the Right######################
            ####################################################################

            #click the chest to the right
            self.ChestDirection(400, 200,0) 

            #Wait for the GUI to reappear
            #sleep(0.5)
            pydirectinput.moveTo(self.hwndX + 532  ,self.hwndY + 269)
            pydirectinput.moveRel(1,1)
            pydirectinput.moveRel(-1,-1)

            #Harvest items from the chest
            self.gatherItems()

            #Click the screen that is not in the chest gui so it exits the chest gui.
            pydirectinput.moveTo(self.hwndX + 609,self.hwndY + 480)
            pydirectinput.moveRel(1,1)
            pydirectinput.click()

            ####################################################################
            ####################Harvest Chest To the Left#######################
            ####################################################################

            #click the chest to the right
            self.ChestDirection(400, 200,1) 

            #Wait for the GUI to reappear
            #sleep(0.5)
            pydirectinput.moveTo(self.hwndX + 532  ,self.hwndY + 269)
            pydirectinput.moveRel(1,1)
            pydirectinput.moveRel(-1,-1)

            #Harvest items from the chest
            self.gatherItems()

            #Click the screen that is not in the chest gui so it exits the chest gui.
            pydirectinput.moveTo(self.hwndX + 609,self.hwndY + 480)
            pydirectinput.moveRel(1,1)
            pydirectinput.click()

            #Move orgin so it dosent pull of gui button on the chest
            self.clickOrigin()
                
            #Failsafe so it dosent stop at it's current postion where the chest at.
            pydirectinput.keyDown('s')
            sleep(0.5)

            pass