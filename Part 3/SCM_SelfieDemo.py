from djitellopy import tello
from cvzone.PoseModule import PoseDetector
import cv2
import numpy as np
import cvzone
from datetime import datetime
import time
import math

def takePhoto(img, xVal, yVal, zVal):
    global takingPhoto
    global pauseTime

    # if this is the first time calling this function set takingPhoto to true and flip the drone
    if takingPhoto == False:
        takingPhoto = True
        # drone.flip_back()
        pauseTime = time.time() + 2
    else:
        # print(f'now: {time.time()} pause till: {pauseTime}')
        # taking photo is true so check if errors are small
        if (pauseTime < time.time()) and (-10<xVal<10 and -10<yVal<10 and -10<zVal<10):
            # save the photo with the timestamp as the name
            cv2.imwrite(f'{datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}.jpg', img)

            # done saving photo so flip and reset the takingPhoto state to false
            # drone.flip_forward()
            print('took photo')
            takingPhoto = False

def findDistance(lmList, p1, p2, img, draw=True, r=15, t=3):
    x1, y1 = lmList[p1][1:]
    x2, y2 = lmList[p2][1:]
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    length = math.hypot(x2 - x1, y2 - y1)

    if draw:
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
        cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
        cv2.putText(img, f'{length:0.0f}', (cx-50, cy+50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

    return length, img, [x1, y1, x2, y2, cx, cy]

drone = tello.Tello()
# drone.connect()
# print(drone.get_battery())
# drone.streamoff()
# drone.streamon()

hi, wi = 480, 640

detector = PoseDetector(upBody=True)
webcam = cv2.VideoCapture(0)
_, img = webcam.read()
img = cv2.resize(img, (wi, hi))

isFlying = False
takingPhoto = False
pauseTime = 0.0

bodyAreaTarget = round(0.25*wi*hi) # 33% of the overall area

#                   P   I  D
xPID = cvzone.PID([0.22, 0, 0.15], wi // 2, limit=[-100,100])
yPID = cvzone.PID([0.27, 0, 0.1], hi // 2, axis=1, limit=[-100,100])
zPID = cvzone.PID([0.0006, 0.00000, 0.000015], bodyAreaTarget,limit=[-100,100])

plotX = cvzone.LivePlot(yLimit=[-100, 100], char='X')
plotY = cvzone.LivePlot(yLimit=[-100, 100], char='Y')
plotZ = cvzone.LivePlot(yLimit=[-100, 100], char='Z')

while True:
    # get image
    #img = drone.get_frame_read().frame
    _, img = webcam.read()

    # save original image
    imgOrig = img

    # resize then find face and draw bbox
    img = cv2.resize(img, (wi, hi))
    img = detector.findPose(img, draw=True)
    landmarks, bbox = detector.findPosition(img, draw=True)
    # draw center lines on image
    cv2.line(img, pt1=(0,yPID.targetVal), pt2=(wi,yPID.targetVal), color=(255,0,255), thickness=2)
    cv2.line(img, pt1=(wi//2,0), pt2=(wi//2,hi), color=(255,0,255), thickness=2)

    gesture = ""

    # if a body was found
    if bbox:
        # extract center and area of bbox
        cx, cy = bbox['center']
        x,y,w,h = bbox['bbox']
        area = w*h

        # draw circle at center of upper body
        cv2.circle(img, (cx, cy), 5, [255, 0, 255], thickness=2)
        # draw line from center of upper body to center of view
        cv2.line(img, (cx, cy), (wi // 2, yPID.targetVal), (25, 0, 255), thickness=2)
        # print the area of the upper body bbox in square-pixels
        cv2.putText(img, str(round(area/(wi*hi)*100))+"%", (cx-w//2, cy-yPID.targetVal-50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

        # update PID controls based on current position
        xVal = int(xPID.update(cx))
        yVal = -int(yPID.update(cy))
        zVal = -int(zPID.update(area))
        wVal = xVal  # set left right control equal to CCW, CW control to improve tracking

        # If gestures are found override tracking control
        angArmL = detector.findAngle(img, 13, 11, 23, draw=True)
        angArmR = detector.findAngle(img, 14, 12, 24, draw=True)
        angElbowL = detector.findAngle(img, 11, 13, 15, draw=True)
        angElbowR = detector.findAngle(img, 12, 14, 16, draw=True)
        # wristDistance, img, _ = findDistance(landmarks, 15, 16, img)
        # wristShoulderDistance1, img, _ = findDistance(landmarks, 12, 16, img)
        # wristShoulderDistance2, img, _ = findDistance(landmarks, 11, 15, img)

        # check for  photo request
        if ((angArmL > 80 and angArmL < 100) and (angArmR > 260 and angArmR < 280)) or takingPhoto:
            gesture = "Take Photo"
            takePhoto(imgOrig, xVal, yVal, zVal)

        # track body
        if angArmL > 80 and angArmL < 100:
            if angElbowL < 100:
                gesture = 'Down'
                yVal = -33
                # yPID.targetVal = np.clip(yPID.targetVal - (hi // 100), 50, hi-50)  # decrease PID target 1%
            else:
                gesture = 'Left'
                wVal = 33 # move left
        if angArmR > 260 and angArmR < 280:
            if angElbowR > 260:
                gesture = 'Down'
                yVal = -33
                # yPID.targetVal = np.clip(yPID.targetVal - (hi // 100), 50, hi-50)  # decrease PID target 1%
            else:
                gesture = 'Right'
                wVal = -33 # move right
        if (angArmR > 180 and angArmR < 200) or (angArmL > 160 and angArmL < 180):
            gesture = 'Up'
            yVal = 33
            #yPID.targetVal = np.clip(yPID.targetVal + (hi//100), 50, hi-50) # increase PID target 1%
        # if wristDistance < 50 and (wristShoulderDistance1 < 50 and wristShoulderDistance2 < 50):
        #     gesture = "Cross"
        #     #drone.land();
        #     isFlying = False
    else:
        # no body was found so zero out errors (forces stoppage of movement)
        xVal = 0
        yVal = 0
        zVal = 0
        wVal = 0

        # TODO: add movement to search for a face

    # plot values
    imgPlotX = plotX.update(xVal)
    imgPlotY = plotY.update(yVal)
    imgPlotZ = plotZ.update(zVal)

    # combine images
    cv2.putText(img, f'{gesture}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
    imgStacked = cvzone.stackImages([img, imgPlotZ, imgPlotX, imgPlotY], 2, 0.75)
    #cv2.imshow("drone view", img)
    cv2.imshow("drone view", imgStacked)

    # if isFlying:
    #     # command the drone to move
    #     drone.send_rc_control(wVal, zVal, yVal, xVal)

    key = cv2.waitKey(5)
    if key & 0xFF == ord('q'):
        break
    elif key & 0xFF == ord('t'):
        drone.takeoff()
        isFlying = True

# print(drone.get_battery())
cv2.destroyAllWindows()
# print(drone.get_battery())
# drone.end()
