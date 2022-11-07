from PyQt5.QtGui import QIcon, QPixmap

# Loads icon from filepath


def load_icon(path: str) -> QIcon:
    icon = QIcon()
    icon.addPixmap(QPixmap(path), QIcon.Normal, QIcon.Off)

    return icon
