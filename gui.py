from PyQt5 import QtCore, QtGui, QtWidgets
from os import path, remove
import helpers


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        ###############
        # Settings
        self.repository_path = '' # For fast implementation; this must be removed from there
        self.repo_clone_observer_path = '' # IN DEVELOPMENT
        self.repo_clone_test_runner_path = '' # IN DEVELOPMENT
        self.test_results_path = '' # IN DEVELOPMENT
        self.test_every_commit = True # Determines whether we will test every commit or check repo periodically
        self.n_test_runners = 1
        self.started = False # For fast implementation; this must be removed from there
        ###############

        MainWindow.setObjectName("MainWindow")
        MainWindow.setMinimumSize(760, 220)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(80, 10, 600, 180))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")

        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")

        self.okButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.okButton.setObjectName("okButton")
        self.okButton.clicked.connect(self.ok_button_callback)
        self.gridLayout_4.addWidget(self.okButton, 1, 1, 1, 1)

        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout_4.addWidget(self.label_2, 5, 0, 1, 1)

        self.observer_radio_button = QtWidgets.QRadioButton(self.gridLayoutWidget)
        self.observer_radio_button.setObjectName("observer_radio_button")
        self.gridLayout_4.addWidget(self.observer_radio_button, 3, 0, 1, 2)

        self.textBrowser = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout_4.addWidget(self.textBrowser, 0, 0, 1, 2)

        self.spinBox = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.spinBox.setObjectName("spinBox")
        self.spinBox.setMinimum(1)
        self.spinBox.setValue(1)
        self.spinBox.setMaximum(100)
        self.gridLayout_4.addWidget(self.spinBox, 5, 1, 1, 1)

        self.every_commit_radio_button = QtWidgets.QRadioButton(self.gridLayoutWidget)
        self.every_commit_radio_button.setObjectName("every_commit_radio_button")
        self.every_commit_radio_button.setChecked(True)
        self.gridLayout_4.addWidget(self.every_commit_radio_button, 2, 0, 1, 2)

        self.lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout_4.addWidget(self.lineEdit, 1, 0, 1, 1)

        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")

        self.startButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.startButton.setObjectName("startButton")
        self.startButton.clicked.connect(self.start_button_callback)
        self.gridLayout_3.addWidget(self.startButton, 0, 0, 1, 1)

        self.stopButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.stopButton.setObjectName("stopButton")
        self.stopButton.clicked.connect(self.stop_button_callback)
        self.gridLayout_3.addWidget(self.stopButton, 0, 1, 1, 1)

        self.gridLayout_4.addLayout(self.gridLayout_3, 6, 0, 1, 2)

        self.horizontalLayout.addLayout(self.gridLayout_4)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 720, 26))
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

        self.okButton.setText(_translate("MainWindow", "OK"))
        self.label_2.setText(_translate("MainWindow", " Количество тестирующих модулей"))
        self.observer_radio_button.setText(_translate("MainWindow", "Тестировать периодически"))
        self.every_commit_radio_button.setText(_translate("MainWindow", "Тестировать каждый коммит"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "Полный путь к репозиторию"))
        self.startButton.setText(_translate("MainWindow", "Запустить систему"))
        self.stopButton.setText(_translate("MainWindow", "Остановить систему"))

    def start_button_callback(self):
        '''
        Check if system already started:
        if not start every module in new cmd, get their pid and save it
        if yes print message
        '''

        if self.repository_path != '':
            try:
                response = helpers.communicate('localhost', 8888, 'status')
                if response == 'OK':
                    self.textBrowser.setText('Кажется систему уже запущена...')
            except:
                try:
                    if self.repository_path[-1] not in ['/', '\\']:
                        if '\\' in self.repository_path:
                            self.repository_path += '\\'
                        else:
                            self.repository_path += '/'

                    self.n_test_runners = self.spinBox.value()
                    self.test_every_commit = self.every_commit_radio_button.isChecked()

                    helpers.start_system(self.repository_path, self.test_every_commit, self.n_test_runners)
                    self.started = True
                    self.textBrowser.setText('Система запущена')
                except Exception as e:
                    print(e)
                    self.textBrowser.setText('Что-то пошло не так...')
        else:
            self.textBrowser.setText('Укажите путь к репозиторию')

    def stop_button_callback(self):
        '''
        close every module by pid
        '''
        if path.isfile('ids.txt'):
            remove('ids.txt')
        if self.started==True and helpers.module_process_ids:
            helpers.kill_all()
            self.started=False

    def ok_button_callback(self):
        self.repository_path = self.lineEdit.text()
        if self.repository_path != '':
            self.textBrowser.setText('Текущий путь к репозиторию: ' + self.repository_path)
        else:
            self.textBrowser.setText('Укажите путь к репозиторию:')


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
