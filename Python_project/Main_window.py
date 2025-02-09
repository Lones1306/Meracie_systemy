# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1159, 935)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setMaximumSize(QtCore.QSize(1008, 872))
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.frame_5 = QtWidgets.QFrame(self.centralwidget)
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tabWidget = QtWidgets.QTabWidget(self.frame_5)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setAutoFillBackground(False)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("tab_1")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_1)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.Graph_Stress = QtWidgets.QWidget(self.tab_1)
        self.Graph_Stress.setMinimumSize(QtCore.QSize(616, 610))
        self.Graph_Stress.setObjectName("Graph_Stress")
        self.gridLayout_3.addWidget(self.Graph_Stress, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_1, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.frame_6 = QtWidgets.QFrame(self.tab_2)
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame_6)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.Graph_Integration = QtWidgets.QWidget(self.frame_6)
        self.Graph_Integration.setMinimumSize(QtCore.QSize(596, 282))
        self.Graph_Integration.setObjectName("Graph_Integration")
        self.verticalLayout_4.addWidget(self.Graph_Integration)
        self.gridLayout_2.addWidget(self.frame_6, 0, 0, 1, 1)
        self.Graph_Force = QtWidgets.QWidget(self.tab_2)
        self.Graph_Force.setMinimumSize(QtCore.QSize(616, 302))
        self.Graph_Force.setObjectName("Graph_Force")
        self.gridLayout_2.addWidget(self.Graph_Force, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.horizontalLayout_2.addWidget(self.tabWidget)
        self.frame_4 = QtWidgets.QFrame(self.frame_5)
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_4)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame = QtWidgets.QFrame(self.frame_4)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_6 = QtWidgets.QLabel(self.frame)
        self.label_6.setObjectName("label_6")
        self.verticalLayout.addWidget(self.label_6)
        self.Priemer = QtWidgets.QDoubleSpinBox(self.frame)
        self.Priemer.setAcceptDrops(True)
        self.Priemer.setMaximum(10000.0)
        self.Priemer.setObjectName("Priemer")
        self.verticalLayout.addWidget(self.Priemer)
        self.label_5 = QtWidgets.QLabel(self.frame)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.Dlzka = QtWidgets.QDoubleSpinBox(self.frame)
        self.Dlzka.setAcceptDrops(True)
        self.Dlzka.setMaximum(100000000.0)
        self.Dlzka.setObjectName("Dlzka")
        self.verticalLayout.addWidget(self.Dlzka)
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.Youngov_modul = QtWidgets.QDoubleSpinBox(self.frame)
        self.Youngov_modul.setAcceptDrops(True)
        self.Youngov_modul.setMaximum(10000.0)
        self.Youngov_modul.setObjectName("Youngov_modul")
        self.verticalLayout.addWidget(self.Youngov_modul)
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.Re_mat = QtWidgets.QDoubleSpinBox(self.frame)
        self.Re_mat.setAcceptDrops(True)
        self.Re_mat.setMaximum(99999.99)
        self.Re_mat.setObjectName("Re_mat")
        self.verticalLayout.addWidget(self.Re_mat)
        self.label_8 = QtWidgets.QLabel(self.frame)
        self.label_8.setObjectName("label_8")
        self.verticalLayout.addWidget(self.label_8)
        self.Bezpecnost = QtWidgets.QDoubleSpinBox(self.frame)
        self.Bezpecnost.setAcceptDrops(True)
        self.Bezpecnost.setObjectName("Bezpecnost")
        self.verticalLayout.addWidget(self.Bezpecnost)
        self.verticalLayout_3.addWidget(self.frame)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.frame_2 = QtWidgets.QFrame(self.frame_4)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.inputs_pushButton = QtWidgets.QPushButton(self.frame_2)
        self.inputs_pushButton.setObjectName("inputs_pushButton")
        self.verticalLayout_2.addWidget(self.inputs_pushButton)
        self.verticalLayout_3.addWidget(self.frame_2)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.frame_3 = QtWidgets.QFrame(self.frame_4)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Start_button = QtWidgets.QPushButton(self.frame_3)
        self.Start_button.setObjectName("Start_button")
        self.horizontalLayout.addWidget(self.Start_button)
        self.Stop_button = QtWidgets.QPushButton(self.frame_3)
        self.Stop_button.setEnabled(False)
        self.Stop_button.setObjectName("Stop_button")
        self.horizontalLayout.addWidget(self.Stop_button)
        self.verticalLayout_3.addWidget(self.frame_3)
        self.horizontalLayout_2.addWidget(self.frame_4)
        self.gridLayout.addWidget(self.frame_5, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), _translate("MainWindow", "Tab 1"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))
        self.label_6.setText(_translate("MainWindow", "Priemer [mm]"))
        self.label_5.setText(_translate("MainWindow", "Dlzka [mm]"))
        self.label_4.setText(_translate("MainWindow", "Youngov modul [GPa]"))
        self.label_3.setText(_translate("MainWindow", "Medza pevnosti [MPa]"))
        self.label_8.setText(_translate("MainWindow", "Koeficient bezpecnosti"))
        self.inputs_pushButton.setText(_translate("MainWindow", "Vstupny signal"))
        self.Start_button.setText(_translate("MainWindow", "START"))
        self.Stop_button.setText(_translate("MainWindow", "STOP"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
