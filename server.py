from picamera import PiCamera
from time import sleep
from fractions import Fraction
import os
from PIL import ImageStat
from PIL import Image
from datetime import datetime

PHOTO_LOCATION = '/home/pi/Pictures'

class CameraManager(object):
    def __init__(self):
        super(CameraManager, self).__init__()
        print 'initializing camera'
        self.camera = PiCamera(
            framerate=Fraction(1,10),
            resolution=(3240,2464)  # if code throws an out of memory error, use raspi-config to set gpu memory to 256mb
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

    def increase_sensor_sensitivity(self):
        print 'increase_sensor_sensitivity: starting'
        # set ISO
        iso_values = [100, 200, 320, 400, 500, 640, 800]

        # if ISO is 0 (auto), set it to 100
        if self.camera.iso == 0:
            self.camera.iso = 100
            print 'increase_sensor_sensitivity: setting iso from auto to %d' % (self.camera.iso)
            return True
        # if the current ISO value is lower than the max ISO value, increase it to the next ISO setting
        elif iso_values.index(self.camera.iso) < (len(iso_values) - 1):
            old_camera_iso = self.camera.iso
            self.camera.iso = iso_values[iso_values.index(self.camera.iso) + 1]
            print 'increase_sensor_sensitivity: increasing iso %d to %d' % (old_camera_iso, self.camera.iso)
            return True

        # if the shutter speed is under its max, increase the shutter speed by 102%
        if self.camera.shutter_speed < 1000000 * 30:
            old_shutter_speed = self.camera.shutter_speed
            self.camera.shutter_speed = int(self.camera.shutter_speed * 1.02)
            print 'increase_sensor_sensitivity: increasing shutter speed from %s to %s' % (old_shutter_speed, self.camera.shutter_speed)
            return True
        print 'increase_sensor_sensitivity: sensor is at most sensitive (iso: %d, shutter_speed %s)' % (self.camera.iso, self.camera.shutter_speed)
    
    def decrease_sensor_sensitivity(self):
        print 'decrease_sensor_sensitivity: starting'
        # set ISO
        iso_values = [100, 200, 320, 400, 500, 640, 800]

        # if ISO is 0 (auto), set it to 800
        if self.camera.iso == 0:
            self.camera.iso = 800
            print 'decrease_sensor_sensitivity: setting iso from auto to %d' % (self.camera.iso)
            return True
        # if the current ISO value is higher than the lowest ISO value, decrease it to the next lowest ISO setting
        elif iso_values.index(self.camera.iso) > 0:
            old_camera_iso = self.camera.iso
            self.camera.iso = iso_values[iso_values.index(self.camera.iso) - 1]
            print 'increase_sensor_sensitivity: decreasing iso %d to %d' % (old_camera_iso, self.camera.iso)
            return True

        # if the shutter speed is over 1/1000, decrease the shutter speed by 102%
        if self.camera.shutter_speed > 1000000 * (1/1000.0):
            old_shutter_speed = self.camera.shutter_speed
            self.camera.shutter_speed = int(self.camera.shutter_speed / 1.02)
            print 'decrease_sensor_sensitivity: decreasing shutter speed from %s to %s' % (old_shutter_speed, self.camera.shutter_speed)
            return True
        print 'decrease_sensor_sensitivity: sensor is at least sensitive (iso: %d, shutter_speed %s)' % (self.camera.iso, self.camera.shutter_speed)

    def calibrate_sensor(self, calibration_image_path, desired_brightness=120):
        """
        Calibrates the sensor based on the image at calibration_image_path
        Does so by examining the brightness of the image and comparing against the desired brightness
        If the brightness is too high, the camera will lower ISO sensitivity and shutter speed
        If the brightness is too low, the camera will increase ISO sensitivity and shutter speed
        Give priority first to ISO sensitivity, then shutter speed
        """
        print 'calibrate_sensor: Beginning sensor calibration'
        current_brightness = CameraManager.get_image_brightness(calibration_path)
        brightness_diff = current_brightness - desired_brightness
        print 'calibration_sensor: current_brightness=%d desired_brightness=%d brightness_diff=%d' % (current_brightness, desired_brightness, brightness_diff)
        if brightness_diff > 20:
            print 'calibration_sensor: decrease_sensor_sensitivity'
            self.decrease_sensor_sensitivity()
        elif brightness_diff < -20:
            print 'calibration_sensor: increase_sensor_sensitivity'
            self.increase_sensor_sensitivity()
        print 'calibrate_sensor: Completed sensor calibration'

    @staticmethod
    def get_image_brightness(image_path):
        img = Image.open(image_path).convert('L')
        stat = ImageStat.Stat(img)
        return stat.mean[0]

if __name__ == '__main__':
    camera_man = CameraManager()
    if datetime.now().hour > 8 and datetime.now().hour < 18:
        camera_man.set_day()
    else:
        camera_man.set_night()

    i = 0
    for filename in camera_man.camera.capture_continuous(os.path.join(PHOTO_LOCATION, 'image{counter:04d}.jpg')):
        print 'Iteration %d: Captured %s' % (i, filename)
        i += 1

        if(i % 2 == 0):
            camera_man.calibrate_sensor(filename)

        sleep(10)

