# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\pp\pyt1.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication , QMainWindow
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import usb.core
import usb.util
import struct
import sys
import time

class ISP_USB:
      AP_FILE=[]
      AP_CHECKSUM=0
      PacketNumber=0
      dev=None
      ep_in=None
      name=""
      def __init__(self):
            #self.name=name
            #print(name)
            self.PacketNumber=0;
            self.dev = usb.core.find(idVendor=0x0416, idProduct=0x3F00)
            # was it found?
            if self.dev is None:
                raise ValueError('USB Device not found')
            self.dev.set_configuration()
            usb.util.claim_interface(self.dev, 0)
            self.dev.reset()
            cfg=self.dev[0]
            intf=cfg[(0,0)]
            self.ep_in= usb.util.find_descriptor(intf,# match the first OUT endpoint
                                                    custom_match = \
                                                    lambda e: \
                                                    usb.util.endpoint_direction(e.bEndpointAddress) == \
                                                    usb.util.ENDPOINT_IN)
            ep_out = usb.util.find_descriptor(intf,# match the first OUT endpoint
                                                custom_match = \
                                                lambda e: \
                                                usb.util.endpoint_direction(e.bEndpointAddress) == \
                                                usb.util.ENDPOINT_OUT)
      def USB_TRANSFER(self, thelist, PN):
            thelist[4]=PN&0xff
            thelist[5]=PN>>8&0xff
            thelist[6]=PN>>16&0xff
            thelist[7]=PN>>24&0xff
            

            test=self.dev.write(0x02,thelist)            
            return_str=self.ep_in.read(0x81,64) #return by string
            return_buffer=bytearray(return_str)
 #print 'rx package'
 #print '[{}]'.format(', '.join(hex(x) for x in return_buffer))

            checksum=0
            for i in range(64):
                checksum=checksum+thelist[i]
 #print "checksum=0x%x"%checksum
            packege_checksum=0
            packege_checksum=return_buffer[0]
            packege_checksum=(return_buffer[1]<<8)|packege_checksum
            if checksum!=packege_checksum:
                #print("checksum error")
                error_return()
            RPN=0
            RPN=return_buffer[4]
            RPN=(return_buffer[5]<<8)|RPN
            RPN=(return_buffer[6]<<16)|RPN
            RPN=(return_buffer[7]<<24)|RPN
            if RPN!=(PN+1):
                #print("package number error")
                error_return()
            return return_buffer

      def LINK_FUN(self):            
            LINK = [0 for i in range(64)] # 64 byte data buffer is all zero
            self.PacketNumber=0x01
            LINK[0]=0xae
            self.USB_TRANSFER(LINK,self.PacketNumber)

      def SN_FUN(self):
            self.PacketNumber =self.PacketNumber+2
            SN_PACKAGE = [0 for i in range(64)] 
            SN_PACKAGE[0]=0xa4
            SN_PACKAGE[8]=self.PacketNumber&0xff
            SN_PACKAGE[9]=self.PacketNumber>>8&0xff
            SN_PACKAGE[10]=self.PacketNumber>>16&0xff
            SN_PACKAGE[11]=self.PacketNumber>>24&0xff
            self.USB_TRANSFER(SN_PACKAGE,self.PacketNumber)

      def READ_fW_FUN(self):            
            self.PacketNumber=self.PacketNumber+2
            READFW_VERSION = [0 for i in range(64)] 
            READFW_VERSION[0]=0xa6
            buf=self.USB_TRANSFER(READFW_VERSION,self.PacketNumber)
            FW_VERSION=buf[8]
            #print("FW_VERSION=0x%8x" % FW_VERSION)

      def RUN_TO_APROM_FUN(self):            
            self.PacketNumber=self.PacketNumber+2
            RUN_TO_APROM = [0 for i in range(64)] 
            RUN_TO_APROM[0]=0xab
            self.USB_TRANSFER(RUN_TO_APROM,self.PacketNumber)
    
      def READ_PID_FUN(self):
            self.PacketNumber=self.PacketNumber+2
            READ_PID = [0 for i in range(64)] 
            READ_PID[0]=0xB1
            buf=self.USB_TRANSFER(READ_PID,self.PacketNumber)
            PID=buf[8]|buf[9]<<8|buf[10]<<16|buf[11]<<24
            #print("PID=0x%8x" % PID)

      def READ_CONFIG_FUN(self):
            self.PacketNumber=self.PacketNumber+2
            READ_CONFIG = [0 for i in range(64)] 
            READ_CONFIG[0]=0xa2
            buf=self.USB_TRANSFER(READ_CONFIG,self.PacketNumber)
            CONFIG0=buf[8]|buf[9]<<8|buf[10]<<16|buf[11]<<24
            CONFIG1=buf[12]|buf[13]<<8|buf[14]<<16|buf[15]<<24
            #print("CONFIG0=0x%8x" % CONFIG0)
            #print("CONFIG1=0x%8x" % CONFIG1)

      def READ_APROM_BIN_FILE(self, FILENAME):
            f=open(FILENAME, 'rb')            
            self.AP_CHECKSUM=0
            while True:
                x=f.read(1)
                if not x:
                    break
                temp=struct.unpack('B',x) 
                self.AP_FILE.append(temp[0])
                self.AP_CHECKSUM=self.AP_CHECKSUM+temp[0]
            f.close() 
            #print(len(self.AP_FILE)) 
            #print(self.AP_CHECKSUM) 

      def USB_TRANSFER_ERASE(self, thelist, PN):
            thelist[4]=PN&0xff
            thelist[5]=PN>>8&0xff
            thelist[6]=PN>>16&0xff
            thelist[7]=PN>>24&0xff
            test=self.dev.write(0x02,thelist)
            time.sleep(5)
            return_str=self.ep_in.read(0x81,64) #return by string
            return_buffer=bytearray(return_str)
 #print 'rx package'
 #print '[{}]'.format(', '.join(hex(x) for x in return_buffer))

            checksum=0
            for i in range(64):
                checksum=checksum+thelist[i]
 #print "checksum=0x%x"%checksum
            packege_checksum=0
            packege_checksum=return_buffer[0]
            packege_checksum=(return_buffer[1]<<8)|packege_checksum
            if checksum!=packege_checksum:
                #print("checksum error")
                error_return()
            RPN=0
            RPN=return_buffer[4]
            RPN=(return_buffer[5]<<8)|RPN
            RPN=(return_buffer[6]<<16)|RPN
            RPN=(return_buffer[7]<<24)|RPN
            if RPN!=(PN+1):
                #print("package number error")
                error_return()
            return return_buffer

      def UPDATE_APROM(self):
            self.PacketNumber=self.PacketNumber+2
            AP_ADRESS=0;
            AP_SIZE=len(self.AP_FILE)
            PAP_COMMNAD = [0 for i in range(64)] 
            PAP_COMMNAD[0]=0xa0
            #APROM START ADDRESS 
            PAP_COMMNAD[8]=AP_ADRESS&0xff
            PAP_COMMNAD[9]=AP_ADRESS>>8&0xff
            PAP_COMMNAD[10]=AP_ADRESS>>16&0xff
            PAP_COMMNAD[11]=AP_ADRESS>>24&0xff
            #APROM SIZE
            PAP_COMMNAD[12]=AP_SIZE&0xff  
            PAP_COMMNAD[13]=AP_SIZE>>8&0xff
            PAP_COMMNAD[14]=AP_SIZE>>16&0xff
            PAP_COMMNAD[15]=AP_SIZE>>24&0xff
            PAP_COMMNAD[16:64]=self.AP_FILE[0:48] #first package to copy
            #print '[{}]'.format(', '.join(hex(x) for x in PAP_COMMNAD)) 
            self.USB_TRANSFER_ERASE(PAP_COMMNAD,self.PacketNumber)

            for i in range(48,AP_SIZE,56):
                #print(i)
                self.PacketNumber=self.PacketNumber+2
                PAP1_COMMNAD = [0 for j in range(64)] 
                PAP1_COMMNAD[8:64]=self.AP_FILE[i:(i+56)]
                #print "test len: %d" % len(PAP1_COMMNAD)
                if len(PAP1_COMMNAD) < 64:
                    for k in range(64-len(PAP1_COMMNAD)):
                        PAP1_COMMNAD.append(0xFF)          
                        #print '[{}]'.format(', '.join(hex(x) for x in PAP1_COMMNAD)) 
                if (((AP_SIZE-i)<56) or ((AP_SIZE-i)==56)):
                    #print "end"    
                    buf=self.USB_TRANSFER(PAP1_COMMNAD,self.PacketNumber)
                    d_checksum=buf[8]|buf[9]<<8
                    if(d_checksum==(self.AP_CHECKSUM&0xffff)):
                        error_return()
                        #print("checksum pass")
                else:
                        #print "loop"     
                    self.USB_TRANSFER(PAP1_COMMNAD,self.PacketNumber)

class Ui_Form(object):
    
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 200)
        Form.setFixedSize(400, 200);  
        Form.setStyleSheet("")
        self.progressBar = QtWidgets.QProgressBar(Form)
        self.progressBar.setGeometry(QtCore.QRect(90, 60, 271, 23))
        self.progressBar.setMinimumSize(QtCore.QSize(0, 0))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.pushButton_1 = QtWidgets.QPushButton(Form)
        self.pushButton_1.setGeometry(QtCore.QRect(90, 140, 75, 23))
        self.pushButton_1.setMinimumSize(QtCore.QSize(0, 0))
        self.pushButton_1.setObjectName("pushButton_1")
        self.pushButton_1.clicked.connect(self.getFilename)
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(240, 140, 75, 23))
        self.pushButton_2.setMinimumSize(QtCore.QSize(0, 0))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.startISP)
        self.pushButton_2.setEnabled(False)
        self.textEdit = QtWidgets.QTextEdit(Form)
        self.textEdit.setEnabled(False)
        self.textEdit.setGeometry(QtCore.QRect(90, 90, 231, 31))
        self.textEdit.setMinimumSize(QtCore.QSize(0, 0))
        self.textEdit.setObjectName("textEdit")       
        self.thread = Worker()
        self.thread.sinOut.connect(self.slotAdd)
        
        #goable variable
        self.findname=""
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Nuvoton ISP"))
        self.pushButton_1.setText(_translate("Form", "Load Bin File"))
        self.pushButton_2.setText(_translate("Form", "Start ISP"))

    def getFilename(self):
        fname, _  = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\',"Bin file (*.bin)")
        if (fname==""):
            return

        self.findname=fname
        self.textEdit.setText(fname)
        self.pushButton_2.setEnabled(True)
    def startISP(self):
        self.progressBar.setValue(0)
        self.pushButton_1.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.thread.setfilename(self.findname)
        self.thread.start()

    def slotAdd(self,count):
        if(int(count)<=100):
             self.progressBar.setValue(int(count))
        if(int(count)==100): 
           self.pushButton_1.setEnabled(True)
           self.pushButton_2.setEnabled(True)

class Worker(QThread):
	sinOut = pyqtSignal(str)

	def __init__(self,parent=None):
		super(Worker,self).__init__(parent)
		self.working = True
		self.num = 0
		self.ISP = ISP_USB()
		self.filename=""

	def __del__(self):
		self.working = False
		self.wait()

	def setfilename(self,msg):
		self.filename=msg

	def Thread_UPDATE_APROM(self):
            self.ISP.PacketNumber=self.ISP.PacketNumber+2
            AP_ADRESS=0;
            AP_SIZE=len(self.ISP.AP_FILE)
            PAP_COMMNAD = [0 for i in range(64)] 
            PAP_COMMNAD[0]=0xa0
            #APROM START ADDRESS 
            PAP_COMMNAD[8]=AP_ADRESS&0xff
            PAP_COMMNAD[9]=AP_ADRESS>>8&0xff
            PAP_COMMNAD[10]=AP_ADRESS>>16&0xff
            PAP_COMMNAD[11]=AP_ADRESS>>24&0xff
            #APROM SIZE
            PAP_COMMNAD[12]=AP_SIZE&0xff  
            PAP_COMMNAD[13]=AP_SIZE>>8&0xff
            PAP_COMMNAD[14]=AP_SIZE>>16&0xff
            PAP_COMMNAD[15]=AP_SIZE>>24&0xff
            PAP_COMMNAD[16:64]=self.ISP.AP_FILE[0:48] #first package to copy
            #print '[{}]'.format(', '.join(hex(x) for x in PAP_COMMNAD)) 
            self.ISP.USB_TRANSFER_ERASE(PAP_COMMNAD,self.ISP.PacketNumber)

            for i in range(48,AP_SIZE,56):
                #print(int(i/AP_SIZE*100))
                self.sinOut.emit(str(int(i/AP_SIZE*100)))
                #if(int(i/AP_SIZE)%10==0):
                #    print(int(i/AP_SIZE))
                #    self.sleep(0.5)
                self.ISP.PacketNumber=self.ISP.PacketNumber+2
                PAP1_COMMNAD = [0 for j in range(64)] 
                PAP1_COMMNAD[8:64]=self.ISP.AP_FILE[i:(i+56)]
                #print "test len: %d" % len(PAP1_COMMNAD)
                if len(PAP1_COMMNAD) < 64:
                    for k in range(64-len(PAP1_COMMNAD)):
                        PAP1_COMMNAD.append(0xFF)          
                        #print '[{}]'.format(', '.join(hex(x) for x in PAP1_COMMNAD)) 
                if (((AP_SIZE-i)<56) or ((AP_SIZE-i)==56)):
                    #print "end"    
                    buf=self.ISP.USB_TRANSFER(PAP1_COMMNAD,self.ISP.PacketNumber)
                    d_checksum=buf[8]|buf[9]<<8
                    if(d_checksum==(self.ISP.AP_CHECKSUM&0xffff)):
                        #print("checksum pass")
                        self.sinOut.emit("100")
                else:
                        #print "loop"     
                    self.ISP.USB_TRANSFER(PAP1_COMMNAD,self.ISP.PacketNumber)


	def run(self):
         self.ISP.LINK_FUN()
         self.ISP.SN_FUN()
         self.ISP.READ_fW_FUN()
         self.ISP.READ_PID_FUN()
         self.ISP.READ_CONFIG_FUN()
         self.ISP.READ_APROM_BIN_FILE(self.filename) 
         self.Thread_UPDATE_APROM()      
         #self.sinOut.emit("100")



class MyMainWindow(QMainWindow, Ui_Form):
    def __init__(self, parent=None):    
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)  #only keep close button 


if __name__=="__main__":  
    '''
    test=ISP_USB()
    test.LINK_FUN()    
    test.SN_FUN()
    test.READ_PID_FUN()
    test.READ_fW_FUN()
    test.READ_APROM_BIN_FILE("c:\\t1.bin")
    test.UPDATE_APROM()
    '''
    app = QApplication(sys.argv)  
    myWin = MyMainWindow()  
    myWin.show()  
    sys.exit(app.exec_())
