from djitellopy import tello
import cv2
import time

drone = tello.Tello()
drone.connect()
print(drone.get_battery())

drone.streamoff()
drone.streamon()

while True:
    time.sleep(2)
    # stop any previous velocity commands
    drone.send_rc_control(0, 0, 0, 0)

    # get video frame, resize and display it
    img = drone.get_frame_read().frame
    img = cv2.resize(img, (640, 480))
    cv2.imshow("drone image", img)

    # get operator input
    key = cv2.waitKey(5)
    if key & 0xFF == ord('q'):
        break
    elif key & 0xFF == ord('w'):
        drone.send_rc_control(0, 20, 0, 0)  # drone.move_forward(20)
    elif key & 0xFF == ord('s'):
        drone.send_rc_control(0, -20, 0, 0)  # drone.move_back(20)
    elif key & 0xFF == ord('d'):
        drone.send_rc_control(20, 0, 0, 0)  # drone.move_right(20)
    elif key & 0xFF == ord('a'):
        drone.send_rc_control(-20, 0, 0, 0)  # drone.move_left(20)
    elif key & 0xFF == ord('i'):
        drone.send_rc_control(0, 0, 20, 0)  # drone.move_up(20)
    elif key & 0xFF == ord('k'):
        drone.send_rc_control(0, 0, -20, 0)  # drone.move_down(20)
    elif key & 0xFF == ord('j'):
        drone.send_rc_control(0, 0, 0, 20)  # drone.rotate_clockwise(20)
    elif key & 0xFF == ord('l'):
        drone.send_rc_control(0, 20, 0, -20)  # drone.rotate_counter_clockwise(20)
    elif key & 0xFF == ord('g'):
        drone.takeoff()
    elif key & 0xFF == ord('h'):
        drone.land()

print(drone.get_battery())
drone.end()
cv2.destroyAllWindows()
exit()
