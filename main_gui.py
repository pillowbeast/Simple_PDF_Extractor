import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QTextEdit
from PyQt5.QtCore import Qt, QMimeData


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Create widgets
        self.runButton1 = QPushButton('Raw Text', self)
        self.runButton2 = QPushButton('MP3', self)
        self.LoadFileButton = QPushButton('Load File', self)
        self.input1LineEdit = QLineEdit(self)
        self.input2LineEdit = QLineEdit(self)
        self.input3LineEdit = QLineEdit(self)
        self.input4LineEdit = QLineEdit(self)
        self.input5LineEdit = QLineEdit(self)
        self.input6LineEdit = QLineEdit(self)
        self.outputLabel = QLabel(self)

        # Create layouts
        inputLayout1 = QVBoxLayout()
        inputLayout1.addWidget(QLabel('AWS Key ID:', self))
        inputLayout1.addWidget(self.input1LineEdit)
        inputLayout1.addWidget(QLabel('AWS Secret Key:', self))
        inputLayout1.addWidget(self.input2LineEdit)
        
        inputLayout2 = QVBoxLayout()
        inputLayout2.addStretch(1)
        inputLayout2.addWidget(QLabel('Output name:', self))
        inputLayout2.addWidget(self.input3LineEdit)
        inputLayout2.addWidget(QLabel('Language:', self))
        inputLayout2.addWidget(self.input4LineEdit)
        inputLayout2.addWidget(QLabel('Speed:', self))
        inputLayout2.addWidget(self.input5LineEdit)
        inputLayout2.addWidget(QLabel('Flags:', self))
        inputLayout2.addWidget(self.input6LineEdit)

        loadlayout = QHBoxLayout()
        loadlayout.addWidget(self.LoadFileButton)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.runButton1)
        buttonLayout.addWidget(self.runButton2)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(inputLayout1)
        mainLayout.addLayout(inputLayout2)
        mainLayout.addWidget(QLabel(self))  # Add a separator line
        mainLayout.addLayout(loadlayout)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

        # Set main window properties
        self.setWindowTitle('PDF Parser')
        self.setGeometry(300, 300, 300, 150)

        # Set drag and drop functionality for PDF files
        self.setAcceptDrops(True)

        # Connect signals and slots
        self.runButton1.clicked.connect(self.convert2Text)
        self.runButton2.clicked.connect(self.convert2MP3)
        self.LoadFileButton.clicked.connect(self.loadFile)

    def convert2Text(self):
        # Get input values
        aws_key_id = self.input1LineEdit.text()
        aws_secret_key = self.input2LineEdit.text()
        output_name = self.input3LineEdit.text()
        language = self.input4LineEdit.text()
        speed = self.input5LineEdit.text()
        flags = self.input6LineEdit.text()
        mode = 'txt'

        subprocess.run(['python', 'main.py', '-i', aws_key_id, '-k', aws_secret_key, '-m', mode, '-o', output_name, '-l', language, '-s', speed, '-f', flags])

    def convert2MP3(self):
        # Get input values
        aws_key_id = self.input1LineEdit.text()
        aws_secret_key = self.input2LineEdit.text()
        output_name = self.input3LineEdit.text()
        language = self.input4LineEdit.text()
        speed = self.input5LineEdit.text()
        flags = self.input6LineEdit.text()
        mode = 'mp3'

        subprocess.run(['python', 'main.py', '-i', aws_key_id, '-k', aws_secret_key, '-m', mode, '-o', output_name, '-l', language, '-s', speed, '-f', flags])

    def loadFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.pdf)", options=options)
        if fileName:
            # Open the file and read its contents
            with open(fileName, 'r') as f:
                fileContents = f.read()
            

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        # Get the PDF file path from the dropped url
        file_path = event.mimeData().text()
        file_path = file_path.strip()[7:]

        # Open the PDF file and display it in the text viewer
        with open(file_path, 'r') as f:
            pdf = f.read()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())