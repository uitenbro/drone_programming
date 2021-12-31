from djitellopy import tello
import cv2
import time

drone = tello.Tello()
drone.connect()
print(drone.get_battery())

drone.streamoff()
drone.streamon()

while True:
    img = drone.get_frame_read().frame
    img = cv2.resize(img, (640, 480))
    cv2.imshow("drone image", img)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        drone.streamoff()
        break

cv2.destroyAllWindows()
