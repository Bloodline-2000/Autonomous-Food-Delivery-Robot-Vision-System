import numpy
import serial
import numpy as np
from heapq import nsmallest

def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')

def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result

def lds_poll(ser):
    got_scan = False
    raw_bytes = [0] * 2520
    res = [-1] * 360
    # print(raw_bytes)
    start_count, good_sets, motor_speed = 0, 0, 0
    while (got_scan==False):
        raw_bytes[start_count] = bytes_to_int(ser.read(1))
        # print(ser.read(1))
        # if (raw_bytes[start_count] == b'\xfa'):
        #     print("nms")
        if (start_count == 0):
            if (raw_bytes[start_count] == bytes_to_int(b'\xfa')):
                start_count = 1
                #print("gdl")
        elif (start_count == 1):
            if (raw_bytes[start_count] == bytes_to_int(b'\xa0')):
                #print("gdl2")
                start_count = 0
                got_scan = True
                data = ser.read(2518)
                for i in range(2518):
                    raw_bytes[2+i] = data[i]

                for i in range(0,2520,42):
                    if (int_to_bytes(raw_bytes[i]) == b'\xfa' and raw_bytes[i+1] == bytes_to_int(b'\xa0') + (int(i / 42))):
                    
                        good_sets+=1
                        motor_speed += (raw_bytes[i+3]<<8) + raw_bytes[i+2]
                        s= (raw_bytes[i+3] << 8 | raw_bytes[i+2]) / 10
                        
                        for j in range(i+4, i+40, 6):
                            index = 6*(i/42) + (j-4-i)/6
                            byte0, byte1, byte2, byte3 = raw_bytes[j], raw_bytes[j+1], raw_bytes[j+2], raw_bytes[j+3]

                            intensity = (byte1 << 8) + byte0
                            rge = (byte3 << 8) + byte2
                            #res[359-int(index)] = rge / 1000.0
                            res[int(index)] = rge / 1000.0
                            #print('r[%d]=%f' %(int(index),rge / 1000.0))
                            #print(res[100])

            else:
                start_count = 0
  
        #print(res)             
    return res 

def lds_driver_init():
    # Setting up baud rate and io service
    port = '/dev/ttyUSB0'
    baud_rate = 230400
    ser = serial.Serial(port, baud_rate)
    return ser

def lds_driver_test():
    # Setting up baud rate and io service
    port = '/dev/ttyUSB0'
    baud_rate = 230400
    ser = serial.Serial(port, baud_rate)

    while (1):
        rge = lds_poll(ser)
        sectors = [rge[315:] + rge[:45],  # front
                   rge[45:135],  # left
                   rge[135:225],  # back
                   rge[225:315]]  # right
        res = [0,0,0,0]
        for id_sec in range(4):
            sec = sectors[id_sec]
            sec =numpy.array(sec)
            sec = sec[sec>0]
            if len(sec>2):
                mins = nsmallest(2, sec)
                score = 0.5 * (mins[0] + mins[1]) if mins[0] < 0.3 else mins[0]
                res[id_sec] = score
        print(res)

        # rge = rge[rge > 0]
        # if len(rge>2):
        #     mins = nsmallest(2, rge)
        #     score = 0.5*(mins[0]+mins[1]) if mins[0]<0.3 else mins[0]
        #     # if score<0.4:
        #     print(score)


if __name__ == '__main__':
    lds_driver_test()