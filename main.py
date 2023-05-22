import cv2
import webbrowser
from pyzbar.pyzbar import decode
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QLabel
from PyQt5.QtCore import QSize, Qt

from PyQt5.QtGui import QPainter, QFont, QColor


class QRCodeScanner(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize UI
        self.initUI()

        # Create a QLabel widget for image display
        self.label = QLabel(self)
        self.label.move(10, 50)
        self.label.resize(self.width() - 20, self.height() - 110)

        # Create a QLabel widget for displaying the code data
        self.code_data_label = QLabel(self)
        self.code_data_label.move(10, self.height() - 50)
        self.code_data_label.resize(self.width() - 20, 40)
        self.code_data_label.setAlignment(Qt.AlignCenter)
        self.code_data_label.setStyleSheet("QLabel { font-weight: bold; }")

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('QR Code Scanner')

    def initUI(self):
        # Enable drag-and-drop
        self.setAcceptDrops(True)

        # Set the fixed size of the window
        self.setFixedSize(800, 600)

        # Create a combo box for selecting codes
        self.codes_select = QComboBox(self)
        self.codes_select.move(10, 10)
        self.codes_select.activated.connect(self.showImage)

        self.setWindowTitle('QR Code Scanner')

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.openImage(file_path)
                break

    def openImage(self, file_path):
        # Read the image
        self.img = cv2.imread(file_path)

        # Convert the image to grayscale
        self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        # Decode QR codes or barcodes in the image
        self.qr_codes = decode(self.gray)
        if not self.qr_codes:
            self.barcodes = decode(self.img)

        # Populate the list of detected codes
        self.codes_list = []
        if self.qr_codes:
            for qr_code in self.qr_codes:
                self.codes_list.append(qr_code.data.decode('utf-8'))
        elif self.barcodes:
            for barcode in self.barcodes:
                self.codes_list.append(barcode.data.decode('utf-8'))

        # If no codes are found in the image, display a message
        if not self.codes_list:
            print('QR Code or Barcode not detected')
            return

        # Update the code selection combo box
        self.codes_select.clear()
        self.codes_select.addItems(self.codes_list)

        # Display the image
        self.showImage()

    def showImage(self):
        # Get the selected code from the combo box
        selected_code = self.codes_select.currentText()

        # Find the selected code in the image
        qr_code_found = False
        for qr_code in self.qr_codes:
            if qr_code.data.decode('utf-8') == selected_code:
                qr_code_found = True
                x, y, w, h = qr_code.rect
                cv2.rectangle(self.img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                qr_data = qr_code.data.decode('utf-8')
                self.code_data_label.setText(f"QR Code Data: {qr_data}")
                if qr_data.startswith('http://') or qr_data.startswith('https://'):
                    webbrowser.open(qr_data)
                break

        if not qr_code_found:
            for barcode in self.barcodes:
                if barcode.data.decode('utf-8') == selected_code:
                    x, y, w, h = barcode.rect
                    cv2.rectangle(self.img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    barcode_data = barcode.data.decode('utf-8')
                    self.code_data_label.setText(f"Barcode Data: {barcode_data}")
                    break
            else:
                print('QR Code or Barcode not detected')
                return

        # Convert the image to a format that can be displayed in the application window
        height, width, channel = self.img.shape
        bytesPerLine = 3 * width
        qImg = QImage(self.img.data, width, height, bytesPerLine, QImage.Format_RGB888)

        # Determine the image size to fit within the window while maintaining aspect ratio
        img_qsize = QSize(width, height)
        app_qsize = QSize(self.width() - 20, self.height() - 110)
        img_qsize.scale(app_qsize, Qt.KeepAspectRatio)

        # Create a pixmap with the scaled image
        scaled_qimg = qImg.scaled(img_qsize.width(), img_qsize.height(), Qt.KeepAspectRatio)
        pixmap = QPixmap.fromImage(scaled_qimg)

        # Update the image label
        self.label.setPixmap(pixmap)

        # Hide the text label if there is no code selected
        if not selected_code:
            self.code_data_label.setText("")

    def paintEvent(self, event):
        # Draw text on the background of the window
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        font = QFont("Arial", 20, QFont.Bold)

        # Set the text color to red
        text_color = QColor(128, 128, 128)
        painter.setPen(text_color)

        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, "Drag and drop an image here")


if __name__ == '__main__':
    app = QApplication([])
    window = QRCodeScanner()
    window.show()
    app.exec_()
