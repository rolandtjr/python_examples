#!/usr/bin/env python3
"""pyqt_tabs.py
----------------
This module contains a Python script utilizing the PyQt5 library to create a
basic graphical user interface (GUI) application. The application showcases a
tabbed window with two tabs, each containing a grid of numbers. The first tab
displays numbers from 1 to 100, and the second tab displays numbers from 101 to
200, arranged in a grid format.

Dependencies:
    PyQt5
"""
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QGridLayout,
    QLabel,
)


class TabbedWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tabbed Window")
        self.resize(300, 300)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.tab1 = QWidget()
        self.tab_widget.addTab(self.tab1, "1-100")

        layout1 = QGridLayout()
        layout1.setHorizontalSpacing(10)
        layout1.setVerticalSpacing(10)

        for i in range(1, 101):
            column = (i - 1) % 10
            row = (i - 1) // 10
            label = QLabel(str(i))
            layout1.addWidget(label, row, column)

        self.tab1.setLayout(layout1)

        self.tab2 = QWidget()
        self.tab_widget.addTab(self.tab2, "101-200")

        layout2 = QGridLayout()
        layout2.setHorizontalSpacing(10)
        layout2.setVerticalSpacing(10)

        for i in range(101, 201):
            column = (i - 101) % 10
            row = (i - 101) // 10
            label = QLabel(str(i))
            layout2.addWidget(label, row, column)

        self.tab2.setLayout(layout2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TabbedWindow()
    window.show()
    sys.exit(app.exec_())
