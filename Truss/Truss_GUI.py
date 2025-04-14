# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TrussStructuralDesign(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(800, 600)
        self.layout = QtWidgets.QVBoxLayout(Form)

        # File selection
        self.te_Path = QtWidgets.QLineEdit(Form)
        self.te_Path.setObjectName("te_Path")
        self.btn_Open = QtWidgets.QPushButton(Form)
        self.btn_Open.setText("Open File")
        self.btn_Open.setObjectName("btn_Open")
        file_layout = QtWidgets.QHBoxLayout()
        file_layout.addWidget(self.te_Path)
        file_layout.addWidget(self.btn_Open)
        self.layout.addLayout(file_layout)

        # Main layout with design report, graphics view, and link details
        self.main_layout = QtWidgets.QHBoxLayout()

        # Design Report
        self.te_DesignReport = QtWidgets.QTextEdit(Form)
        self.te_DesignReport.setObjectName("te_DesignReport")
        self.te_DesignReport.setReadOnly(True)
        self.te_DesignReport.setFixedWidth(200)
        self.main_layout.addWidget(self.te_DesignReport)

        # Graphics View
        self.gv_Main = QtWidgets.QGraphicsView(Form)
        self.gv_Main.setObjectName("gv_Main")
        self.main_layout.addWidget(self.gv_Main)

        # Link Details
        self.link_details_group = QtWidgets.QGroupBox("Link Details", Form)
        self.link_details_group.setFixedWidth(200)
        link_layout = QtWidgets.QFormLayout()
        self.le_LinkName = QtWidgets.QLineEdit(Form)
        self.le_LinkName.setReadOnly(True)
        self.le_Node1Name = QtWidgets.QLineEdit(Form)
        self.le_Node1Name.setReadOnly(True)
        self.le_Node2Name = QtWidgets.QLineEdit(Form)
        self.le_Node2Name.setReadOnly(True)
        self.le_LinkLength = QtWidgets.QLineEdit(Form)
        self.le_LinkLength.setReadOnly(True)
        link_layout.addRow("Link Name:", self.le_LinkName)
        link_layout.addRow("Node 1:", self.le_Node1Name)
        link_layout.addRow("Node 2:", self.le_Node2Name)
        link_layout.addRow("Length:", self.le_LinkLength)
        self.link_details_group.setLayout(link_layout)
        self.main_layout.addWidget(self.link_details_group)

        self.layout.addLayout(self.main_layout)

        # Mouse Position Label
        self.lbl_MousePos = QtWidgets.QLabel(Form)
        self.lbl_MousePos.setText("Mouse Position: x=0, y=0")
        self.layout.addWidget(self.lbl_MousePos)

        # Zoom Control
        self.spnd_Zoom = QtWidgets.QDoubleSpinBox(Form)
        self.spnd_Zoom.setMinimum(0.01)
        self.spnd_Zoom.setMaximum(10.0)
        self.spnd_Zoom.setValue(1.0)
        self.spnd_Zoom.setObjectName("spnd_Zoom")
        self.layout.addWidget(self.spnd_Zoom)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Truss Structural Design"))