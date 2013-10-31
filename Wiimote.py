import time
from bluetooth import BluetoothSocket, L2CAP

class Wiimote:
    def __init__(self, addr):
        self._addr = addr
        self._inSocket = BluetoothSocket(L2CAP)
        self._outSocket = BluetoothSocket(L2CAP)
        self._connected = False

    def __del__(self):
        self.disconnect()

    def _send(self, *data):
        self._inSocket.send(reduce(lambda x, y: x + chr(y), data, ''))
        return True

    def disconnect(self):
        if self._connected:
            self._inSocket.close()
            self._outSocket.close()
            self._connected = False

    def connect(self):
        if self._connected:
            return None

        self._inSocket.connect((self._addr, 0x13)
        self._outSocket.connect((self._addr, 0x11))

        # TODO give the choice of the mode to the user
        # Set the mode of the data reporting of the Wiimote with the last byte of this sending
        # 0x30 : Only buttons (2 bytes)
        # 0x31 : Buttons and Accelerometer (3 bytes)
        # 0x32 : Buttons + Extension (8 bytes)
        # 0x33 : Buttons + Accel + InfraRed sensor (12 bytes)
        # 0x34 : Buttons + Extension (19 bytes)
        # 0x35 : Buttons + Accel + Extension (16 bytes)
        # 0x36 : Buttons + IR sensor (10 bytes) + Extension (9 bytes)
        # 0x37 : Buttons + Accel + IR sensor (10 bytes) + Extension (6 bytes)
        # 0x3d : Extension (21 bytes)
        # 0x3e / 0x3f : Buttons + Accel + IR sensor (36 bytes). Need two reports for a sigle data unit.
        self._send(0x52, 0x12, 0x00, 0x33)

        # Enable the IR camera
        # Enable IR Camera (Send 0x04 to Output Report 0x13)
        # Enable IR Camera 2 (Send 0x04 to Output Report 0x1a)
        # Write 0x08 to register 0xb00030
        # Write Sensitivity Block 1 to registers at 0xb00000
        # Write Sensitivity Block 2 to registers at 0xb0001a
        # Write Mode Number to register 0xb00033
        # Write 0x08 to register 0xb00030 (again)
        # Put a sleep of 50ms to avoid a bad configuration of the IR sensor
        time.sleep(0.050); self._send(0x52, 0x13, 0x04)
        time.sleep(0.050); self._send(0x52, 0x1a, 0x04)
        # TODO

        self._connected = True

    def vibrate(self, duration=1):
        if not self._connected:
            return None
        self._send(0x52, 0x15, 0x01)
        time.sleep(duration)
        self._send(0x52, 0x15, 0x00)

    def setLed(self, binary):
        if not self._connected:
            return None
        self._send(0x52, 0x11, int(n << 4))

    def _getData(self):
        return [ord(b) for b in self._inSocket.recv(19)]

    def _checkButton(self, bit, mask):
        return self._getData()[bit] & mask != 0

    def buttonAPressed(self):
        if not self._connected:
            return None
        return self._checkButton(3, 0x08)

    def buttonBPressed(self):
        if not self._connected:
            return None
        return self._checkButton(3, 0x04)

    def buttonUpPressed(self):
        if not self._connected:
            return None
        return self._checkButton(2, 0x08)

    def buttonDownPressed(self):
        if not self._connected:
            return None
        return self._checkButton(2, 0x04)

    def buttonLeftPressed(self):
        if not self._connected:
            return None
        return self._checkButton(2, 0x01)

    def buttonRightPressed(self):
        if not self._connected:
            return None
        return self._checkButton(2, 0x02)

    def buttonPlusPressed(self):
        if not self._connected:
            return None
        return self._checkButton(2, 0x10)

    def buttonMinusPressed(self):
        if not self._connected:
            return None
        return self._checkButton(3, 0x10)

    def buttonHomePressed(self):
        if not self._connected:
            return None
        return self._checkButton(3, 0x80)

    def buttonOnePressed(self):
        if not self._connected:
            return None
        return self._checkButton(3, 0x02)

    def buttonTwoPressed(self):
        if not self._connected:
            return None
        return self._checkButton(3, 0x01)

    # 0x80 means no movement
    def getAcceleration(self):
        if not self._connected:
            return None

        d = self._getData()
        if len(d) != 19:
            return None

        ax = d[4] << 2 | d[2] & (0x20 | 0x40)
        ay = d[5] << 1 | d[3] & 0x20
        az = d[6] << 1 | d[3] & 0x40
        return (ax, ay, az)

    def getIRPoints(self):
        if not self._connected:
            return None

        d = self._getData()
        if len(d) != 19:
            return None

        x1 = d[7] | ((d[9] & (0b00110000)) << 4)
        y1 = d[8] | ((d[9] & (0b11000000)) << 2)
        i1 = d[9] & 0b00001111

        x2 = d[10] | ((d[12] & (0b00110000)) << 4)
        y2 = d[11] | ((d[12] & (0b11000000)) << 2)
        i2 = d[12] & 0b00001111

        x3 = d[13] | ((d[15] & (0b00110000)) << 4)
        y3 = d[14] | ((d[15] & (0b11000000)) << 2)
        i3 = d[15] & 0b00001111

        x4 = d[16] | ((d[18] & (0b00110000)) << 4)
        y4 = d[17] | ((d[18] & (0b11000000)) << 2)
        i4 = d[18] & 0b00001111

        return [(x1, y2, i1), (x2, y2, i2), (x3, y3, i3), (x4, y4, i4)]
