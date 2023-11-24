import cv2 as cv
import numpy as np
import os
import time

from bot import Bot
from windowcapture import WindowCapture
from vision import Vision
from detection import Detection

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their 
# own folder on GitHub#
os.chdir(os.path.dirname(os.path.abspath(__file__)))


DEBUG = True


wincap = WindowCapture('Roblox')
vision = Vision()
bot    = Bot('Roblox')

# load the trained model
# detector = Detection('cascade.xml')

cascade = cv.CascadeClassifier('cascade.xml')

wincap.start()
bot.start()
# detector.start()


font = cv.FONT_HERSHEY_SIMPLEX
  
# fontScale
fontScale = 0.5
   
# Blue color in BGR
color = (0, 0, 255)
  
# Line thickness of 2 px
thickness = 1
   
# Using cv2.putText() method

DEBUG = True

while(True):

    if wincap.screenshot is None:
        continue
    


    # do object detection
    # Dumb  --> detector.update(wincap.screenshot)

    rectangles = cascade.detectMultiScale(wincap.screenshot)

    rectangles = [face for face in rectangles if 30 <= face[2] <= 80]

    # merge rectangles near
    combined_squares = vision.process1(rectangles)
    #print(combined_squares)

    # give bot the positions of the squares
    bot.update_targets(combined_squares)



    if DEBUG:
        for a in combined_squares:
            x, y, w, h = a

            stringy = "T2 Chest"#str(w) + " " + str(h)
            cv.rectangle(wincap.screenshot, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv.putText(wincap.screenshot, stringy, (x, y), font, fontScale, color, thickness, cv.LINE_AA)

        cv.imshow('Matches', wincap.screenshot)
        cv.moveWindow('Matches', 873, 0)    
            




    

    key = cv.waitKey(1)
    if key == ord('q'):
        wincap.stop()
        bot.stop()
        # detector.stop()
        cv.destroyAllWindows()
        break

print('Done.')
