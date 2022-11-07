from typing import Callable
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QObject
from ui.newfilewindow.newfilewindow import Ui_NewFileWindow


class NewFileWindow(QWidget, Ui_NewFileWindow):
    def __init__(self, on_done_callback: Callable, parent: QObject = None) -> None:
        super().__init__(parent)

        self.keep_aspect_ratio = False
        self.aspect_ratio = 1
        self.on_done_callback = on_done_callback

        self.initUI()

    def initUI(self):
        self.setupUi(self)

        self.cancelButton.clicked.connect(self.close)
        self.okButton.clicked.connect(self.handle_done_button_clicked)

        self.keepAspectRatioCheckbox.stateChanged.connect(
            self.enable_keep_aspect_ratio)
        self.widthBox.valueChanged.connect(
            lambda: self.correct_aspect_ratio("height"))
        self.heightBox.valueChanged.connect(
            lambda: self.correct_aspect_ratio("width"))

    def enable_keep_aspect_ratio(self, enabled: bool):
        self.keep_aspect_ratio = enabled

        if enabled:
            self.aspect_ratio = self.widthBox.value() / self.heightBox.value()

    def correct_aspect_ratio(self, characteristic):
        if not self.keep_aspect_ratio:
            return

        if characteristic == "width":
            # To avoid valueChange callback triggering when changing widthBox value ( and avoid
            # cyclic value changing ), we block signals
            self.widthBox.blockSignals(True)
            self.widthBox.setValue(
                int(self.heightBox.value() * self.aspect_ratio))
            self.widthBox.blockSignals(False)
        elif characteristic == "height":
            # To avoid valueChange callback triggering when changing heightBox value ( and avoid
            # cyclic value changing ), we block signals
            self.heightBox.blockSignals(True)
            self.heightBox.setValue(
                int(self.widthBox.value() // self.aspect_ratio))
            self.heightBox.blockSignals(False)

    def handle_done_button_clicked(self):
        self.on_done_callback(self.widthBox.value(), self.heightBox.value())
        self.close()
