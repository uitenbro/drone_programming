from cvzone.PoseModule import PoseDetector
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

detector = PoseDetector(upBody=True)
cap = cv2.VideoCapture(0)

while True:
    _, img = cap.read()

    img = detector.findPose(img, draw=True)
    lmList, bboxInfo = detector.findPosition(img, draw=True)

    gesture = ''
    if bboxInfo:
        angArmL = detector.findAngle(img, 13, 11, 23, draw=True)
        angArmR = detector.findAngle(img, 14, 12, 24, draw=True)
        wristDistance, img, _ = findDistance(lmList, 15, 16, img)

        if angArmL > 80 and angArmL < 100:
            gesture = 'Left'
        if angArmR > 260 and angArmR < 280:
            gesture = 'Right'
        if (wristDistance < 100):
            gesture = 'Cross'

        cv2.putText(img, f'{gesture}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)



