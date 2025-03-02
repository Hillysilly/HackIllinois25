import numpy as np

def panAndTilt(panServo, tiltServo, faces, currentPan, currentTilt, haventSeen):
    #Range
    fudge = 0.5
    if(len(faces) == 0):
        if(haventSeen > 20):
            setDefault(panServo, tiltServo)
            return currentPan, currentTilt, (haventSeen + 1)
        return currentPan, currentTilt, (haventSeen + 1)
    
    goodPanMin = 200
    goodPanMax = 440
    goodTiltMin = 150
    goodTiltMax = 350
    
    lookingAt = np.array([320, 240])
    MaxArea = 0
    maxPt = np.array([0,0])
    for (x, y, w, h) in faces:
        area = w * h
        if(area > MaxArea):
            MaxArea = area
            maxPt = np.array([x+(w/2), y-(h/2)])
        break
    
    distVec = maxPt - lookingAt

    if((maxPt[0] > goodPanMin and maxPt[0] < goodPanMax)):
        return currentPan, currentTilt, 0
    else:
        if(distVec[0] < 0):
            currentPan = currentPan + 1
        elif(distVec[0] == 0):
            currentPan = currentPan
        elif(distVec[0] > 0 ):
            currentPan = currentPan - 1

    
    if( (maxPt[1] > goodTiltMin and maxPt[1] < goodTiltMax)):
        return currentPan, currentTilt, 0
    #else:
        #currentTilt = int(currentTilt + (dVec[1]))

    #print("max pt is (" + str(maxPt[0]) + "," + str(maxPt[1]) + ")")
    setPanTilt(currentPan, currentTilt, panServo, tiltServo)
    return currentPan, currentTilt, 0
    
def setDefault(pan_servo, tilt_servo):
    pan_servo.set_angle(90)
    tilt_servo.set_angle(0)
    return

def setPanTilt(pan, tilt, panServo, tiltServo): 
    maxTilt = 40
    minTilt =0
    maxPan = 270
    minPan = 0

    if(pan > maxPan or pan < minPan):
        setDefault(panServo, tiltServo)
    if(tilt > maxTilt or tilt < minPan):
        setDefault(panServo, tiltServo)
    panServo.set_angle(pan)
    tiltServo.set_angle(tilt)
    return
