# Created by BaiJiFeiLong@gmail.com at 2021/12/20 10:56
import json
import logging

import colorlog
import redis
from PySide2 import QtWidgets, QtGui, QtCore


def refreshNode(index: QtCore.QModelIndex):
    key = index.data().encode()
    value = rds.get(key)
    ttl = rds.ttl(key)
    infoEdit.setText(f"TTL: {ttl}")
    infoEdit.setProperty("key", key)
    infoEdit.setProperty("value", value)
    refreshValue()


def detectType(text: str) -> str:
    if text.startswith("{") or text.startswith("["):
        return "JSON"
    return "Raw"


def refreshValue():
    key = infoEdit.property("key")
    value = infoEdit.property("value")
    type = valueRadioGroup.checkedButton().text()
    type = type if type != "Auto" else detectType(value.decode())
    text = json.dumps(json.loads(value), indent=4, ensure_ascii=False) if type == "JSON" else value.decode()
    keyEdit.setText(key.decode())
    valueEdit.setText(text)


pattern = "%(log_color)s%(asctime)s %(levelname)8s %(name)-10s %(message)s"
logging.getLogger().handlers = [logging.StreamHandler()]
logging.getLogger().handlers[0].setFormatter(colorlog.ColoredFormatter(pattern))
logging.getLogger().setLevel(logging.DEBUG)

app = QtWidgets.QApplication()
font = app.font()
font.setPointSize(12)
app.setFont(font)
mainWindow = QtWidgets.QMainWindow()
mainWindow.statusBar().showMessage("Ready.")
mainWindow.resize(1280, 720)

mainSplitter = QtWidgets.QSplitter(mainWindow)
treeView = QtWidgets.QTreeView(mainSplitter)
treeView.setAlternatingRowColors(True)
treeView.setEditTriggers(QtWidgets.QTreeView.NoEditTriggers)
treeView.doubleClicked.connect(refreshNode)
detailSplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, mainSplitter)
mainSplitter.addWidget(treeView)
mainSplitter.addWidget(detailSplitter)
mainSplitter.setStretchFactor(0, 1)
mainSplitter.setStretchFactor(1, 1)
mainWindow.setCentralWidget(mainSplitter)

infoEdit = QtWidgets.QTextEdit("Info", detailSplitter)
keyEdit = QtWidgets.QTextEdit("Key", detailSplitter)
valueWidget = QtWidgets.QWidget(detailSplitter)
detailSplitter.addWidget(infoEdit)
detailSplitter.addWidget(keyEdit)
detailSplitter.addWidget(valueWidget)
detailSplitter.setStretchFactor(0, 1)
detailSplitter.setStretchFactor(1, 1)
detailSplitter.setStretchFactor(2, 2)

valueLayout = QtWidgets.QVBoxLayout(valueWidget)
valueLayout.setMargin(0)
valueLayout.setSpacing(0)
valueWidget.setLayout(valueLayout)
valueEdit = QtWidgets.QTextEdit("Value", detailSplitter)
valueRadioLayout = QtWidgets.QHBoxLayout(valueWidget)
valueLayout.addWidget(valueEdit)
valueLayout.addLayout(valueRadioLayout)
valueAutoRadio = QtWidgets.QRadioButton("Auto", valueWidget)
valueAutoRadio.setChecked(True)
valueRawRadio = QtWidgets.QRadioButton("Raw", valueWidget)
valueJsonRadio = QtWidgets.QRadioButton("JSON", valueWidget)
valueRadioGroup = QtWidgets.QButtonGroup(valueLayout)
valueRadioGroup.buttonClicked.connect(refreshValue)
for radio in valueAutoRadio, valueRawRadio, valueJsonRadio:
    valueRadioLayout.addWidget(radio)
    valueRadioGroup.addButton(radio)
valueRadioLayout.addStretch()

treeModel = QtGui.QStandardItemModel(treeView)
treeModel.setHorizontalHeaderLabels(["Key"])
treeView.setModel(treeModel)

rds = redis.Redis()
keys = rds.keys()
for key in keys:
    treeModel.invisibleRootItem().appendRow(QtGui.QStandardItem(key.decode()))
treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)

mainWindow.show()
app.exec_()
