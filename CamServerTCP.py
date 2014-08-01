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
    '''print img
    print "Tipo img: ",type(img)
    print "Grandezza img",img.shape
    print "Tipo di dato img: ",img.dtype
    print "Numero di elementi: ",img.size'''
    minColor = numpy.array((26,75,67))
    maxColor = numpy.array((256,256,256))
    frame2 = cv2.inRange(frame,minColor,maxColor)
    '''print "Tipo img: ",type(img2)
    print "Grandezza img",img2.shape
    print "Tipo di dato img: ",img2.dtype
    print "Numero di elementi: ",img2.size'''
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
        if client_socket.recv(1024)=="end":
            print "Ho ricevuto l'end dal Client"
            client_socket.close()
            client_socket = None
        else:
            print "Ho ricevuto il continue dal Client"
    except:
        client_socket.close()
        client_socket = None
cv2.VideoCapture(0).release()
server_socket.close()
