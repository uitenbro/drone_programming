from djitellopy import tello
from cvzone.FaceDetectionModule import FaceDetector
import cv2
import cvzone

plotX = cvzone.LivePlot(yLimit=[-100, 100], char='X')
plotY = cvzone.LivePlot(yLimit=[-100, 100], char='Y')
plotZ = cvzone.LivePlot(yLimit=[-100, 100], char='Z')

detector = FaceDetector(minDetectionCon=0.60)

drone = tello.Tello()
drone.connect()
print(drone.get_battery())
drone.streamoff()
drone.streamon()


#webcam = cv2.VideoCapture(1)
#_, img = webcam.read()
#img = cv2.resize(img, (640, 480))
#hi, wi, _ = img.shape
hi = 480
wi = 640

while True:
    img = drone.get_frame_read().frame
    #_, img = webcam.read()
    img = cv2.resize(img, (640, 480))
    img, bboxs = detector.findFaces(img, draw = True)
    # draw center lines
    cv2.line(img, pt1=(0,hi//2), pt2=(wi,hi//2), color=(255,0,255), thickness=2)
    cv2.line(img, pt1=(wi//2,0), pt2=(wi//2,hi), color=(255,0,255), thickness=2)

    if bboxs:
        cx, cy = bboxs[0]['center']
        cv2.circle(img, (cx,cy), 5, [255,0,255], thickness=2)
        cv2.line(img, (cx,cy), (wi//2,hi//2), (25,0,255), thickness=2)
        x,y,w,h = bboxs[0]['bbox']
        area = w*h
        cv2.putText(img, str(area), (cx-w//2, cy+h//2+50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

        # calculate error percents
        xErr = round(((cx-wi//2) / (wi//2)) * 50) # distance to center as percent of full distance
        yErr = round(((hi//2-cy) / (hi//2)) * 50) # distance to center as percent of full distance
        zErr = round(((0.02 - (area / (hi*wi))) / 0.2) * 100) # target 2% of the total area
        if zErr < - 100:
            zErr = - 100
        elif zErr > 25:
            zErr = 25
    else:
        # no face was found so zero out errors (forces stoppage of movement)
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
    drone.send_rc_control(0, zErr, yErr, xErr)

    key = cv2.waitKey(5)
    if key & 0xFF == ord('q'):
        break
    elif key & 0xFF == ord('t'):
        drone.takeoff()

cv2.destroyAllWindows()
print(drone.get_battery())
drone.end()
