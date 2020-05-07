from PyQt5 import QtCore, QtGui, QtWidgets
import main
import helpers


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.repo_path = '' # For fast implementation; this must be removed from there
        self.started = False # For fast implementation; this must be removed from there

        MainWindow.setObjectName("MainWindow")
        MainWindow.setMinimumSize(760,140)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(80, 10, 600, 100))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")

        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)

        self.okButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.okButton.setObjectName("okButton")
        self.okButton.clicked.connect(self.ok_button_callback)
        self.horizontalLayout.addWidget(self.okButton)

        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 2)

        self.startButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.startButton.setObjectName("startButton")
        self.startButton.clicked.connect(self.start_button_callback)
        self.gridLayout.addWidget(self.startButton, 2, 0, 1, 1)

        self.stopButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.stopButton.setObjectName("exitButton")
        self.stopButton.clicked.connect(self.stop_button_callback)
        self.gridLayout.addWidget(self.stopButton, 2, 1, 1, 1)

        self.textBrowser = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 0, 0, 1, 2)

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 731, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CI system"))
        MainWindow.setWindowIcon(QtGui.QIcon(_translate("MainWindow", "ci-icon.png")))
        self.startButton.setText(_translate("MainWindow", "START"))
        self.stopButton.setText(_translate("MainWindow", "STOP"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "Path to repository"))
        self.okButton.setText(_translate("MainWindow", "OK"))

    def start_button_callback(self):
        '''
        Check if system already started:
        if not start every module in new cmd, get their pid and save it
        if yes print message
        '''
        try:
            response = helpers.communicate('localhost', 8888, 'status')
            if response == 'OK':
                self.textBrowser.setText('It seems that CI system is working')
        except:
            if self.repo_path != '':
                try:
                    if self.repo_path[-1] not in ['/', '\\']:
                        self.repo_path += '/'
                    main.start_system(self.repo_path)
                    self.started = True
                except:
                    print('Cant start the system, check if repository path is correct...')
            else:
                print(self.repo_path)
                self.textBrowser.setText('Paste repository path')

    def stop_button_callback(self):
        '''
        close every module by pid
        '''
        if self.started==True and main.module_process_ids:
            main.kill_all()
            os.remove('ids.txt')
            self.started=False

    def ok_button_callback(self):
        self.repo_path = self.lineEdit.text()
        if self.repo_path != '':
            print(self.repo_path)
            self.textBrowser.setText('Current repository path: ' + self.repo_path)
        else:
            print(self.repo_path)
            self.textBrowser.setText('Paste repository path')


if __name__ == "__main__":
    import sys, os
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())