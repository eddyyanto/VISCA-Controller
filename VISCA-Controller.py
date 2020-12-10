'''
   ____  __  ____   ________________  ___    __  ___
  / __ \/  |/  / | / /  _/ ____/ __ \/   |  /  |/  /
  / / / / /|_/ /  |/ // // / __/ /_/ / /| | / /|_/ /
  / /_/ / /  / / /|  // // /_/ / _, _/ ___ |/ /  / /
  \____/_/  /_/_/ |_/___/\____/_/ |_/_/  |_/_/  /_/

   Project  : VISCA Controller
   Author   : Eddy Yanto
   Created  : 10/12/2020
   Version  : 0.0.1

'''

# Qt related libraries
from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork
import sys, socket
from time import sleep

# Compiled Qt Ui (do not edit the Ui files, as they get overridden during build)
from MainWindow import Ui_MainWindow


camera_ip = '10.100.117.40'
camera_port = 52381
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP
buffer_size = 1024


sequence_number = 1
camera_on = '81 01 04 00 02 FF'
camera_off = '81 01 04 00 03 FF'

information_display_on = '81 01 7E 01 18 02 FF'
information_display_off = '81 01 7E 01 18 03 FF'

zoom_stop = '81 01 04 07 00 FF'
zoom_tele = '81 01 04 07 02 FF'
zoom_wide = '81 01 04 07 03 FF'
zoom_tele_variable = '81 01 04 07 2p FF' # p=0 (Low) to 7 (High)
zoom_wide_variable = '81 01 04 07 3p FF' # p=0 (Low) to 7 (High)
zoom_direct = '81 01 04 47 0p 0q 0r 0s FF' # pqrs: Zoom Position

memory_reset = '81 01 04 3F 00 0p FF'
memory_set = '81 01 04 3F 01 0p FF' # p: Memory number (=0 to F)
memory_recall = '81 01 04 3F 02 0p FF' # p: Memory number (=0 to F)

#Pan-tilt Drive
# VV: Pan speed setting 0x01 (low speed) to 0x18
# WW: Tilt speed setting 0x01 (low speed) to 0x17
movement_speed = '03'
pan_speed = movement_speed
tilt_speed = movement_speed

# YYYY: Pan Position DE00 to 2200 (CENTER 0000)
# ZZZZ: Tilt Position FC00 to 1200 (CENTER 0000)
#YYYY = '0000'
#ZZZZ = '0000'
pan_up = '81 01 06 01 VV WW 03 01 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_down = '81 01 06 01 VV WW 03 02 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_left = '81 01 06 01 VV WW 01 03 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_right = '81 01 06 01 VV WW 02 03 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_up_left = '81 01 06 01 VV WW 01 01 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_up_right = '81 01 06 01 VV WW 02 01 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_down_left = '81 01 06 01 VV WW 01 02 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_down_right = '81 01 06 01 VV WW 02 02 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_stop = '81 01 06 01 VV WW 03 03 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
#pan_absolute_position = '81 01 06 02 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF'.replace('VV', str(VV)) #YYYY[0]
#pan_relative_position = '81 01 06 03 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF'.replace('VV', str(VV))
pan_home = '81 01 06 04 FF'
pan_reset = '81 01 06 05 FF'
zoom_direct = '81 01 04 47 0p 0q 0r 0s FF' # pqrs: Zoom Position
zoom_focus_direct = '81 01 04 47 0p 0q 0r 0s 0t 0u 0v 0w FF' # pqrs: Zoom Position  tuvw: Focus Position

inquiry_lens_control = '81 09 7E 7E 00 FF'
# response: 81 50 0p 0q 0r 0s 0H 0L 0t 0u 0v 0w 00 xx xx FF
inquiry_camera_control = '81 09 7E 7E 01 FF'

focus_stop = '81 01 04 08 00 FF'
focus_far = '81 01 04 08 02 FF'
focus_near = '81 01 04 08 03 FF'
focus_far_variable = '81 01 04 08 2p FF'.replace('p', '7') # 0 low to 7 high
focus_near_variable = '81 01 04 08 3p FF'.replace('p', '7') # 0 low to 7 high
focus_direct = '81 01 04 48 0p 0q 0r 0s FF' #.replace('p', ) q, r, s
focus_auto = '81 01 04 38 02 FF'
focus_manual = '81 01 04 38 03 FF'
focus_infinity = '81 01 04 18 02 FF'


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setFixedSize(960, 480) # get width and height from MainWindow UI

        self.btnZoomIn.pressed.connect(self.zoomInPressed)
        self.btnZoomIn.released.connect(self.zoomInReleased)
        self.btnZoomOut.pressed.connect(self.zoomOutPressed)
        self.btnZoomOut.released.connect(self.zoomOutReleased)

        self.btnNavUp.pressed.connect(self.navUpPressed)
        self.btnNavUp.released.connect(self.navUpReleased)

        self.btnNavUpRight.pressed.connect(self.navUpRightPressed)
        self.btnNavUpRight.released.connect(self.navUpRightReleased)

        self.btnNavRight.pressed.connect(self.navRightPressed)
        self.btnNavRight.released.connect(self.navRightReleased)

        self.btnNavDownRight.pressed.connect(self.navDownRightPressed)
        self.btnNavDownRight.released.connect(self.navDownRightReleased)

        self.btnNavDown.pressed.connect(self.navDownPressed)
        self.btnNavDown.released.connect(self.navDownReleased)

        self.btnNavDownLeft.pressed.connect(self.navDownLeftPressed)
        self.btnNavDownLeft.released.connect(self.navDownLeftReleased)        

        self.btnNavLeft.pressed.connect(self.navLeftPressed)
        self.btnNavLeft.released.connect(self.navLeftReleased)

        self.btnNavUpLeft.pressed.connect(self.navUpLeftPressed)
        self.btnNavUpLeft.released.connect(self.navUpLeftReleased)

        self.btnPreset1.pressed.connect(self.preset1)
        self.btnPreset2.pressed.connect(self.preset2)
        self.btnPreset3.pressed.connect(self.preset3)
        self.btnPreset4.pressed.connect(self.preset4)
        self.btnPreset5.pressed.connect(self.preset5)
        self.btnPreset6.pressed.connect(self.preset6)
        self.btnPreset7.pressed.connect(self.preset7)
        self.btnPreset8.pressed.connect(self.preset8)
        self.btnPreset9.pressed.connect(self.preset9)


    def zoomInPressed(self):
        self.send_message(zoom_tele)

    def zoomInReleased(self):
        self.send_message(zoom_stop)

    def zoomOutPressed(self):
        self.send_message(zoom_wide)

    def zoomOutReleased(self):
        self.send_message(zoom_stop)

    def navUpPressed(self):
        self.send_message(pan_up)

    def navUpReleased(self):
        self.send_message(pan_stop)

    def navUpLeftPressed(self):
        self.send_message(pan_up_left)

    def navUpLeftReleased(self):
        self.send_message(pan_stop)

    def navLeftPressed(self):
        self.send_message(pan_left)

    def navLeftReleased(self):
        self.send_message(pan_stop)

    def navDownLeftPressed(self):
        self.send_message(pan_down_left)

    def navDownLeftReleased(self):
        self.send_message(pan_stop)

    def navDownPressed(self):
        self.send_message(pan_down)

    def navDownReleased(self):
        self.send_message(pan_stop)

    def navDownRightPressed(self):
        self.send_message(pan_down_right)

    def navDownRightReleased(self):
        self.send_message(pan_stop)

    def navRightPressed(self):
        self.send_message(pan_right)

    def navRightReleased(self):
        self.send_message(pan_stop)

    def navUpRightPressed(self):
        self.send_message(pan_up_right)

    def navUpRightReleased(self):
        self.send_message(pan_stop)

    def preset1(self):
        self.memory_recall_function(1)

    def preset2(self):
        self.memory_recall_function(2)

    def preset3(self):
        self.memory_recall_function(3)

    def preset4(self):
        self.memory_recall_function(4)

    def preset5(self):
        self.memory_recall_function(5)

    def preset6(self):
        self.memory_recall_function(6)

    def preset7(self):
        self.memory_recall_function(7)

    def preset8(self):
        self.memory_recall_function(8)

    def preset9(self):
        self.memory_recall_function(9)


    def memory_recall_function(self, memory_number):
        message_string = memory_recall.replace('p', str(memory_number))
        self.send_message(information_display_off) # otherwise we see a message on the camera output
        sleep(0.25)
        message = self.send_message(message_string)
        sleep(1)
        self.send_message(information_display_off)
        return message

    def send_message(self, message_string):
        global sequence_number
        #global received_message
        payload_type = bytearray.fromhex('01 00')
        payload = bytearray.fromhex(message_string)
        payload_length = len(payload).to_bytes(2, 'big')
        message = payload_type + payload_length + sequence_number.to_bytes(4, 'big') + payload
        sequence_number += 1
        s.sendto(message, (camera_ip, camera_port))



if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())