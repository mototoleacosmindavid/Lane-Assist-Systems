from PyQt5 import QtCore, QtGui, QtWidgets
import socket
import rsa_library
import pickle as cPickle
import os
import threading
import sys, time

HOST = 'localhost'
PORT = 12346

stop_thread = False

flag = 1
flag_low = 0

unlockCar = 0xfd02
server_created_flag = True

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        global server
        global server_created_flag
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(600,500)
        MainWindow.setWindowTitle('Server')
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
    
        self.centralwidget.setStyleSheet("background-color:white;")
        
        # Start server button
        self.server_start = QtWidgets.QPushButton(MainWindow)
        self.server_start .setText("Start server")
        self.server_start .setStyleSheet("font: bold; font-size: 15px;")
        self.server_start .setGeometry(QtCore.QRect(200, 170, 200, 41))
        self.server_start.clicked.connect(self.start_server)

        # Start server label
        self.server_label = QtWidgets.QLabel(self.centralwidget)
        self.server_label.setGeometry(QtCore.QRect(-20, 210, 600, 40))
        self.server_label.setStyleSheet("font:bold;font-size: 15px;qproperty-alignment: AlignCenter;")

        # Key button
        self.key = QtWidgets.QPushButton(self.centralwidget)
        self.key.setGeometry(QtCore.QRect(225,270,150,150))
        keyImage = QtGui.QIcon('./key.png')
        self.key.setIcon(keyImage)
        self.key.setIconSize(QtCore.QSize(80,80))
        self.key.clicked.connect(self.send_key_data)
        self.key.setEnabled(False)

        # Unlock
        self.unlock = QtWidgets.QLabel(self.centralwidget)
        self.unlock.setGeometry(QtCore.QRect(225,430,150,20))
        self.unlock.setText("Unlock the car!")
        self.unlock.setStyleSheet("font:bold;font-size: 15px;qproperty-alignment: AlignCenter;")

        # Dashboard image
        self.dashboard_label = QtWidgets.QLabel(self.centralwidget)
        self.dashboard_label.setGeometry(QtCore.QRect(120, 280,360,180))
        dashboard = QtGui.QImage(QtGui.QImageReader('./dashboard.png').read())
        self.dashboard_label.setPixmap(QtGui.QPixmap(dashboard))
        self.dashboard_label.setVisible(False)

        # Airgab image label
        self.airbag_label = QtWidgets.QLabel(self.centralwidget)
        self.airbag_label.setGeometry(QtCore.QRect(290,365,30,30))
        airbag_image = QtGui.QPixmap("./airbag.png")
        airbag_image = airbag_image.scaled(30,30, QtCore.Qt.KeepAspectRatio)
        self.airbag_label.setPixmap(QtGui.QPixmap(airbag_image))
        self.airbag_label.setVisible(False)

        # Ecu defect label
        self.ecu_defect_label = QtWidgets.QLabel(self.centralwidget)
        self.ecu_defect_label.setGeometry(QtCore.QRect(280,365,40,30))
        self.ecu_defect_label.setStyleSheet("font:bold;font-size:12px;color:red")
        self.ecu_defect_label.setVisible(False)
        
        # Continental image
        self.conti_label = QtWidgets.QLabel(self.centralwidget)
        self.conti_label.setGeometry(QtCore.QRect(110, 30, 400, 100))
        continental = QtGui.QImage(QtGui.QImageReader('./rsz_conti.png').read())
        self.conti_label.setPixmap(QtGui.QPixmap(continental))
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.show()

    
############################### EXERCISE 5 ###############################

    def start_server(self):
        self.key.setEnabled(True)
        self.airbag_label.setVisible(False)
        self.ecu_defect_label.clear()
        self.dashboard_label.setVisible(False)
        self.key.setVisible(True)
        self.unlock.setVisible(True)
        self.images()

        # Generează perechea de chei RSA
        self.public_key, self.private_key = rsa_library.generate_keypair(277, 239)

        # Configurează socket-ul serverului
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((HOST, PORT))
            self.server.listen(1)
            self.server_label.setText("Server is listening for connections...")

            # Acceptă o conexiune
            self.client_socket, addr = self.server.accept()
            self.server_label.setText(f"Connected to client at {addr}")
            
            self.recv_messages()
            
            # Trimite cheia publică și cheia privată clientului
            keys = (self.public_key, self.private_key)
            self.client_socket.send(cPickle.dumps(keys))
            
            # După trimiterea cheilor, pregătește-te pentru acțiuni viitoare sau închide socket-ul clientului
            self.client_socket.close()
            self.server_label.setText("Keys sent to client, connection closed.")
        except Exception as e:
            self.server_label.setText(f"Error: {str(e)}")
            if hasattr(self, 'server'):
                self.server.close()

############################### EXERCISE 6 ###############################   
    def send_key_data(self):
        try:
            # Criptează valoarea unlockCar folosind cheia publică
            encrypted_data = rsa_library.encrypt(self.public_key, hex(unlockCar))

            # Creează un nou socket pentru a trimite datele
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))

            # Trimite datele criptate către client
            self.client_socket.send(cPickle.dumps(encrypted_data))
            print("Encrypted data sent to client.")

            # Actualizează GUI-ul după trimiterea datelor
            self.dashboard_label.setVisible(True)
            self.unlock.setVisible(False)
            self.key.setVisible(False)

            # Închide socket-ul
            self.client_socket.close()
        except Exception as e:
            print(f"Failed to send encrypted data: {str(e)}")


############################### EXERCISE 7 ###############################   
    def recv_messages(self):
        self.stop_event = threading.Event()
        self.c_thread=threading.Thread(target=self.recv_messages_handler, args=(self.stop_event,))
        self.c_thread.start()

    def recv_messages_handler(self, stop_event):
        global server_created_flag
        global stop_thread
        try:
            while server_created_flag and not stop_event.isSet() and not stop_thread:
                 # Acceptă o conexiune
                client_socket, addr = self.server.accept()
                print(f"Connected to client at {addr}")

                 # Așteaptă un mesaj de la client
                data = client_socket.recv(1024)
            if data:
                try:
                    # Decriptează datele
                    decrypted_data = rsa_library.decrypt(self.private_key, cPickle.loads(data))
                    print(f"Decrypted data: {decrypted_data}")

                    # Extrage părțile LOW și HIGH
                    low_part = decrypted_data & 0xFF
                    high_part = (decrypted_data >> 8) & 0xFF

                    # Verifică validitatea
                    if low_part != 0x01 or high_part != (~low_part & 0xFF):
                        # Trimite un mesaj de eroare clientului
                        error_message = "Error: Invalid data received."
                        client_socket.send(cPickle.dumps(error_message))
                    else:
                       # Trimite un mesaj de succes clientului
                        success_message = "Data is valid."
                        client_socket.send(cPickle.dumps(success_message))
                except Exception as e:
                    error_message = f"Decryption or validation failed: {str(e)}"
                    client_socket.send(cPickle.dumps(error_message))

             # Închide socket-ul
            client_socket.close()
        except Exception as e:
            print(f"Error in receiving or processing data: {str(e)}")

##############################################################     
    def images(self):
        self.c_thread1=threading.Thread(name='images',target=self.images_handler)
        self.c_thread1.start()

    def images_handler(self):
        global flag
        global flag_low
        global stop_thread 

        while stop_thread == False:
            if flag_low == True and flag == True:
                self.ecu_defect_label.setVisible(False)
                self.airbag_label.setVisible(True)
            elif flag_low == True and flag == False:
                self.airbag_label.setVisible(False)
                self.ecu_defect_label.setVisible(True)
                self.ecu_defect_label.setText('  ECU\nDefect')
            elif flag_low == False and flag == False:
                self.airbag_label.setVisible(False)
                self.ecu_defect_label.setVisible(True)
                self.ecu_defect_label.setText('  ECU\nDefect')
            
class MyWindow(QtWidgets.QMainWindow):
    def closeEvent(self,event):
        global stop_thread
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)        

        if result == QtWidgets.QMessageBox.Yes:
            stop_thread = True
            event.accept()
        elif result == QtWidgets.QMessageBox.No:
            event.ignore()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

def kill_proc_tree(pid, including_parent=True):    
    parent = psutil.Process(pid)
    if including_parent:
        parent.kill()

def main():
    global server_created_flag
    import sys
    global app
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.center()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

me = os.getpid()
kill_proc_tree(me)
