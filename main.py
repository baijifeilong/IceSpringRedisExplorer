# Created by BaiJiFeiLong@gmail.com at 2021/12/20 10:56
import logging

import colorlog
import redis
from PySide2 import QtWidgets, QtGui, QtCore


def onDoubleClicked(index: QtCore.QModelIndex):
    key = keys[index.row()]
    value = rds.get(key)
    ttl = rds.ttl(key)
    infoEdit.setText(f"TTL: {ttl}")
    keyEdit.setText(key.decode())
    valueEdit.setText(value.decode())


consoleLogPattern = "%(log_color)s%(asctime)s %(levelname)8s %(name)-10s %(message)s"
logging.getLogger().handlers = [logging.StreamHandler()]
logging.getLogger().handlers[0].setFormatter(colorlog.ColoredFormatter(consoleLogPattern))
logging.getLogger().setLevel(logging.DEBUG)

app = QtWidgets.QApplication()
mainWindow = QtWidgets.QMainWindow()
mainWindow.statusBar().showMessage("Ready.")
mainWindow.resize(800, 600)

mainSplitter = QtWidgets.QSplitter(mainWindow)
treeView = QtWidgets.QTreeView(mainSplitter)
treeView.setEditTriggers(QtWidgets.QTreeView.NoEditTriggers)
treeView.doubleClicked.connect(onDoubleClicked)
detailSplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, mainSplitter)
mainSplitter.addWidget(treeView)
mainSplitter.addWidget(detailSplitter)
mainSplitter.setStretchFactor(0, 1)
mainSplitter.setStretchFactor(1, 1)
mainWindow.setCentralWidget(mainSplitter)

infoEdit = QtWidgets.QTextEdit("Info", detailSplitter)
keyEdit = QtWidgets.QTextEdit("Key", detailSplitter)
valueEdit = QtWidgets.QTextEdit("Value", detailSplitter)
detailSplitter.addWidget(infoEdit)
detailSplitter.addWidget(keyEdit)
detailSplitter.addWidget(valueEdit)
detailSplitter.setStretchFactor(0, 1)
detailSplitter.setStretchFactor(1, 1)
detailSplitter.setStretchFactor(2, 2)

treeModel = QtGui.QStandardItemModel(treeView)
treeModel.setHorizontalHeaderLabels(["Key"])
treeView.setModel(treeModel)

rds = redis.Redis()
keys = rds.keys()
for key in keys:
    treeModel.invisibleRootItem().appendRow(QtGui.QStandardItem(key.decode()))

mainWindow.show()
app.exec_()
