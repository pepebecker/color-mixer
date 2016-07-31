import sys
from PyQt4 import QtGui, QtCore, uic


class Safe:
    def __init__(self):
        self.code = [203, 75, 164]
        self.secret = ""

        self.unlocked = False
        self.new_code = [None, None, None]
        self.isReady = False
        self.isPrepared = False

        self.unlockCallback = None
        self.setCodeCallback = None

        self.reset()

    def reset(self):
        self.unlocked = False
        self.new_code = [None, None, None]
        self.isReady = False
        self.isPrepared = False
        print "Reset"

    def prepare(self):
        self.isPrepared = True
        print "Prepared"

    def ready(self):
        self.isPrepared = False
        self.isReady = True
        print "Ready"

    def unlock(self):
        self.isReady = False
        self.unlocked = True
        print "Unlocked"

    def apply_new_code(self):
        self.code = self.new_code
        print "Code Changed"

    def numberEnteredAt(self, index):
        return type(self.new_code[index]) == int

    def allNumbersEntered(self):
        return self.numberEnteredAt(0) and self.numberEnteredAt(1) and self.numberEnteredAt(2)

    def enter_number_1(self, n):
        if self.unlocked:
            if self.isReady and not self.numberEnteredAt(1):
                self.new_code[0] = n
            else:
                self.reset()
        else:
            if self.isReady and not self.numberEnteredAt(0) and not self.numberEnteredAt(1) and not self.numberEnteredAt(2):
                if self.code[0] == n:
                    self.new_code[0] = n
                    print "First Number Entered"
            else:
                self.reset()

    def enter_number_2(self, n):
        if self.unlocked:
            if self.numberEnteredAt(0) and not self.numberEnteredAt(2):
                self.new_code[1] = n
            else:
                self.reset()
        else:
            if self.numberEnteredAt(0) and not self.numberEnteredAt(1) and not self.numberEnteredAt(2):
                if self.code[1] == n:
                    self.new_code[1] = n
                    print "Second Number Entered"
            else:
                self.reset()

    def enter_number_3(self, n):
        if self.unlocked:
            if self.numberEnteredAt(0) and self.numberEnteredAt(1):
                self.new_code[2] = n
            else:
                self.reset()
        else:
            if self.numberEnteredAt(0) and self.numberEnteredAt(1) and not self.numberEnteredAt(2):
                if self.code[2] == n:
                    self.new_code[2] = n
                    print "Third Number Entered"
            else:
                self.reset()

    def enter_number_4(self, n):
        if self.unlocked:
            if n == 128:
                self.ready()
            elif self.allNumbersEntered() and n == 255:
                self.apply_new_code()
                if self.setCodeCallback:
                    self.setCodeCallback()

            if n < 128:
                self.reset()
        else:
            if n == 0:
                self.prepare()
            elif self.isPrepared and n == 128:
                self.ready()
            elif self.allNumbersEntered() and n == 255:
                self.unlock()

            if (not self.isPrepared and n < 128) or (not self.allNumbersEntered() and not self.unlocked and n == 255):
                self.reset()

        if self.unlocked:
            if n == 255:
                self.reset()
                self.unlocked = True
                if self.unlockCallback:
                    self.unlockCallback()
            if n < 128:
                self.reset()


class ColorMixer(QtGui.QWidget):
    def __init__(self):
        super(ColorMixer, self).__init__()

        self.settings = QtCore.QSettings("PepeApps", "ColorMixer")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

        interface = "mixer.ui"
        uic.loadUi(interface, self)
        self.setMinimumWidth(400)
        self.safe = Safe()
        self.safe.secret = self.settings.value("secret").toString()

        code = self.settings.value("code").toList()
        if len(code) == 3:
            self.safe.code = code

        self.safe.unlockCallback = self.unlock_message
        self.safe.setCodeCallback = self.save_new_code

        self.connect_widgets()
        self.update_gui()

    def unlock_message(self):
        self.safe.unlocked = True
        secret, ok = QtGui.QInputDialog().getText(self, "Safe", "Secret:", QtGui.QLineEdit.Normal, self.safe.secret)
        if ok:
            self.safe.secret = secret
            self.settings.setValue("secret", secret)
            print "New secret saved."
        print secret

    def save_new_code(self):
        self.settings.setValue("code", self.safe.code)

    def connect_widgets(self):
        self.slider_1.valueChanged.connect(self.update_gui)
        self.slider_2.valueChanged.connect(self.update_gui)
        self.slider_3.valueChanged.connect(self.update_gui)
        self.slider_4.valueChanged.connect(self.update_gui)

        self.slider_1.valueChanged.connect(self.safe.enter_number_1)
        self.slider_2.valueChanged.connect(self.safe.enter_number_2)
        self.slider_3.valueChanged.connect(self.safe.enter_number_3)
        self.slider_4.valueChanged.connect(self.safe.enter_number_4)

    def get_color(self):
        return QtGui.QColor(self.slider_1.value(), self.slider_2.value(), self.slider_3.value(), self.slider_4.value())

    def update_gui(self):
        red = self.get_color().red()
        green = self.get_color().green()
        blue = self.get_color().blue()
        alpha = self.get_color().alpha()

        self.border_color = "white"

        if self.safe.isReady or self.safe.numberEnteredAt(0):
            self.border_color = "orange"

        if self.safe.unlocked:
            self.border_color = "green"

        self.color_widget.setStyleSheet("""
        background: rgba(""" + str(red) + ", " + str(green) + ", " + str(blue) + ", " + str(alpha) + """);
        border: 1px solid """ + self.border_color + """;
        border-radius: 4px;
        """)

        self.value_1.setNum(red)
        self.value_2.setNum(green)
        self.value_3.setNum(blue)
        self.value_4.setNum(alpha)

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        super(ColorMixer, self).closeEvent(event)


def main():
    app = QtGui.QApplication(sys.argv)

    color_mixer = ColorMixer()
    color_mixer.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
