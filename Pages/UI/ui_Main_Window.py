# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Main_Window_2lzKgWw.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect,
    QSize, Qt)
from PySide6.QtGui import (QAction, QFont, QIcon)
from PySide6.QtWidgets import (QComboBox, QFrame, QGridLayout,
    QLCDNumber, QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSizePolicy,
    QTextEdit, QWidget)

class Ui_Main_Window(object):
    def setupUi(self, Main_Window):
        if not Main_Window.objectName():
            Main_Window.setObjectName(u"Main_Window")
        Main_Window.resize(1035, 652)
        icon = QIcon()
        icon.addFile(u"Resources/Icons/write.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        Main_Window.setWindowIcon(icon)
        self.actionSave = QAction(Main_Window)
        self.actionSave.setObjectName(u"actionSave")
        self.actionNew = QAction(Main_Window)
        self.actionNew.setObjectName(u"actionNew")
        self.actionMarkdown = QAction(Main_Window)
        self.actionMarkdown.setObjectName(u"actionMarkdown")
        self.actionPDF = QAction(Main_Window)
        self.actionPDF.setObjectName(u"actionPDF")
        self.action = QAction(Main_Window)
        self.action.setObjectName(u"action")
        self.actionPDF_2 = QAction(Main_Window)
        self.actionPDF_2.setObjectName(u"actionPDF_2")
        self.actionHTML = QAction(Main_Window)
        self.actionHTML.setObjectName(u"actionHTML")
        self.actionOpen = QAction(Main_Window)
        self.actionOpen.setObjectName(u"actionOpen")
        self.action_New = QAction(Main_Window)
        self.action_New.setObjectName(u"action_New")
        self.action_Open = QAction(Main_Window)
        self.action_Open.setObjectName(u"action_Open")
        self.action_Markdown = QAction(Main_Window)
        self.action_Markdown.setObjectName(u"action_Markdown")
        self.action_HTML = QAction(Main_Window)
        self.action_HTML.setObjectName(u"action_HTML")
        self.action_PDF = QAction(Main_Window)
        self.action_PDF.setObjectName(u"action_PDF")
        self.actionSettings = QAction(Main_Window)
        self.actionSettings.setObjectName(u"actionSettings")
        self.actionSave_2 = QAction(Main_Window)
        self.actionSave_2.setObjectName(u"actionSave_2")
        self.actionDOCX = QAction(Main_Window)
        self.actionDOCX.setObjectName(u"actionDOCX")
        self.centralwidget = QWidget(Main_Window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_12 = QGridLayout(self.centralwidget)
        self.gridLayout_12.setSpacing(4)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.gridLayout_12.setContentsMargins(4, 4, 4, 4)
        self.SubjectPlaceholder = QWidget(self.centralwidget)
        self.SubjectPlaceholder.setObjectName(u"SubjectPlaceholder")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SubjectPlaceholder.sizePolicy().hasHeightForWidth())
        self.SubjectPlaceholder.setSizePolicy(sizePolicy)
        self.SubjectPlaceholder.setMinimumSize(QSize(100, 0))
        self.SubjectPlaceholder.setMaximumSize(QSize(400, 16777215))

        self.gridLayout_12.addWidget(self.SubjectPlaceholder, 0, 0, 1, 1)

        self.ContainerLesson = QWidget(self.centralwidget)
        self.ContainerLesson.setObjectName(u"ContainerLesson")
        self.gridLayout_11 = QGridLayout(self.ContainerLesson)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.gridLayout_11.setHorizontalSpacing(0)
        self.gridLayout_11.setVerticalSpacing(2)
        self.gridLayout_11.setContentsMargins(0, 0, 0, 0)
        self.ContainerSubject = QWidget(self.ContainerLesson)
        self.ContainerSubject.setObjectName(u"ContainerSubject")
        self.gridLayout_10 = QGridLayout(self.ContainerSubject)
        self.gridLayout_10.setSpacing(0)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.gridLayout_10.setContentsMargins(0, 0, 0, 0)
        self.TopContainer_0 = QWidget(self.ContainerSubject)
        self.TopContainer_0.setObjectName(u"TopContainer_0")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.TopContainer_0.sizePolicy().hasHeightForWidth())
        self.TopContainer_0.setSizePolicy(sizePolicy1)
        self.gridLayout_4 = QGridLayout(self.TopContainer_0)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setHorizontalSpacing(4)
        self.gridLayout_4.setVerticalSpacing(0)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.TimerSubject_0 = QWidget(self.TopContainer_0)
        self.TimerSubject_0.setObjectName(u"TimerSubject_0")
        sizePolicy1.setHeightForWidth(self.TimerSubject_0.sizePolicy().hasHeightForWidth())
        self.TimerSubject_0.setSizePolicy(sizePolicy1)
        self.gridLayout_5 = QGridLayout(self.TimerSubject_0)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.LCDDisplaySubject_0 = QLCDNumber(self.TimerSubject_0)
        self.LCDDisplaySubject_0.setObjectName(u"LCDDisplaySubject_0")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.LCDDisplaySubject_0.sizePolicy().hasHeightForWidth())
        self.LCDDisplaySubject_0.setSizePolicy(sizePolicy2)
        self.LCDDisplaySubject_0.setDigitCount(8)
        self.LCDDisplaySubject_0.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)

        self.gridLayout_5.addWidget(self.LCDDisplaySubject_0, 0, 0, 1, 1)

        self.ContainerButtonsR_0 = QWidget(self.TimerSubject_0)
        self.ContainerButtonsR_0.setObjectName(u"ContainerButtonsR_0")
        sizePolicy1.setHeightForWidth(self.ContainerButtonsR_0.sizePolicy().hasHeightForWidth())
        self.ContainerButtonsR_0.setSizePolicy(sizePolicy1)
        self.gridLayout_6 = QGridLayout(self.ContainerButtonsR_0)
        self.gridLayout_6.setSpacing(0)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.PBPlaySubject_0 = QPushButton(self.ContainerButtonsR_0)
        self.PBPlaySubject_0.setObjectName(u"PBPlaySubject_0")
        self.PBPlaySubject_0.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.gridLayout_6.addWidget(self.PBPlaySubject_0, 0, 0, 1, 1)

        self.PBResetSubject_0 = QPushButton(self.ContainerButtonsR_0)
        self.PBResetSubject_0.setObjectName(u"PBResetSubject_0")
        self.PBResetSubject_0.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.gridLayout_6.addWidget(self.PBResetSubject_0, 1, 0, 1, 1)


        self.gridLayout_5.addWidget(self.ContainerButtonsR_0, 0, 1, 1, 1)


        self.gridLayout_4.addWidget(self.TimerSubject_0, 0, 1, 1, 1)

        self.ContainerTitle_0 = QWidget(self.TopContainer_0)
        self.ContainerTitle_0.setObjectName(u"ContainerTitle_0")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.ContainerTitle_0.sizePolicy().hasHeightForWidth())
        self.ContainerTitle_0.setSizePolicy(sizePolicy3)
        self.gridLayout_7 = QGridLayout(self.ContainerTitle_0)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_7.setHorizontalSpacing(4)
        self.gridLayout_7.setVerticalSpacing(0)
        self.gridLayout_7.setContentsMargins(0, 0, 0, 0)
        self.LELessonTitle_0 = QLineEdit(self.ContainerTitle_0)
        self.LELessonTitle_0.setObjectName(u"LELessonTitle_0")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.LELessonTitle_0.sizePolicy().hasHeightForWidth())
        self.LELessonTitle_0.setSizePolicy(sizePolicy4)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.LELessonTitle_0.setFont(font)

        self.gridLayout_7.addWidget(self.LELessonTitle_0, 0, 0, 1, 1, Qt.AlignmentFlag.AlignBottom)

        self.ContainerSession_0 = QWidget(self.ContainerTitle_0)
        self.ContainerSession_0.setObjectName(u"ContainerSession_0")
        self.gridLayout_8 = QGridLayout(self.ContainerSession_0)
        self.gridLayout_8.setSpacing(0)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_8.setContentsMargins(0, 0, 0, 0)
        self.label_0 = QLabel(self.ContainerSession_0)
        self.label_0.setObjectName(u"label_0")

        self.gridLayout_8.addWidget(self.label_0, 0, 0, 1, 1)

        self.CBSessionType_0 = QComboBox(self.ContainerSession_0)
        self.CBSessionType_0.setObjectName(u"CBSessionType_0")
        self.CBSessionType_0.setMinimumSize(QSize(125, 0))
        font1 = QFont()
        font1.setPointSize(9)
        self.CBSessionType_0.setFont(font1)
        self.CBSessionType_0.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.CBSessionType_0.setEditable(True)
        self.CBSessionType_0.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)

        self.gridLayout_8.addWidget(self.CBSessionType_0, 1, 0, 1, 1)


        self.gridLayout_7.addWidget(self.ContainerSession_0, 0, 1, 1, 1)


        self.gridLayout_4.addWidget(self.ContainerTitle_0, 0, 0, 1, 1)


        self.gridLayout_10.addWidget(self.TopContainer_0, 0, 0, 1, 1)

        self.TEContent_0 = QTextEdit(self.ContainerSubject)
        self.TEContent_0.setObjectName(u"TEContent_0")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.TEContent_0.sizePolicy().hasHeightForWidth())
        self.TEContent_0.setSizePolicy(sizePolicy5)
        font2 = QFont()
        font2.setPointSize(12)
        self.TEContent_0.setFont(font2)

        self.gridLayout_10.addWidget(self.TEContent_0, 1, 0, 1, 1)


        self.gridLayout_11.addWidget(self.ContainerSubject, 2, 0, 1, 1)

        self.widget = QWidget(self.ContainerLesson)
        self.widget.setObjectName(u"widget")
        self.gridLayout_3 = QGridLayout(self.widget)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setHorizontalSpacing(2)
        self.gridLayout_3.setVerticalSpacing(0)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.LELessonName = QLineEdit(self.widget)
        self.LELessonName.setObjectName(u"LELessonName")
        font3 = QFont()
        font3.setPointSize(20)
        font3.setBold(True)
        self.LELessonName.setFont(font3)

        self.gridLayout_3.addWidget(self.LELessonName, 0, 0, 1, 1)

        self.Container_TopR = QWidget(self.widget)
        self.Container_TopR.setObjectName(u"Container_TopR")
        self.gridLayout_9 = QGridLayout(self.Container_TopR)
        self.gridLayout_9.setSpacing(0)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.gridLayout_9.setContentsMargins(0, 0, 0, 0)
        self.PBNewSubject = QPushButton(self.Container_TopR)
        self.PBNewSubject.setObjectName(u"PBNewSubject")

        self.gridLayout_9.addWidget(self.PBNewSubject, 0, 0, 1, 1)

        self.PBEndLesson = QPushButton(self.Container_TopR)
        self.PBEndLesson.setObjectName(u"PBEndLesson")

        self.gridLayout_9.addWidget(self.PBEndLesson, 1, 0, 1, 1)


        self.gridLayout_3.addWidget(self.Container_TopR, 0, 3, 1, 1)

        self.TimeLesson = QWidget(self.widget)
        self.TimeLesson.setObjectName(u"TimeLesson")
        sizePolicy1.setHeightForWidth(self.TimeLesson.sizePolicy().hasHeightForWidth())
        self.TimeLesson.setSizePolicy(sizePolicy1)
        self.gridLayout_2 = QGridLayout(self.TimeLesson)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(2, 0, 0, 0)
        self.LCDDisplay_lesson = QLCDNumber(self.TimeLesson)
        self.LCDDisplay_lesson.setObjectName(u"LCDDisplay_lesson")
        sizePolicy2.setHeightForWidth(self.LCDDisplay_lesson.sizePolicy().hasHeightForWidth())
        self.LCDDisplay_lesson.setSizePolicy(sizePolicy2)
        self.LCDDisplay_lesson.setDigitCount(8)
        self.LCDDisplay_lesson.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)

        self.gridLayout_2.addWidget(self.LCDDisplay_lesson, 0, 0, 1, 1)

        self.ContainerButtonsR_Lesson = QWidget(self.TimeLesson)
        self.ContainerButtonsR_Lesson.setObjectName(u"ContainerButtonsR_Lesson")
        sizePolicy1.setHeightForWidth(self.ContainerButtonsR_Lesson.sizePolicy().hasHeightForWidth())
        self.ContainerButtonsR_Lesson.setSizePolicy(sizePolicy1)
        self.gridLayout = QGridLayout(self.ContainerButtonsR_Lesson)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.PBPPlayLesson = QPushButton(self.ContainerButtonsR_Lesson)
        self.PBPPlayLesson.setObjectName(u"PBPPlayLesson")
        self.PBPPlayLesson.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.gridLayout.addWidget(self.PBPPlayLesson, 0, 0, 1, 1)

        self.PBResetLesson = QPushButton(self.ContainerButtonsR_Lesson)
        self.PBResetLesson.setObjectName(u"PBResetLesson")
        self.PBResetLesson.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.gridLayout.addWidget(self.PBResetLesson, 1, 0, 1, 1)


        self.gridLayout_2.addWidget(self.ContainerButtonsR_Lesson, 0, 1, 1, 1)


        self.gridLayout_3.addWidget(self.TimeLesson, 0, 1, 1, 1)

        self.line = QFrame(self.widget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_3.addWidget(self.line, 0, 2, 1, 1)


        self.gridLayout_11.addWidget(self.widget, 0, 0, 1, 1)

        self.line_2 = QFrame(self.ContainerLesson)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_11.addWidget(self.line_2, 1, 0, 1, 1)


        self.gridLayout_12.addWidget(self.ContainerLesson, 0, 1, 1, 1)

        Main_Window.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Main_Window)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1035, 33))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuExport = QMenu(self.menuFile)
        self.menuExport.setObjectName(u"menuExport")
        Main_Window.setMenuBar(self.menubar)
        QWidget.setTabOrder(self.LELessonName, self.LELessonTitle_0)
        QWidget.setTabOrder(self.LELessonTitle_0, self.CBSessionType_0)
        QWidget.setTabOrder(self.CBSessionType_0, self.TEContent_0)
        QWidget.setTabOrder(self.TEContent_0, self.PBNewSubject)
        QWidget.setTabOrder(self.PBNewSubject, self.PBEndLesson)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.action_New)
        self.menuFile.addAction(self.action_Open)
        self.menuFile.addAction(self.actionSave_2)
        self.menuFile.addAction(self.menuExport.menuAction())
        self.menuFile.addAction(self.actionSettings)
        self.menuExport.addAction(self.action_Markdown)
        self.menuExport.addAction(self.action_HTML)
        self.menuExport.addAction(self.action_PDF)
        self.menuExport.addAction(self.actionDOCX)

        self.retranslateUi(Main_Window)

        QMetaObject.connectSlotsByName(Main_Window)
    # setupUi

    def retranslateUi(self, Main_Window):
        Main_Window.setWindowTitle(QCoreApplication.translate("Main_Window", u"TAP", None))
        self.actionSave.setText(QCoreApplication.translate("Main_Window", u"Save", None))
        self.actionNew.setText(QCoreApplication.translate("Main_Window", u"New", None))
        self.actionMarkdown.setText(QCoreApplication.translate("Main_Window", u"Markdown", None))
        self.actionPDF.setText(QCoreApplication.translate("Main_Window", u"PDF", None))
        self.action.setText(QCoreApplication.translate("Main_Window", u"DocX", None))
        self.actionPDF_2.setText(QCoreApplication.translate("Main_Window", u"PDF", None))
        self.actionHTML.setText(QCoreApplication.translate("Main_Window", u"HTML", None))
        self.actionOpen.setText(QCoreApplication.translate("Main_Window", u"Open", None))
        self.action_New.setText(QCoreApplication.translate("Main_Window", u"New", None))
        self.action_Open.setText(QCoreApplication.translate("Main_Window", u"Open", None))
        self.action_Markdown.setText(QCoreApplication.translate("Main_Window", u"Markdown", None))
        self.action_HTML.setText(QCoreApplication.translate("Main_Window", u"HTML", None))
        self.action_PDF.setText(QCoreApplication.translate("Main_Window", u"PDF", None))
        self.actionSettings.setText(QCoreApplication.translate("Main_Window", u"Settings", None))
        self.actionSave_2.setText(QCoreApplication.translate("Main_Window", u"Save", None))
        self.actionDOCX.setText(QCoreApplication.translate("Main_Window", u"DOCX", None))
        self.PBPlaySubject_0.setText(QCoreApplication.translate("Main_Window", u"Play/Pause", None))
        self.PBResetSubject_0.setText(QCoreApplication.translate("Main_Window", u"Reset", None))
        self.LELessonTitle_0.setInputMask("")
        self.LELessonTitle_0.setText("")
        self.LELessonTitle_0.setPlaceholderText(QCoreApplication.translate("Main_Window", u"## Subject Title...", None))
        self.label_0.setText(QCoreApplication.translate("Main_Window", u"Session Type", None))
        self.CBSessionType_0.setPlaceholderText(QCoreApplication.translate("Main_Window", u"Type...", None))
        self.LELessonName.setPlaceholderText(QCoreApplication.translate("Main_Window", u"# Lesson Name", None))
        self.PBNewSubject.setText(QCoreApplication.translate("Main_Window", u"New Subject", None))
        self.PBEndLesson.setText(QCoreApplication.translate("Main_Window", u"End Lesson", None))
        self.PBPPlayLesson.setText(QCoreApplication.translate("Main_Window", u"Play", None))
        self.PBResetLesson.setText(QCoreApplication.translate("Main_Window", u"Reset", None))
        self.menuFile.setTitle(QCoreApplication.translate("Main_Window", u"File", None))
        self.menuExport.setTitle(QCoreApplication.translate("Main_Window", u"Export", None))
    # retranslateUi

