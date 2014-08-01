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

while True:
    if (client_socket is None):
        client_socket, address = server_socket.accept()
        print "Open socket whit: " , address
    _,frame = capture.read()
    
    minColor = numpy.array((26,75,67))
    maxColor = numpy.array((256,256,256))
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
        try:
            direzione = ricevuto.split("velocita")
        except:
            direzione = None
            pass
        if ricevuto=="end":
            print "Ho ricevuto l'end dal Client"
            client_socket.close()
            client_socket = None
        elif(direzione[0]=="comando:F"):
            print "Forward at ",direzione[1]
        elif(direzione[0]=="comando:L"):
            print "Left at ",direzione[1]
        elif(direzione[0]=="comando:R"):
            print "Right at ",direzione[1]
        else:
            #devo continuare
    except:
        client_socket.close()
        client_socket = None
    
cv2.VideoCapture(0).release()
server_socket.close()
