from djitellopy import tello
from cvzone.FaceDetectionModule import FaceDetector
import cv2

detector = FaceDetector()

drone = tello.Tello()
drone.connect()
print(drone.get_battery())
drone.streamoff()
drone.streamon()


while True:
    img = drone.get_frame_read().frame
    img, bboxs = detector.findFaces(img, draw = True)
    cv2.imshow("face", img)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
drone.end()
