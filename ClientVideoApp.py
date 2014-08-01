from Tkinter import *
import cv2
import numpy
from PIL import Image, ImageTk
import socket
import string
import time

class ClientVideoApp:

    global socket_is_ready
    global main_Video
    global thresh_Video
    global client_socket
    global manual_command_socket
    global tresh_bar_socket
    global manual_mode
    global TCP_IP
    global TCP_PORT
    global minH
    global minS
    global minV
    global maxH
    global maxS
    global maxV

    def updateVideoFrame(self,master):
        master.after(0,self.update_frame(master,self.main_Video,self.thresh_Video))

    def update_frame(self,master,mainVideo,threshVideo):
        data1 = None
        data2 = None
        
        if self.socket_is_ready:
            #receiving video data by server
            #videoData = self.client_socket.recv(4096000)
            
            length = self.recvall(self.client_socket,16)
            stringData = self.recvall( self.client_socket, int(length))
            data_list = stringData.split("separatore")
            data1 = numpy.fromstring(data_list[0], dtype='uint8')
            data2 = numpy.fromstring(data_list[1], dtype='uint8')

            
            image1 = cv2.imdecode(data1, 1)
            image2 = cv2.imdecode(data2, 1)
            image1 = cv2.cvtColor(image1,cv2.COLOR_BGR2RGB)
            
            #changing color space because PIL use RGB representation
            a1 = Image.fromarray(numpy.uint8(image1))
            a2 = Image.fromarray(numpy.uint8(image2))
            b1 = ImageTk.PhotoImage(image=a1)
            b2 = ImageTk.PhotoImage(image=a2)
            mainVideo.configure(image=b1)
            threshVideo.configure(image=b2)
            master.update()

            self.client_socket.send("tresh;"+str(self.minH)+";"+str(self.minS)+";"+str(self.minV)+";"+str(self.maxH)+";"+str(self.maxS)+";"+str(self.maxV))

            #self.client_socket.send("continue")
            
        master.after(0,func=lambda:self.update_frame(master,self.main_Video,self.thresh_Video))

    #define method for change manual/automatic motion
    def set_manual_mode(self):
        if self.manual_mode:
            self.manual_mode = False
            print "Manual mode: OFF" 
            offPhoto = ImageTk.PhotoImage(file="Off.png")
            self.enableManualButton.config(image=offPhoto)
            self.enableManualButton.image = offPhoto #needed for save image from garbage collection
        else:
            self.manual_mode = True
            print "Manual mode: ON" 
            onPhoto = ImageTk.PhotoImage(file="On.png")
            self.enableManualButton.config(image=onPhoto)
            self.enableManualButton.image = onPhoto #needed for save image from garbage collection

    def turn_right(self):
        self.client_socket.send("comando;R;30")

    def turn_left(self):
        self.client_socket.send("comando;L;30")

    def forward(self):
        self.client_socket.send("comando;F;30")

    def fastForward(self):
        self.client_socket.send("comando;F;60")
        
    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def __init__(self,master):
        TCP_IP = '192.168.7.7'
        TCP_PORT = 32230
    
        #initialize socket
        try:
            self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.client_socket.connect((TCP_IP, TCP_PORT))
            self.socket_is_ready = True
        except:
            self.socket_is_ready = False

        #creating main frame
        frame = Frame(master,height=650,width=1300,bg="black")
        frame.pack()

        #define space for main video
        self.main_Video = Label(master,relief=RAISED,bg="black",fg="white")
        self.main_Video.pack()
        self.main_Video.place(x=5,y=5,height=480,width=640)

        #define space for thresholded video
        self.thresh_Video = Label(master,relief=RAISED,bg="black",fg="white")
        self.thresh_Video.pack()
        self.thresh_Video.place(x=655,y=5,height=480,width=640)

        #label for manual mode text
        manualModeInfoLabel = Label(master,text="Manual Mode",relief=RAISED,bg="black",fg="white")
        manualModeInfoLabel.pack()
        manualModeInfoLabel.place(x=5,y=495,height=30,width=640)

        #label for slider
        thresholdsInfoLabel = Label(master,text="HSV Thresholds",relief=RAISED,bg="black",fg="white")
        thresholdsInfoLabel.pack()
        thresholdsInfoLabel.place(x=655,y=495,height=30,width=640)

        #define min and max HSV values
        self.minH = IntVar()
        self.minS = IntVar()
        self.minV = IntVar()
        self.maxH = IntVar()
        self.maxS = IntVar()
        self.maxV = IntVar()

        #minH slider
        minHInfo = Label(master,text="Min H",relief=RAISED,bg="black",fg="white")
        minHInfo.pack()
        minHInfo.place(x=655,y=525,height=40,width=40)
        minHSlider = Scale(master,bd=1,from_=0,to=256,bg="black",fg="white",variable=self.minH,orient=HORIZONTAL,troughcolor="black",relief=RAISED)
        minHSlider.pack()
        minHSlider.place(x=695,y=525,height=40,width=280)
        #minS slider
        minSInfo = Label(master,text="Min S",relief=RAISED,bg="black",fg="white")
        minSInfo.pack()
        minSInfo.place(x=655,y=565,height=40,width=40)
        minSSlider = Scale(master,bd=1,from_=0,to=256,bg="black",fg="white",variable=self.minS,orient=HORIZONTAL,troughcolor="black",relief=RAISED)
        minSSlider.pack()
        minSSlider.place(x=695,y=565,height=40,width=280)
        #minV slider
        minVInfo = Label(master,text="Min V",relief=RAISED,bg="black",fg="white")
        minVInfo.pack()
        minVInfo.place(x=655,y=605,height=40,width=40)
        minVSlider = Scale(master,bd=1,from_=0,to=256,bg="black",fg="white",variable=self.minV,orient=HORIZONTAL,troughcolor="black",relief=RAISED)
        minVSlider.pack()
        minVSlider.place(x=695,y=605,height=40,width=280)
        #max H slider
        maxHInfo = Label(master,text="Max H",relief=RAISED,bg="black",fg="white")
        maxHInfo.pack()
        maxHInfo.place(x=975,y=525,height=40,width=40)
        maxHSlider = Scale(master,bd=1,from_=0,to=256,bg="black",fg="white",variable=self.maxH,orient=HORIZONTAL,troughcolor="black",relief=RAISED)
        maxHSlider.pack()
        maxHSlider.place(x=1015,y=525,height=40,width=280)
        #max S slider
        maxSInfo = Label(master,text="Max S",relief=RAISED,bg="black",fg="white")
        maxSInfo.pack()
        maxSInfo.place(x=975,y=565,height=40,width=40)
        maxSSlider = Scale(master,bd=1,from_=0,to=256,bg="black",fg="white",variable=self.maxS,orient=HORIZONTAL,troughcolor="black",relief=RAISED)
        maxSSlider.pack()
        maxSSlider.place(x=1015,y=565,height=40,width=280)
        #max V slider
        maxVInfo = Label(master,text="Max V",relief=RAISED,bg="black",fg="white")
        maxVInfo.pack()
        maxVInfo.place(x=975,y=605,height=40,width=40)
        maxVSlider = Scale(master,bd=1,from_=0,to=256,bg="black",fg="white",variable=self.maxV,orient=HORIZONTAL,troughcolor="black",relief=RAISED)
        maxVSlider.pack()
        maxVSlider.place(x=1015,y=605,height=40,width=280)

        #button for enable manual mode
        offPhoto = ImageTk.PhotoImage(file="Off.png")
        self.manual_mode = False
        self.enableManualButton = Button(master,command=self.set_manual_mode,relief=RAISED,bg="black",image=offPhoto)
        self.enableManualButton.pack()
        self.enableManualButton.image = offPhoto #needed for save image from garbage collection
        self.enableManualButton.place(x=5,y=525,height=120,width=120)

        #buttons for manual mode command
        rightPhoto = ImageTk.PhotoImage(file="Right.png")
        rightButton = Button(master,command=self.turn_right,bg="black",relief=RAISED,image=rightPhoto)
        rightButton.pack()
        rightButton.image = rightPhoto
        rightButton.place(x=435,y=595,height=50,width=100)
        leftPhoto = ImageTk.PhotoImage(file="Left.png")
        leftButton = Button(master,command=self.turn_left,bg="black",relief=RAISED,image=leftPhoto)
        leftButton.pack()
        leftButton.image = leftPhoto
        leftButton.place(x=235,y=595,height=50,width=100)
        forwardPhoto = ImageTk.PhotoImage(file="Forward.png")
        forwardButton = Button(master,command=self.forward,bg="black",relief=RAISED,image=forwardPhoto)
        forwardButton.pack()
        forwardButton.image = forwardPhoto
        forwardButton.place(x=335,y=575,height=50,width=100)
        fastForwardPhoto = ImageTk.PhotoImage(file="FastForward.png")
        fastForwardButton = Button(master,command=self.fastForward,bg="black",relief=RAISED,image=fastForwardPhoto)
        fastForwardButton.pack()
        fastForwardButton.image = fastForwardPhoto
        fastForwardButton.place(x=335,y=525,height=50,width=100)
        

root = Tk()
client=ClientVideoApp(root)
root.resizable(width=FALSE,height=FALSE)
root.title("Client Video App")
client.updateVideoFrame(root)
root.mainloop()
if client.socket_is_ready:
    client.client_socket.send("end;rocco")
try:
    root.destroy()
except:
    pass
