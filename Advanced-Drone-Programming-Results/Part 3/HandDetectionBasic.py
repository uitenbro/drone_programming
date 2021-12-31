import cvzone
from cvzone.HandTrackingModule import HandDetector
from cvzone.FaceDetectionModule import FaceDetector
import cv2
import math

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

handDetector = HandDetector()
faceDetector = FaceDetector()
cap = cv2.VideoCapture(0)

while True:
    _, img = cap.read()

    # face detection
    img, faceBboxs = faceDetector.findFaces(img, draw=True)

    # hand detection
    img = handDetector.findHands(img, draw=True)
    lmList, handBboxInfo = handDetector.findPosition(img, draw=True)

    gesture = ''
    if faceBboxs:
        # define region relative to the face for hand gesture detection
        x,y,w,h = faceBboxs[0]["bbox"]
        detectionRegion = x - 2*w, y, 2*w, h
        cvzone.cornerRect(img, detectionRegion)

        if handBboxInfo:
            # check if hand center is within the detection region
            handCenter = handBboxInfo["center"]
            thumb, index, middle, ring, pinky = handDetector.fingersUp()
            if (detectionRegion[0]+detectionRegion[2])>handCenter[0]>detectionRegion[0] and \
                    detectionRegion[1]<handCenter[1]<(detectionRegion[1]+detectionRegion[3]):

                # Hand Gesture detection
                if (index+middle) == 2 and (thumb+ring+pinky == 0):
                    gesture = "peace"
                elif (index+pinky+thumb == 3) and (middle+ring == 0):
                    gesture = "love you"
                elif (index+pinky == 2) and (middle+ring+thumb == 0):
                    gesture = "rock-n-roll"
                elif (thumb+pinky == 2) and (index+middle+ring == 0):
                    gesture = "shaka"

                cv2.putText(img, f'{gesture}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)



