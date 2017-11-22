from picamera import PiCamera
from time import sleep
from fractions import Fraction
import os

PHOTO_LOCATION = '/home/pi/Pictures'

class CameraManager(object):
    def __init__(self):
        super(CameraManager, self).__init__()
        print 'initializing camera'
        self.camera = PiCamera(
            framerate=Fraction(1,10) 
            #resolution='3280x2464'
        )
        self.camera.rotation = 180
        sleep(2)
        print 'camera initialized'

    def set_day(self):
        print 'set_day started'
        self.camera.shutter_speed = int(1000000 * .2)
        self.camera.iso = 100
        sleep(4)  # give the camera a bit of time
        self.camera.exposure_mode = 'off'

        print 'set_day complete'
    def set_night(self):
        print 'set_night started'
        self.camera.shutter_speed = 1000000 * 10
        self.camera.iso = 800
        sleep(30)  # give the camera a long time to set gains and measure AWB (you may wish to use fixed AWB insetad)
        self.camera.exposure_mode = 'off'
        print 'set_night complete'

    def launch_preview(self, preview_time=3):
        self.camera.start_preview()
        sleep(preview_time)
        self.camera.stop_preview()

camera_man = CameraManager()
camera_man.set_day()
# camera_man.camera.capture(os.path.join(PHOTO_LOCATION, 'preview.jpg'))

for filename in camera_man.camera.capture_continuous(os.path.join(PHOTO_LOCATION, 'image{counter:04d}.jpg')):
    print 'Captured %s' % filename
    sleep(10)

