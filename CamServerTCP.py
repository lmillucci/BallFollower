import socket, cv2, numpy

TCP_IP = ''
TCP_PORT = 32230

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((TCP_IP,TCP_PORT))
server_socket.listen(5)

capture = cv2.VideoCapture(0)
capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480)

client_socket = None

minH = 26
minS = 75
minV = 67
maxH = 256
maxS = 256
maxV = 256

while True:
    if (client_socket is None):
        client_socket, address = server_socket.accept()
        print "Open socket whit: " , address
    _,frame = capture.read()
    
    minColor = numpy.array((minH,minS,minV))
    maxColor = numpy.array((maxH,maxS,maxV))
    frame2 = cv2.inRange(frame,minColor,maxColor)

    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
    #encoding frame and frame2
    result, imgencoded = cv2.imencode('.jpg', frame, encode_param)
    result, imgencoded2 = cv2.imencode('.jpg', frame2, encode_param)
    #creating arrays
    data1 = numpy.array(imgencoded)
    data2 = numpy.array(imgencoded2)
    #creating one string
    stringData = data1.tostring() + "separatore" + data2.tostring()
    try:
        client_socket.send( str(len(stringData)).ljust(16));
        client_socket.send(stringData);
    except:
        pass
    try:
        ricevuto = client_socket.recv(1024)
        option = ricevuto.split(";")
        if option[0]=="end":
            print "Ho ricevuto l'end dal Client"
            client_socket.close()
            client_socket = None
        elif option[0]=="comando":
            if(option[1]=="F"):
                print "Forward at ",option[2]
            elif(option[1]=="L"):
                print "Left at ",option[2]
            elif(option[1]=="R"):
                print "Right at ",option[2]
        elif option[0]=="soglie":
            minH = int(option[1])
            minS = int(option[2])
            minV = int(option[3])
            maxH = int(option[4])
            maxS = int(option[5])
            maxV = int(option[6])
        else:
            #devo continuare
            pass
    except:
        client_socket.close()
        client_socket = None
    
cv2.VideoCapture(0).release()
server_socket.close()
