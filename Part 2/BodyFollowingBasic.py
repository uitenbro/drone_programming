from djitellopy import tello
from cvzone.PoseModule import PoseDetector
import cv2
import cvzone

plotX = cvzone.LivePlot(yLimit=[-100, 100], char='X')
plotY = cvzone.LivePlot(yLimit=[-100, 100], char='Y')
plotZ = cvzone.LivePlot(yLimit=[-100, 100], char='Z')

detector = PoseDetector(upBody=True)

drone = tello.Tello()
# drone.connect()
# print(drone.get_battery())
# drone.streamoff()
# drone.streamon()


webcam = cv2.VideoCapture(0)
_, img = webcam.read()
hi, wi = 480, 640
img = cv2.resize(img, (wi, hi))

while True:
    # img = drone.get_frame_read().frame
    _, img = webcam.read()
    img = cv2.resize(img, (wi, hi))

    # find body and draw bbox
    img = detector.findPose(img)
    landmarks, bbox = detector.findPosition(img)

    # draw center lines
    cv2.line(img, pt1=(0,hi//2), pt2=(wi,hi//2), color=(255,0,255), thickness=2)
    cv2.line(img, pt1=(wi//2,0), pt2=(wi//2,hi), color=(255,0,255), thickness=2)

    # if a body was found
    if bbox:
        # determine center and bbox area
        cx, cy = bbox['center']
        x,y,w,h = bbox['bbox']
        area = w*h

        # draw line from center of bbox and print area as a percent
        cv2.circle(img, (cx, cy), 5, [255, 0, 255], thickness=2)
        cv2.line(img, (cx, cy), (wi // 2, hi // 2), (25, 0, 255), thickness=2)
        cv2.putText(img, str(round(area/(wi*hi)*100))+"%", (cx-w//2, cy-h//2-50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

        # calculate error percents
        xErr = round(((cx-wi//2) / (wi//2)) * 50) # distance to center as percent of full distance
        yErr = round(((hi//2-cy) / (hi//2)) * 50) # distance to center as percent of full distance
        zErr = round(((0.33 - (area / (hi*wi))) / 0.33) * 100) # target 33% of the total area
        # limit forward and backward speed
        if zErr < - 50:
            zErr = - 50
        elif zErr > 25:
            zErr = 25
    else:
        # no body was found so zero out errors (forces stoppage of movement)
        xErr = 0
        yErr = 0
        zErr = 0

        # TODO: add movement to search for a face

    # plot errors
    imgPlotX = plotX.update(xErr)
    imgPlotY = plotY.update(yErr)
    imgPlotZ = plotZ.update(zErr)

    # combine images
    imgStacked = cvzone.stackImages([img, imgPlotZ, imgPlotX, imgPlotY], 2, 0.75)
    #cv2.imshow("face", img)
    cv2.imshow("face", imgStacked)

    # send remote control command backward/forward, left/right, down/up, spin ccw/spin cw
    # drone.send_rc_control(0, zErr, yErr, xErr)

    key = cv2.waitKey(5)
    if key & 0xFF == ord('q'):
        break
    elif key & 0xFF == ord('t'):
        drone.takeoff()

cv2.destroyAllWindows()
print(drone.get_battery())
drone.end()
