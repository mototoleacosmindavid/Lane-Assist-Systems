from PyQt5 import QtCore, QtGui, QtWidgets
import socket
import rsa_library
import pickle as cPickle
import os
import threading
import sys, time
import rsa_library


HOST = 'localhost'
PORT = 12346
stop_thread = False


airbag_on = 0xfe01
corrupted_low = 0x5732
corrupted_high = 0x5701
unlockCar = 0xfd02


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(600,500)
        MainWindow.setWindowTitle('Client')
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        MainWindow.setCentralWidget(self.centralwidget)

        self.centralwidget.setStyleSheet("background-color:white;")
        
        # Start client button
        self.client_start = QtWidgets.QPushButton(MainWindow)
        self.client_start.setText("Connect client")
        self.client_start.setStyleSheet("font: bold; font-size: 15px;")
        self.client_start.setGeometry(QtCore.QRect(200, 170, 200, 40))
        self.client_start.clicked.connect(self.start_client)

        self.client_label = QtWidgets.QLabel(self.centralwidget)
        self.client_label.setGeometry(QtCore.QRect(320, 170, 205, 41))
        self.client_label.setStyleSheet("font:bold;font-size: 15px;")

        # Connected label
        self.connected_label = QtWidgets.QLabel(self.centralwidget)
        self.connected_label.setGeometry(QtCore.QRect(200, 210,600 , 40))
        self.connected_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")
        
        # Client_status_label
        self.client_status_label = QtWidgets.QLabel(self.centralwidget)
        self.client_status_label.setGeometry(QtCore.QRect(-50, 200, 600 , 100))
        self.client_status_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")
        
        # Airbag on
        self.airbag = QtWidgets.QPushButton(MainWindow)
        self.airbag.setText("Airbag on")
        self.airbag.setStyleSheet("font: bold; font-size: 15px;")
        self.airbag.setGeometry(QtCore.QRect(70,260,211,41))
        self.airbag.clicked.connect(self.send_on_data)
        self.airbag.setEnabled(False)

        # Airbag on label
        self.airbag_on_label = QtWidgets.QLabel(self.centralwidget)
        self.airbag_on_label.setGeometry(QtCore.QRect(300, 260,200 , 40))
        self.airbag_on_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")

        # Corrupted low
        self.corrupted_low = QtWidgets.QPushButton(MainWindow)
        self.corrupted_low.setText("Corrupted low")
        self.corrupted_low.setStyleSheet("font: bold; font-size: 15px;")
        self.corrupted_low.setGeometry(QtCore.QRect(70,330,211,41))
        self.corrupted_low.clicked.connect(self.send_corrupted_low)
        self.corrupted_low.setEnabled(False)

        # Corrupted low label
        self.corrupted_low_label = QtWidgets.QLabel(self.centralwidget)
        self.corrupted_low_label.setGeometry(QtCore.QRect(300, 330,200 , 40))
        self.corrupted_low_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")
        
        # Corrupted high
        self.corrupted_high = QtWidgets.QPushButton(MainWindow)
        self.corrupted_high.setText("Corrupted high")
        self.corrupted_high.setStyleSheet("font: bold; font-size: 15px;")
        self.corrupted_high.setGeometry(QtCore.QRect(70,400,211,41))
        self.corrupted_high.clicked.connect(self.send_corrupted_high)
        self.corrupted_high.setEnabled(False)

        # Corrupted high label
        self.corrupted_high_label = QtWidgets.QLabel(self.centralwidget)
        self.corrupted_high_label.setGeometry(QtCore.QRect(300, 400,200 , 40))
        self.corrupted_high_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")
     
        # Continental image
        self.conti_label = QtWidgets.QLabel(self.centralwidget)
        self.conti_label.setGeometry(QtCore.QRect(110, 30, 400, 100))
        continental = QtGui.QImage(QtGui.QImageReader('./rsz_conti.png').read())
        self.conti_label.setPixmap(QtGui.QPixmap(continental))
    
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        
        MainWindow.setStatusBar(self.statusbar)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.show()


############################### EXERCISE 5 ###############################
    def start_client(self):
        self.corrupted_low_label.clear()
        self.airbag_on_label.clear()
        self.corrupted_high_label.clear()
        self.airbag.setEnabled(False)
        self.corrupted_high.setEnabled(False)
        self.corrupted_low.setEnabled(False)

        try:
            # Creează un socket client
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Conectează-te la server
            client.connect((HOST, PORT))
            self.client_status_label.setText("Connected to Server...")

            # Primește cheile serializate de la server
            received_data = client.recv(1024)  # Ajustează dimensiunea bufferului dacă este necesar
            public_key, private_key = cPickle.loads(received_data)
            
            # Stochează cheile pentru utilizare ulterioară
            self.public_key = public_key
            self.private_key = private_key
            self.client_status_label.setText("Keys received and stored.")

            # Activează elementele relevante ale GUI-ului bazate pe recepția cheilor cu succes
            self.airbag.setEnabled(True)
            self.corrupted_high.setEnabled(True)
            self.corrupted_low.setEnabled(True)

            # Închide conexiunea
            client.close()
        except Exception as e:
            self.client_status_label.setText(f"Failed to connect or retrieve keys: {str(e)}")
          
############################### EXERCISE 8 ###############################
    def recv_messages(self):
        self.stop_event = threading.Event()
        self.c_thread=threading.Thread(target=self.recv_handler, args=(self.stop_event,))
        self.c_thread.start()

        
    def recv_handler(self, stop_event):
        global stop_thread
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((HOST, PORT))
            while not stop_event.isSet() and not stop_thread:
                try:
                     # Primește date de la server
                    data = client.recv(1024)   # Ajustează dimensiunea bufferului dacă este necesar
                    if data:
                       # Deserializează și decriptează mesajul
                        message = cPickle.loads(data)
                        decrypted_message = rsa_library.decrypt(self.private_key, message)

                       # Verifică conținutul mesajului decriptat
                        if decrypted_message == hex(unlockCar):
                            # If the message is unlockCar variable
                            self.airbag.setEnabled(True)
                            self.corrupted_low.setEnabled(True)
                            self.corrupted_high.setEnabled(True)
                            self.airbag_on_label.setText("Car unlocked successfully!")
                        elif "Error" in decrypted_message:
                            # Dacă mesajul conține o eroare

                            self.corrupted_low_label.setText(decrypted_message)
                        else:
                             # Dacă mesajul indică că nu există erori
                            self.airbag_on_label.setText(decrypted_message)
                except Exception as e:
                    print(f"Failed to receive or process message: {str(e)}")
        except Exception as e:
            print(f"Connection failed: {str(e)}")
        finally:
            client.close()
############################### EXERCISE 9 ###############################              
    def send_on_data(self):
        try:
           # Criptează valoarea airbag_on folosind cheia publică
            encrypted_data = rsa_library.encrypt(self.public_key, hex(airbag_on))

            # Creează un socket client
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                #  Conectează-te la server
                client.connect((HOST, PORT))

                # Trimite datele criptate la server
                client.send(cPickle.dumps(encrypted_data))
                self.airbag_on_label.setText("Airbag status sent to the server.")

            finally:
                # Închide întotdeauna conexiunea
                client.close()

        except Exception as e:
            # Actualizează GUI-ul pentru a afișa eroarea
            self.airbag_on_label.setText(f"Failed to send airbag status: {str(e)}")

    ############################### EXERCISE 10 ###############################     
    def send_corrupted_low(self):
        try:
             # Criptează valoarea corrupted_low folosind cheia publică
            encrypted_data = rsa_library.encrypt(self.public_key, hex(corrupted_low))

            # Creează un socket client
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # Conectează-te la server
                client.connect((HOST, PORT))

                #Trimite datele criptate la server
                client.send(cPickle.dumps(encrypted_data))
                self.corrupted_low_label.setText("Corrupted low data sent to the server.")
            finally:
                 # Închide întotdeauna conexiunea
                client.close()

        except Exception as e:
             # Actualizează GUI-ul pentru a afișa eroarea
            self.corrupted_low_label.setText(f"Failed to send corrupted low data: {str(e)}")

     ############################### EXERCISE 11 ###############################      
    def send_corrupted_high(self):
        try:
           # Criptează valoarea corrupted_high folosind cheia publică
            encrypted_data = rsa_library.encrypt(self.public_key, hex(corrupted_high))

             # Creează un socket client
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # Conectează-te la server
                client.connect((HOST, PORT))

                # Trimite datele criptate la server
                client.send(cPickle.dumps(encrypted_data))
                self.corrupted_high_label.setText("Corrupted high data sent to the server.")
            finally:
                # Închide întotdeauna conexiunea
                client.close()

        except Exception as e:
            # Actualizează GUI-ul pentru a afișa eroarea
            self.corrupted_high_label.setText(f"Failed to send corrupted high data: {str(e)}")
        
def kill_proc_tree(pid, including_parent=True):    
    parent = psutil.Process(pid)
    if including_parent:
        parent.kill()
        
class MyWindow(QtWidgets.QMainWindow):
    def closeEvent(self,event):
        global stop_thread
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)        

        if result == QtWidgets.QMessageBox.Yes:
            event.accept()
            stop_thread = True
        elif result == QtWidgets.QMessageBox.No:
            event.ignore()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
    


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.center()
    sys.exit(app.exec_())
