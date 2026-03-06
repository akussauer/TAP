# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Settings_DialognxpvaP.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect,
    QSize, Qt)
from PySide6.QtGui import (QFont, QIcon)
from PySide6.QtWidgets import (QComboBox, QGridLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(340, 340)
        SettingsDialog.setMinimumSize(QSize(325, 175))
        icon = QIcon()
        icon.addFile(u"Resources/Icons/write.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        SettingsDialog.setWindowIcon(icon)
        self.gridLayout_3 = QGridLayout(SettingsDialog)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.widget_2 = QWidget(SettingsDialog)
        self.widget_2.setObjectName(u"widget_2")
        self.gridLayout_2 = QGridLayout(self.widget_2)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(57, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 0, 0, 1, 1)

        self.widget = QWidget(self.widget_2)
        self.widget.setObjectName(u"widget")
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(2)
        self.gridLayout.setVerticalSpacing(4)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.ButtonSave = QPushButton(self.widget)
        self.ButtonSave.setObjectName(u"ButtonSave")
        self.ButtonSave.setMinimumSize(QSize(100, 0))

        self.gridLayout.addWidget(self.ButtonSave, 0, 0, 1, 1)

        self.ButtonReset = QPushButton(self.widget)
        self.ButtonReset.setObjectName(u"ButtonReset")
        self.ButtonReset.setMinimumSize(QSize(100, 0))

        self.gridLayout.addWidget(self.ButtonReset, 0, 1, 1, 1)


        self.gridLayout_2.addWidget(self.widget, 0, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(57, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_2, 0, 2, 1, 1)


        self.gridLayout_3.addWidget(self.widget_2, 1, 0, 1, 1)

        self.scrollArea = QScrollArea(SettingsDialog)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 308, 307))
        self.gridLayout_11 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.gridLayout_11.setVerticalSpacing(0)
        self.gridLayout_11.setContentsMargins(20, -1, 20, -1)
        self.widget_4 = QWidget(self.scrollAreaWidgetContents)
        self.widget_4.setObjectName(u"widget_4")
        self.gridLayout_5 = QGridLayout(self.widget_4)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(-1, 4, -1, 4)
        self.CBStyle = QComboBox(self.widget_4)
        self.CBStyle.setObjectName(u"CBStyle")
        self.CBStyle.setMaximumSize(QSize(150, 16777215))
        self.CBStyle.setEditable(True)
        self.CBStyle.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.gridLayout_5.addWidget(self.CBStyle, 0, 2, 1, 1)

        self.label_2 = QLabel(self.widget_4)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_5.addWidget(self.label_2, 0, 1, 1, 1)


        self.gridLayout_11.addWidget(self.widget_4, 1, 0, 1, 1)

        self.widget_9 = QWidget(self.scrollAreaWidgetContents)
        self.widget_9.setObjectName(u"widget_9")
        self.gridLayout_10 = QGridLayout(self.widget_9)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.gridLayout_10.setContentsMargins(-1, 4, -1, 4)
        self.label_7 = QLabel(self.widget_9)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_10.addWidget(self.label_7, 0, 0, 1, 1)

        self.LE_Save = QLineEdit(self.widget_9)
        self.LE_Save.setObjectName(u"LE_Save")
        self.LE_Save.setMaximumSize(QSize(150, 16777215))

        self.gridLayout_10.addWidget(self.LE_Save, 0, 1, 1, 1)


        self.gridLayout_11.addWidget(self.widget_9, 9, 0, 1, 1)

        self.widget_5 = QWidget(self.scrollAreaWidgetContents)
        self.widget_5.setObjectName(u"widget_5")
        self.gridLayout_6 = QGridLayout(self.widget_5)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(-1, 4, -1, 4)
        self.label_3 = QLabel(self.widget_5)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_6.addWidget(self.label_3, 0, 0, 1, 1)

        self.CBLang = QComboBox(self.widget_5)
        self.CBLang.setObjectName(u"CBLang")
        self.CBLang.setMaximumSize(QSize(150, 16777215))
        self.CBLang.setEditable(True)
        self.CBLang.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.gridLayout_6.addWidget(self.CBLang, 0, 1, 1, 1)


        self.gridLayout_11.addWidget(self.widget_5, 2, 0, 1, 1)

        self.widget_3 = QWidget(self.scrollAreaWidgetContents)
        self.widget_3.setObjectName(u"widget_3")
        self.gridLayout_4 = QGridLayout(self.widget_3)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(-1, 4, -1, 4)
        self.label = QLabel(self.widget_3)
        self.label.setObjectName(u"label")

        self.gridLayout_4.addWidget(self.label, 0, 0, 1, 1)

        self.CBTheme = QComboBox(self.widget_3)
        self.CBTheme.setObjectName(u"CBTheme")
        self.CBTheme.setMaximumSize(QSize(150, 16777215))
        self.CBTheme.setEditable(True)
        self.CBTheme.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.gridLayout_4.addWidget(self.CBTheme, 0, 1, 1, 1)


        self.gridLayout_11.addWidget(self.widget_3, 0, 0, 1, 1)

        self.widget_8 = QWidget(self.scrollAreaWidgetContents)
        self.widget_8.setObjectName(u"widget_8")
        self.gridLayout_9 = QGridLayout(self.widget_8)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.gridLayout_9.setContentsMargins(-1, 4, -1, 4)
        self.label_6 = QLabel(self.widget_8)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_9.addWidget(self.label_6, 0, 0, 1, 1)

        self.LE_SubTimer = QLineEdit(self.widget_8)
        self.LE_SubTimer.setObjectName(u"LE_SubTimer")
        self.LE_SubTimer.setMaximumSize(QSize(150, 16777215))

        self.gridLayout_9.addWidget(self.LE_SubTimer, 0, 1, 1, 1)


        self.gridLayout_11.addWidget(self.widget_8, 8, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_11.addItem(self.verticalSpacer, 10, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.gridLayout_11.addItem(self.verticalSpacer_2, 4, 0, 1, 1)

        self.widget_7 = QWidget(self.scrollAreaWidgetContents)
        self.widget_7.setObjectName(u"widget_7")
        self.gridLayout_8 = QGridLayout(self.widget_7)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_8.setContentsMargins(-1, 4, -1, 4)
        self.label_5 = QLabel(self.widget_7)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_8.addWidget(self.label_5, 0, 0, 1, 1)

        self.LE_LessTimer = QLineEdit(self.widget_7)
        self.LE_LessTimer.setObjectName(u"LE_LessTimer")
        self.LE_LessTimer.setMaximumSize(QSize(150, 16777215))

        self.gridLayout_8.addWidget(self.LE_LessTimer, 0, 1, 1, 1)


        self.gridLayout_11.addWidget(self.widget_7, 7, 0, 1, 1)

        self.widget_6 = QWidget(self.scrollAreaWidgetContents)
        self.widget_6.setObjectName(u"widget_6")
        self.gridLayout_7 = QGridLayout(self.widget_6)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_7.setContentsMargins(-1, 4, -1, 4)
        self.label_4 = QLabel(self.widget_6)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_7.addWidget(self.label_4, 0, 0, 1, 1)

        self.LE_NewSubject = QLineEdit(self.widget_6)
        self.LE_NewSubject.setObjectName(u"LE_NewSubject")
        self.LE_NewSubject.setMaximumSize(QSize(150, 16777215))

        self.gridLayout_7.addWidget(self.LE_NewSubject, 0, 1, 1, 1)


        self.gridLayout_11.addWidget(self.widget_6, 6, 0, 1, 1)

        self.label_8 = QLabel(self.scrollAreaWidgetContents)
        self.label_8.setObjectName(u"label_8")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label_8.setFont(font)
        self.label_8.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_11.addWidget(self.label_8, 5, 0, 1, 1)

        self.widget_10 = QWidget(self.scrollAreaWidgetContents)
        self.widget_10.setObjectName(u"widget_10")
        self.gridLayout_12 = QGridLayout(self.widget_10)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.gridLayout_12.setContentsMargins(-1, 4, -1, 4)
        self.label_9 = QLabel(self.widget_10)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_12.addWidget(self.label_9, 0, 0, 1, 1)

        self.PHColour = QPushButton(self.widget_10)
        self.PHColour.setObjectName(u"PHColour")

        self.gridLayout_12.addWidget(self.PHColour, 0, 1, 1, 1)


        self.gridLayout_11.addWidget(self.widget_10, 3, 0, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_3.addWidget(self.scrollArea, 0, 0, 1, 1)


        self.retranslateUi(SettingsDialog)

        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"Settings", None))
        self.ButtonSave.setText(QCoreApplication.translate("SettingsDialog", u"Save", None))
        self.ButtonReset.setText(QCoreApplication.translate("SettingsDialog", u"Reset", None))
        self.label_2.setText(QCoreApplication.translate("SettingsDialog", u"Style", None))
        self.label_7.setText(QCoreApplication.translate("SettingsDialog", u"Save", None))
        self.label_3.setText(QCoreApplication.translate("SettingsDialog", u"Spell-Check Language", None))
        self.label.setText(QCoreApplication.translate("SettingsDialog", u"Theme", None))
        self.label_6.setText(QCoreApplication.translate("SettingsDialog", u"Subject Timer", None))
        self.label_5.setText(QCoreApplication.translate("SettingsDialog", u"Lesson Timer", None))
        self.label_4.setText(QCoreApplication.translate("SettingsDialog", u"New Subject", None))
        self.label_8.setText(QCoreApplication.translate("SettingsDialog", u"Key Commands", None))
        self.label_9.setText(QCoreApplication.translate("SettingsDialog", u"Markdown Colour", None))
        self.PHColour.setText(QCoreApplication.translate("SettingsDialog", u"Colour", None))
    # retranslateUi

