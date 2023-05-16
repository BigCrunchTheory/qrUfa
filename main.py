import cv2
import webbrowser
from pyzbar.pyzbar import decode
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QLabel
from PyQt5.QtCore import QSize, Qt

class QRCodeScanner(QMainWindow):
    def __init__(self):
        super().__init__()

        # Инициализируем UI
        self.initUI()

        # Открываем картинку
        self.img = cv2.imread('both.jpg')

        # Переводим картинку в оттенки серого
        self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        # Декодируем qr-коды или штрих-коды на картинке
        self.qr_codes = decode(self.gray)
        if not self.qr_codes:
            self.barcodes = decode(self.img)

        # Заполняем список найденных кодов
        self.codes_list = []
        if self.qr_codes:
            for qr_code in self.qr_codes:
                self.codes_list.append(qr_code.data.decode('utf-8'))
        elif self.barcodes:
            for barcode in self.barcodes:
                self.codes_list.append(barcode.data.decode('utf-8'))

        # Если на картинке не найдено ни одного кода, выводим сообщение
        if not self.codes_list:
            print('QR Code or Barcode not detected')
            return

        # Обновляем список кодов в выборе
        self.codes_select.addItems(self.codes_list)

        # Выводим изображение на экран
        self.showImage()

    def initUI(self):
        # Создаем окно с выбором кода из списка найденных на картинке
        self.codes_select = QComboBox(self)
        self.codes_select.move(10, 10)
        self.codes_select.activated.connect(self.showImage)

        # Создаем метку для отображения изображения
        self.label = QLabel(self)
        self.label.move(10, 50)
        self.label.resize(self.width() - 20, self.height() - 60)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('QR Code Scanner')

    def showImage(self):
        # Получаем выбранный код из списка
        selected_code = self.codes_select.currentText()

        # Ищем выбранный код на изображении
        qr_code_found = False
        for qr_code in self.qr_codes:
            if qr_code.data.decode('utf-8') == selected_code:
                qr_code_found = True

                # Рисуем прямоугольник вокруг qr-кода
                x, y, w, h = qr_code.rect
                cv2.rectangle(self.img, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Получаем текст из декодированных данных qr-кода
                qr_data = qr_code.data.decode('utf-8')
                print(f"QR Code Data: {qr_data}")

                # Если qr_data является ссылкой, открываем браузер и переходим по ссылке
                if qr_data.startswith('http://') or qr_data.startswith('https://'):
                    webbrowser.open(qr_data)

                break

        if not qr_code_found:
            for barcode in self.barcodes:
                if barcode.data.decode('utf-8') == selected_code:
                    # Рисуем прямоугольник вокруг штрих-кода
                    x, y, w, h = barcode.rect
                    cv2.rectangle(self.img, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # Получаем текст из декодированных данных штрих-кода
                    barcode_data = barcode.data.decode('utf-8')
                    print(f"Barcode Data: {barcode_data}")

                    break

            else:
                print('QR Code or Barcode not detected')
                return

        # Конвертируем изображение в формат, который можно вывести в окне приложения
        height, width, channel = self.img.shape
        bytesPerLine = 3 * width
        qImg = QImage(self.img.data, width, height, bytesPerLine, QImage.Format_RGB888)

        # Определяем размеры изображения, чтобы подгонеть его под размеры окна, сохраняя пропорции
        img_qsize = QSize(width, height)
        app_qsize = QSize(self.width() - 20, self.height() - 40)
        img_qsize.scale(app_qsize, Qt.KeepAspectRatio)

        # Создаем pixmap с отмасштабированным изображением
        scaled_qimg = qImg.scaled(img_qsize.width(), img_qsize.height(), Qt.KeepAspectRatio)
        pixmap = QPixmap.fromImage(scaled_qimg)

        # Обновляем изображение в окне приложения
        self.label.setPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication([])
    window = QRCodeScanner()
    window.show()
    app.exec_()