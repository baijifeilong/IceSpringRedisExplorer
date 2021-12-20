# Created by BaiJiFeiLong@gmail.com at 2021/12/20 10:56
import json
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
    valueEdit.setProperty("raw", value)
    valueEdit.setText(value.decode())


def onRefreshValue():
    raw = valueEdit.property("raw")
    type = valueRadioGroup.checkedButton().text()
    text = json.dumps(json.loads(raw), indent=4, ensure_ascii=False) if type == "JSON" else raw.decode()
    valueEdit.setText(text)


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
valueRadioGroup.buttonClicked.connect(onRefreshValue)
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

mainWindow.show()
app.exec_()
