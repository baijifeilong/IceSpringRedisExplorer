# Created by BaiJiFeiLong@gmail.com at 2021/12/20 10:56
import json
import logging
import sys
from sys import excepthook

import colorlog
import redis
from PySide2 import QtWidgets, QtGui, QtCore


def myExceptHook(*args):
    logging.error("Exception occurred: %s", args[1])
    excepthook(*args)
    QtWidgets.QMessageBox.warning(QtWidgets.QApplication.activeWindow(), "Exception", str(args[1]))


sys.excepthook = myExceptHook
pattern = "%(log_color)s%(asctime)s %(levelname)8s %(name)-10s %(message)s"
logging.getLogger().handlers = [logging.StreamHandler()]
logging.getLogger().handlers[0].setFormatter(colorlog.ColoredFormatter(pattern))
logging.getLogger().setLevel(logging.DEBUG)

app = QtWidgets.QApplication()
app.setApplicationName("Ice Spring Redis Explorer")
font = app.font()
font.setPointSize(12)
app.setFont(font)
mainWindow = QtWidgets.QMainWindow()
mainWindow.statusBar().showMessage("Ready.")
mainWindow.resize(1280, 720)
mainWindow.show()

mainSplitter = QtWidgets.QSplitter(mainWindow)
treeView = QtWidgets.QTreeView(mainSplitter)
treeView.setHeaderHidden(True)
treeView.setAlternatingRowColors(True)
treeView.setEditTriggers(QtWidgets.QTreeView.NoEditTriggers)
treeView.clicked.connect(lambda *args: refreshNode(*args))
treeView.doubleClicked.connect(lambda *args: onTreeViewDoubleClicked(*args))
detailSplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, mainSplitter)
mainSplitter.addWidget(treeView)
mainSplitter.addWidget(detailSplitter)
mainSplitter.setStretchFactor(0, 1)
mainSplitter.setStretchFactor(1, 1)
mainWindow.setCentralWidget(mainSplitter)

treeModel = QtGui.QStandardItemModel(treeView)
treeView.setModel(treeModel)

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
valueRadioGroup.buttonClicked.connect(lambda: refreshValue())
for radio in valueAutoRadio, valueRawRadio, valueJsonRadio:
    valueRadioLayout.addWidget(radio)
    valueRadioGroup.addButton(radio)
valueRadioLayout.addStretch()

sources = ["Alpha", "Beta", "Gamma"]
for source in sources:
    sourceNode = QtGui.QStandardItem(source)
    sourceNode.setData(dict(type="SOURCE", host="localhost", port=6379, password=None), QtCore.Qt.UserRole)
    treeModel.invisibleRootItem().appendRow(sourceNode)


def onTreeViewDoubleClicked(modelIndex: QtCore.QModelIndex):
    clickedNode = treeModel.itemFromIndex(modelIndex)
    jd = clickedNode.data(QtCore.Qt.UserRole)
    rds = fetchRedisAtNode(modelIndex)
    if jd["type"] == "SOURCE" and not clickedNode.hasChildren():
        for key in rds.info("KEYSPACE"):
            db = int(key[2:])
            childNode = QtGui.QStandardItem(str(db))
            childNode.setData(dict(type="SCHEMA", db=db), QtCore.Qt.UserRole)
            clickedNode.appendRow(childNode)
    if jd["type"] == "SCHEMA" and not clickedNode.hasChildren():
        generateChildrenForNode(clickedNode, generateTreeDictFromKeys(rds.keys()))
        treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)


def generateTreeDictFromKeys(keys):
    tree = dict()
    for key in map(bytes.decode, keys):
        dkt = tree
        for part in key.split(":"):
            dkt[part] = dkt[part] if part in dkt else dict()
            dkt = dkt[part]
    return tree


def generateChildrenForNode(node, dkt):
    for k, v in dkt.items():
        parentPath = (node.data(QtCore.Qt.UserRole) or dict()).get("path", b"")
        childPath = f"{parentPath.decode()}:{k}".lstrip(":").encode()
        childNode = QtGui.QStandardItem(k)
        childNode.setData(dict(type="KEY", path=childPath), QtCore.Qt.UserRole)
        node.appendRow(childNode)
        generateChildrenForNode(childNode, v)


def refreshNode(index: QtCore.QModelIndex):
    jd = index.data(QtCore.Qt.UserRole)
    if jd["type"] != "KEY":
        return
    key = jd["path"]
    rds = fetchRedisAtNode(index)
    if not rds.exists(key):
        return
    value = rds.get(key)
    ttl = rds.ttl(key)
    infoEdit.setText(f"TTL: {ttl}")
    infoEdit.setProperty("key", key)
    infoEdit.setProperty("value", value)
    refreshValue()


def detectTextFormat(text: str) -> str:
    if text[:1] in '{["':
        return "JSON"
    return "Raw"


def loadJson(text: str):
    try:
        return json.loads(json.loads(text))
    except TypeError:
        return json.loads(text)


def refreshValue():
    key = infoEdit.property("key")
    value = infoEdit.property("value")
    type = valueRadioGroup.checkedButton().text()
    type = type if type != "Auto" else detectTextFormat(value.decode())
    text = json.dumps(loadJson(value), indent=4, ensure_ascii=False) if type == "JSON" else value.decode()
    keyEdit.setText(key.decode())
    valueEdit.setText(text)


def fetchRedisAtNode(index: QtCore.QModelIndex):
    host, port, password, db = (None, None, None, 0)
    item = treeModel.itemFromIndex(index)
    while item is not None:
        host = (item.data(QtCore.Qt.UserRole) or {}).get("host", host)
        port = (item.data(QtCore.Qt.UserRole) or {}).get("port", port)
        password = (item.data(QtCore.Qt.UserRole) or {}).get("password", password)
        db = (item.data(QtCore.Qt.UserRole) or {}).get("db", db)
        item = item.parent()
    assert host and port
    logging.debug("host: %s, port: %s, password: %s, db: %s", host, port, password, db)
    return redis.Redis(host=host, port=port, db=db, password=password)


app.exec_()
