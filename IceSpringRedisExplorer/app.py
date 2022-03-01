# Created by BaiJiFeiLong@gmail.com at 2022/3/1 17:22

import logging
import sys
from sys import excepthook

import colorlog
from PySide2 import QtWidgets

from IceSpringRedisExplorer.mainWindow import MainWindow


class App(QtWidgets.QApplication):
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger("app")
        self._initLogging()
        self._initExceptionHandler()
        self._initStyles()
        self.setApplicationName("Ice Spring Redis Explorer")
        self._mainWindow = MainWindow()

    def run(self):
        self._mainWindow.resize(1280, 720)
        self._mainWindow.show()
        self.exec_()

    @staticmethod
    def _initLogging():
        pattern = "%(log_color)s%(asctime)s %(levelname)8s %(name)-10s %(message)s"
        logging.getLogger().handlers = [logging.StreamHandler()]
        logging.getLogger().handlers[0].setFormatter(colorlog.ColoredFormatter(pattern))
        logging.getLogger().setLevel(logging.DEBUG)

    def _initExceptionHandler(self):
        sys.excepthook = self._exceptionHook

    def _exceptionHook(self, *args):
        self._logger.error("Exception occurred: %s", args[1])
        excepthook(*args)
        QtWidgets.QMessageBox.warning(self.activeWindow(), "Exception", str(args[1]))

    def _initStyles(self):
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)
