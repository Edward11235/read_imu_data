# coding:UTF-8
# Version: V1.0.1
import serial

ACCData = [0.0]*8
GYROData = [0.0]*8
angleData = [0.0]*8
LocationData = [0.0]*8
FrameState = 0  # What is the state of the judgment
Bytenum = 0  # Read the number of digits in this paragraph
CheckSum = 0  # Sum check bit

acc = [0.0]*3
gyro = [0.0]*3
angle = [0.0]*3
location = [0.0]*2


def DueData(inputdata):  # New core procedures, read the data partition, each read to the corresponding array 
    global FrameState    # Declare global variables
    global Bytenum
    global CheckSum
    global acc
    global gyro
    global angle
    for data in inputdata:  # Traversal the input data
        if FrameState == 0:  # When the state is not determined, enter the following judgment
            if data == 0x55 and Bytenum == 0:  # When 0x55 is the first digit, start reading data and increment bytenum
                CheckSum = data
                Bytenum = 1
                continue
            elif data == 0x51 and Bytenum == 1:  # Change the frame if byte is not 0 and 0x51 is identified
                CheckSum += data
                FrameState = 1
                Bytenum = 2
            elif data == 0x52 and Bytenum == 1:
                CheckSum += data
                FrameState = 2
                Bytenum = 2
            elif data == 0x53 and Bytenum == 1:
                CheckSum += data
                FrameState = 3
                Bytenum = 2
            elif data == 0x57 and Bytenum == 1:
                CheckSum += data
                FrameState = 4
                Bytenum = 2
        elif FrameState == 1:  # acc
            if Bytenum < 10:            # Read 8 data
                ACCData[Bytenum-2] = data  # Starting from 0
                CheckSum += data
                Bytenum += 1
            else:
                if data == (CheckSum & 0xff):  # verify check bit
                    acc = get_acc(ACCData)
                CheckSum = 0  # Each data is zeroed and a new circular judgment is made
                Bytenum = 0
                FrameState = 0
        elif FrameState == 2:  # gyro
            if Bytenum < 10:
                GYROData[Bytenum-2] = data
                CheckSum += data
                Bytenum += 1
            else:
                if data == (CheckSum & 0xff):
                    gyro = get_gyro(GYROData)
                CheckSum = 0
                Bytenum = 0
                FrameState = 0
        elif FrameState == 3:  # angle
            if Bytenum < 10:
                angleData[Bytenum-2] = data
                CheckSum += data
                Bytenum += 1
            else:
                if data == (CheckSum & 0xff):
                    angle = get_angle(angleData)
                CheckSum = 0
                Bytenum = 0
                FrameState = 0
        elif FrameState == 4:  # longitude and atitude
            if Bytenum < 10:
                LocationData[Bytenum-2] = data
                CheckSum += data
                Bytenum += 1
            else:
                if data == (CheckSum & 0xff):
                    location = get_location(LocationData)
                    print(f"acceleration: {acc}\ngyro: {gyro}\nangle: {angle}\nlocation: {location}")
                CheckSum = 0
                Bytenum = 0
                FrameState = 0


def get_acc(datahex):
    axl = datahex[0]
    axh = datahex[1]
    ayl = datahex[2]
    ayh = datahex[3]
    azl = datahex[4]
    azh = datahex[5]
    k_acc = 16.0
    acc_x = (axh << 8 | axl) / 32768.0 * k_acc
    acc_y = (ayh << 8 | ayl) / 32768.0 * k_acc
    acc_z = (azh << 8 | azl) / 32768.0 * k_acc
    if acc_x >= k_acc:
        acc_x -= 2 * k_acc
    if acc_y >= k_acc:
        acc_y -= 2 * k_acc
    if acc_z >= k_acc:
        acc_z -= 2 * k_acc
    return acc_x, acc_y, acc_z


def get_gyro(datahex):
    wxl = datahex[0]
    wxh = datahex[1]
    wyl = datahex[2]
    wyh = datahex[3]
    wzl = datahex[4]
    wzh = datahex[5]
    k_gyro = 2000.0
    gyro_x = (wxh << 8 | wxl) / 32768.0 * k_gyro
    gyro_y = (wyh << 8 | wyl) / 32768.0 * k_gyro
    gyro_z = (wzh << 8 | wzl) / 32768.0 * k_gyro
    if gyro_x >= k_gyro:
        gyro_x -= 2 * k_gyro
    if gyro_y >= k_gyro:
        gyro_y -= 2 * k_gyro
    if gyro_z >= k_gyro:
        gyro_z -= 2 * k_gyro
    return gyro_x, gyro_y, gyro_z


def get_angle(datahex):
    rxl = datahex[0]
    rxh = datahex[1]
    ryl = datahex[2]
    ryh = datahex[3]
    rzl = datahex[4]
    rzh = datahex[5]
    k_angle = 180.0
    angle_x = (rxh << 8 | rxl) / 32768.0 * k_angle
    angle_y = (ryh << 8 | ryl) / 32768.0 * k_angle
    angle_z = (rzh << 8 | rzl) / 32768.0 * k_angle
    if angle_x >= k_angle:
        angle_x -= 2 * k_angle
    if angle_y >= k_angle:
        angle_y -= 2 * k_angle
    if angle_z >= k_angle:
        angle_z -= 2 * k_angle
    return angle_x, angle_y, angle_z

def get_location(datahex):
    longitude_reading = int.from_bytes(datahex[0:4], byteorder='little', signed=True)
    latitude_reading = int.from_bytes(datahex[4:8], byteorder='little', signed=True)
    western_global = longitude_reading < 0
    if western_global:  # convert long to positive to do operations
        longitude_reading *= -1
    longitude_degree = longitude_reading // 10000000
    latitude_degree = latitude_reading // 10000000
    longitude_minite = (longitude_reading % 10000000.0) / 100000.0
    latitude_minite = (latitude_reading % 10000000.0) / 100000.0
    longitude = longitude_degree + longitude_minite / 60.0
    latitude = latitude_degree + latitude_minite / 60.0
    if western_global:  # convert long to positive to do operations
        longitude *= -1
    return longitude, latitude

if __name__ == '__main__':
    port = '/dev/ttyUSB0' # USB serial port 
    baud = 9600   # Same baud rate as the INERTIAL navigation module
    ser = serial.Serial(port, baud, timeout=0.5)
    print("Serial is Opened:", ser.is_open)
    while(1):
        datahex = ser.read(33)
        DueData(datahex)