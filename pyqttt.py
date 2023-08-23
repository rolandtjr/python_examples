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

        # Set the main window title and size
        self.setWindowTitle("Tabbed Window")
        self.resize(300, 300)

        # Create a tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create the first tab
        self.tab1 = QWidget()
        self.tab_widget.addTab(self.tab1, "1-100")

        # Create a grid layout for the first tab
        layout1 = QGridLayout()
        layout1.setHorizontalSpacing(10)
        layout1.setVerticalSpacing(10)

        # Add the numbers 1-100 to the layout
        for i in range(1, 101):
            column = (i - 1) % 10
            row = (i - 1) // 10
            label = QLabel(str(i))
            layout1.addWidget(label, row, column)

        # Set the layout for the first tab
        self.tab1.setLayout(layout1)

        # Create the second tab
        self.tab2 = QWidget()
        self.tab_widget.addTab(self.tab2, "101-200")

        # Create a grid layout for the second tab
        layout2 = QGridLayout()
        layout2.setHorizontalSpacing(10)
        layout2.setVerticalSpacing(10)

        # Add the numbers 101-200 to the layout
        for i in range(101, 201):
            column = (i - 101) % 10
            row = (i - 101) // 10
            label = QLabel(str(i))
            layout2.addWidget(label, row, column)

        # Set the layout for the second tab
        self.tab2.setLayout(layout2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TabbedWindow()
    window.show()
    sys.exit(app.exec_())
