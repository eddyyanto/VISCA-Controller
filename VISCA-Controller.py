'''
   ____  __  ____   ________________  ___    __  ___
  / __ \/  |/  / | / /  _/ ____/ __ \/   |  /  |/  /
  / / / / /|_/ /  |/ // // / __/ /_/ / /| | / /|_/ /
  / /_/ / /  / / /|  // // /_/ / _, _/ ___ |/ /  / /
  \____/_/  /_/_/ |_/___/\____/_/ |_/_/  |_/_/  /_/

   Project  : VISCA Controller
   Author   : Eddy Yanto
   Created  : 10/12/2020
   Updated  : 14/12/2020
   Version  : 0.0.1

'''

# Qt related libraries
from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork
from PyQt5.QtWidgets import QMessageBox
from time import sleep
import sys
import xml.etree.ElementTree as ET

# Compiled Qt Ui (do not edit the Ui files, as they get overridden during build)
from MainWindow import Ui_MainWindow


CAMERA_PORT = 52381

SEQUENCE_NUMBER = 1

CAMERA_ON               = '81 01 04 00 02 FF'
CAMERA_OFF              = '81 01 04 00 03 FF'

INFORMATION_DISPLAY_ON  = '81 01 7E 01 18 02 FF'
INFORMATION_DISPLAY_OFF = '81 01 7E 01 18 03 FF'

ZOOM_STOP               = '81 01 04 07 00 FF'
ZOOM_TELE               = '81 01 04 07 02 FF'
ZOOM_WIDE               = '81 01 04 07 03 FF'
ZOOM_TELE_VARIABLE      = '81 01 04 07 2p FF' # p=0 (Low) to 7 (High)
ZOOM_WIDE_VARIABLE      = '81 01 04 07 3p FF' # p=0 (Low) to 7 (High)
ZOOM_DIRECT             = '81 01 04 47 0p 0q 0r 0s FF' # pqrs: Zoom Position

MEMORY_RESET            = '81 01 04 3F 00 0p FF'
MEMORY_SET              = '81 01 04 3F 01 0p FF' # p: Memory number (=0 to F)
MEMORY_RECALL           = '81 01 04 3F 02 0p FF' # p: Memory number (=0 to F)

#Pan-tilt Drive
# VV: Pan speed setting 0x01 (low speed) to 0x18
# WW: Tilt speed setting 0x01 (low speed) to 0x17
MOVEMENT_SPEED  = '03'
PAN_SPEED       = MOVEMENT_SPEED
TILT_SPEED      = MOVEMENT_SPEED

# YYYY: Pan Position DE00 to 2200 (CENTER 0000)
# ZZZZ: Tilt Position FC00 to 1200 (CENTER 0000)
#YYYY = '0000'
#ZZZZ = '0000'
PAN_UP                  = '81 01 06 01 VV WW 03 01 FF'#.replace('VV', str(PAN_SPEED)).replace('WW', str(TILT_SPEED))
PAN_DOWN                = '81 01 06 01 VV WW 03 02 FF'#.replace('VV', str(PAN_SPEED)).replace('WW', str(TILT_SPEED))
PAN_LEFT                = '81 01 06 01 VV WW 01 03 FF'#.replace('VV', str(PAN_SPEED)).replace('WW', str(TILT_SPEED))
PAN_RIGHT               = '81 01 06 01 VV WW 02 03 FF'#.replace('VV', str(PAN_SPEED)).replace('WW', str(TILT_SPEED))
PAN_UP_LEFT             = '81 01 06 01 VV WW 01 01 FF'#.replace('VV', str(PAN_SPEED)).replace('WW', str(TILT_SPEED))
PAN_UP_RIGHT            = '81 01 06 01 VV WW 02 01 FF'#.replace('VV', str(PAN_SPEED)).replace('WW', str(TILT_SPEED))
PAN_DOWN_LEFT           = '81 01 06 01 VV WW 01 02 FF'#.replace('VV', str(PAN_SPEED)).replace('WW', str(TILT_SPEED))
PAN_DOWN_RIGHT          = '81 01 06 01 VV WW 02 02 FF'#.replace('VV', str(PAN_SPEED)).replace('WW', str(TILT_SPEED))
PAN_STOP                = '81 01 06 01 VV WW 03 03 FF'#.replace('VV', str(PAN_SPEED)).replace('WW', str(TILT_SPEED))
PAN_HOME                = '81 01 06 04 FF'
PAN_RESET               = '81 01 06 05 FF'
ZOOM_DIRECT             = '81 01 04 47 0p 0q 0r 0s FF' # pqrs: Zoom Position
ZOOM_FOCUS_DIRECT       = '81 01 04 47 0p 0q 0r 0s 0t 0u 0v 0w FF' # pqrs: Zoom Position  tuvw: Focus Position

INQUIRY_LENS_CONTROL    = '81 09 7E 7E 00 FF'
INQUIRY_CAMERA_CONTROL  = '81 09 7E 7E 01 FF'

FOCUS_STOP              = '81 01 04 08 00 FF'
FOCUS_FAR               = '81 01 04 08 02 FF'
FOCUS_NEAR              = '81 01 04 08 03 FF'
FOCUS_FAR_VARIABLE      = '81 01 04 08 2p FF'.replace('p', '7') # 0 low to 7 high
FOCUS_NEAR_VARIABLE     = '81 01 04 08 3p FF'.replace('p', '7') # 0 low to 7 high
FOCUS_DIRECT            = '81 01 04 48 0p 0q 0r 0s FF' #.replace('p', ) q, r, s
FOCUS_AUTO              = '81 01 04 38 02 FF'
FOCUS_MANUAL            = '81 01 04 38 03 FF'
FOCUS_INFINITY          = '81 01 04 18 02 FF'


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setFixedSize(960, 480)

        self.actionAbout.triggered.connect(self.showAbout)

        self.btnZoomTele.pressed.connect(self.zoomTelePressed)
        self.btnZoomTele.released.connect(self.zoomTeleReleased)
        self.btnZoomWide.pressed.connect(self.zoomWidePressed)
        self.btnZoomWide.released.connect(self.zoomWideReleased)

        self.btnFocusFar.pressed.connect(self.focusFarPressed)
        self.btnFocusFar.released.connect(self.focusFarReleased)
        self.btnFocusNear.pressed.connect(self.focusNearPressed)
        self.btnFocusNear.released.connect(self.focusNearReleased)

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

        self.sldPanSpeed.sliderReleased.connect(self.panSpeedHandler)

        self.udpSocket = QtNetwork.QUdpSocket(self)
        self.udpSocket.bind(7001)
        self.udpSocket.readyRead.connect(self.processPendingDatagrams)


        xmlRoot = ET.parse('config.xml').getroot()
        for camera in xmlRoot.findall('camera'):
            camIp = camera.get('ip')
            self.cmbCameras.addItem(camIp)

        self.reset_sequence_number_function()

    def processPendingDatagrams(self):
        while self.udpSocket.hasPendingDatagrams():
            datagram, host, port = self.udpSocket.readDatagram(self.udpSocket.pendingDatagramSize())
            print(datagram)

    def showAbout(self):
       msg = QMessageBox()
       msg.setIcon(QMessageBox.Information)

       msg.setText("VISCA Controller v0.1\t")
       msg.setInformativeText("Release: 14/12/2020\nAuthor: Eddy Yanto")
       msg.setWindowTitle("VISCA Controller")
       msg.setStandardButtons(QMessageBox.Ok)
       msg.exec()

    def panSpeedHandler(self):
        global MOVEMENT_SPEED
        MOVEMENT_SPEED = self.sldPanSpeed.value()

    def zoomTelePressed(self):
        self.send_message(ZOOM_TELE)

    def zoomTeleReleased(self):
        self.send_message(ZOOM_STOP)

    def zoomWidePressed(self):
        self.send_message(ZOOM_WIDE)

    def zoomWideReleased(self):
        self.send_message(ZOOM_STOP)

    def focusFarPressed(self):
        self.send_message(FOCUS_FAR)

    def focusFarReleased(self):
        self.send_message(FOCUS_STOP)

    def focusNearPressed(self):
        self.send_message(FOCUS_NEAR)

    def focusNearReleased(self):
        self.send_message(FOCUS_STOP)

    def navUpPressed(self):
        self.send_message(PAN_UP)

    def navUpReleased(self):
        self.send_message(PAN_STOP)

    def navUpLeftPressed(self):
        self.send_message(PAN_UP_LEFT)

    def navUpLeftReleased(self):
        self.send_message(PAN_STOP)

    def navLeftPressed(self):
        self.send_message(PAN_LEFT)

    def navLeftReleased(self):
        self.send_message(PAN_STOP)

    def navDownLeftPressed(self):
        self.send_message(PAN_DOWN_LEFT)

    def navDownLeftReleased(self):
        self.send_message(PAN_STOP)

    def navDownPressed(self):
        self.send_message(PAN_DOWN)

    def navDownReleased(self):
        self.send_message(PAN_STOP)

    def navDownRightPressed(self):
        self.send_message(PAN_DOWN_RIGHT)

    def navDownRightReleased(self):
        self.send_message(PAN_STOP)

    def navRightPressed(self):
        self.send_message(PAN_RIGHT)

    def navRightReleased(self):
        self.send_message(PAN_STOP)

    def navUpRightPressed(self):
        self.send_message(PAN_UP_RIGHT)

    def navUpRightReleased(self):
        self.send_message(PAN_STOP)

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
        message_string = MEMORY_RECALL.replace('p', str(memory_number))
        message = self.send_message(message_string)
        return message

    def send_message(self, message_string):
        global SEQUENCE_NUMBER

        message_string = message_string.replace('VV', str(MOVEMENT_SPEED).zfill(2)).replace('WW', str(MOVEMENT_SPEED).zfill(2))

        payload_type = bytearray.fromhex('01 00')
        payload = bytearray.fromhex(message_string)
        payload_length = len(payload).to_bytes(2, 'big')
        message = payload_type + payload_length + SEQUENCE_NUMBER.to_bytes(4, 'big') + payload
        SEQUENCE_NUMBER += 1
        print(message)

        try:
            data = message
            hostAddress = QtNetwork.QHostAddress(str(self.cmbCameras.currentText()))
            self.udpSocket.writeDatagram(data, hostAddress, CAMERA_PORT)
        except:
            print("error")

    def reset_sequence_number_function(self):
        global SEQUENCE_NUMBER
        RESET_SEQUENCE_NUMBER_MESSAGE = bytearray.fromhex('02 00 00 01 00 00 00 01 01')
        try:
            data = RESET_SEQUENCE_NUMBER_MESSAGE
            hostAddress = QtNetwork.QHostAddress(str(self.cmbCameras.currentText()))
            self.udpSocket.writeDatagram(data, hostAddress, CAMERA_PORT)
        except:
            print("error")

        SEQUENCE_NUMBER = 1
        return SEQUENCE_NUMBER


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())