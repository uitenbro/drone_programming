from djitellopy import tello
import time

drone = tello.Tello()
drone.connect()

print(drone.get_battery())

drone.takeoff()
drone.move_up(30)

drone.send_rc_control(0,0,0,40)
time.sleep(5)
drone.send_rc_control(0,0,0,-40)
time.sleep(5)
drone.send_rc_control(0,0,0,0)
time.sleep(2)

drone.land()


