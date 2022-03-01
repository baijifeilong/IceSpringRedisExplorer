# Created by BaiJiFeiLong@gmail.com at 2022/3/1 17:24
import json
import logging

import redis
from PySide2 import QtWidgets, QtCore, QtGui


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._setupView()
        self.statusBar().showMessage("Ready.")

    def _setupView(self):
        self._mainSplitter = QtWidgets.QSplitter()
        self._treeView = QtWidgets.QTreeView()
        self._treeView.setHeaderHidden(True)
        self._treeView.setAlternatingRowColors(True)
        self._treeView.setEditTriggers(QtWidgets.QTreeView.NoEditTriggers)
        self._treeView.clicked.connect(self._refreshNode)
        self._treeView.doubleClicked.connect(self._onTreeViewDoubleClicked)
        self._detailSplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, self._mainSplitter)
        self._mainSplitter.addWidget(self._treeView)
        self._mainSplitter.addWidget(self._detailSplitter)
        self._mainSplitter.setStretchFactor(0, 1)
        self._mainSplitter.setStretchFactor(1, 1)
        self.setCentralWidget(self._mainSplitter)

        self._treeModel = QtGui.QStandardItemModel(self._treeView)
        self._treeView.setModel(self._treeModel)

        self._infoEdit = QtWidgets.QTextEdit("Info", self._detailSplitter)
        self._keyEdit = QtWidgets.QTextEdit("Key", self._detailSplitter)
        self._valueWidget = QtWidgets.QWidget(self._detailSplitter)
        self._detailSplitter.addWidget(self._infoEdit)
        self._detailSplitter.addWidget(self._keyEdit)
        self._detailSplitter.addWidget(self._valueWidget)
        self._detailSplitter.setStretchFactor(0, 1)
        self._detailSplitter.setStretchFactor(1, 1)
        self._detailSplitter.setStretchFactor(2, 2)

        self._valueLayout = QtWidgets.QVBoxLayout(self._valueWidget)
        self._valueLayout.setMargin(0)
        self._valueLayout.setSpacing(0)
        self._valueWidget.setLayout(self._valueLayout)
        self._valueEdit = QtWidgets.QTextEdit("Value", self._detailSplitter)
        self._valueRadioLayout = QtWidgets.QHBoxLayout(self._valueWidget)
        self._valueLayout.addWidget(self._valueEdit)
        self._valueLayout.addLayout(self._valueRadioLayout)
        self._valueAutoRadio = QtWidgets.QRadioButton("Auto", self._valueWidget)
        self._valueAutoRadio.setChecked(True)
        self._valueRawRadio = QtWidgets.QRadioButton("Raw", self._valueWidget)
        self._valueJsonRadio = QtWidgets.QRadioButton("JSON", self._valueWidget)
        self._valueRadioGroup = QtWidgets.QButtonGroup(self._valueLayout)
        self._valueRadioGroup.buttonClicked.connect(self._refreshValue)
        for radio in self._valueAutoRadio, self._valueRawRadio, self._valueJsonRadio:
            self._valueRadioLayout.addWidget(radio)
            self._valueRadioGroup.addButton(radio)
        self._valueRadioLayout.addStretch()

        sources = ["Alpha", "Beta", "Gamma"]
        for source in sources:
            sourceNode = QtGui.QStandardItem(source)
            sourceNode.setData(dict(type="SOURCE", host="localhost", port=6379, password=None), QtCore.Qt.UserRole)
            self._treeModel.invisibleRootItem().appendRow(sourceNode)

        self._treeModel = self._treeModel
        self._treeView = self._treeView
        self._infoEdit = self._infoEdit
        self._valueRadioGroup = self._valueRadioGroup
        self._keyEdit = self._keyEdit
        self._valueEdit = self._valueEdit

    def _onTreeViewDoubleClicked(self, modelIndex: QtCore.QModelIndex):
        clickedNode = self._treeModel.itemFromIndex(modelIndex)
        jd = clickedNode.data(QtCore.Qt.UserRole)
        rds = self._fetchRedisAtNode(modelIndex)
        if jd["type"] == "SOURCE" and not clickedNode.hasChildren():
            for key in rds.info("KEYSPACE"):
                db = int(key[2:])
                childNode = QtGui.QStandardItem(str(db))
                childNode.setData(dict(type="SCHEMA", db=db), QtCore.Qt.UserRole)
                clickedNode.appendRow(childNode)
        if jd["type"] == "SCHEMA" and not clickedNode.hasChildren():
            self._generateChildrenForNode(clickedNode, self._generateTreeDictFromKeys(rds.keys()))
            self._treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)

    @staticmethod
    def _generateTreeDictFromKeys(keys):
        tree = dict()
        for key in map(bytes.decode, keys):
            dkt = tree
            for part in key.split(":"):
                dkt[part] = dkt[part] if part in dkt else dict()
                dkt = dkt[part]
        return tree

    def _generateChildrenForNode(self, node, dkt):
        for k, v in dkt.items():
            parentPath = (node.data(QtCore.Qt.UserRole) or dict()).get("path", b"")
            childPath = f"{parentPath.decode()}:{k}".lstrip(":").encode()
            childNode = QtGui.QStandardItem(k)
            childNode.setData(dict(type="KEY", path=childPath), QtCore.Qt.UserRole)
            node.appendRow(childNode)
            self._generateChildrenForNode(childNode, v)

    def _refreshNode(self, index: QtCore.QModelIndex):
        jd = index.data(QtCore.Qt.UserRole)
        if jd["type"] != "KEY":
            return
        key = jd["path"]
        rds = self._fetchRedisAtNode(index)
        if not rds.exists(key):
            return
        value = rds.get(key)
        ttl = rds.ttl(key)
        self._infoEdit.setText(f"TTL: {ttl}")
        self._infoEdit.setProperty("key", key)
        self._infoEdit.setProperty("value", value)
        self._refreshValue()

    @staticmethod
    def _detectTextFormat(text: str) -> str:
        if text[:1] in '{["':
            return "JSON"
        return "Raw"

    @staticmethod
    def _loadJson(text: str):
        try:
            return json.loads(json.loads(text))
        except TypeError:
            return json.loads(text)

    def _refreshValue(self, ):
        key = self._infoEdit.property("key")
        value = self._infoEdit.property("value")
        type = self._valueRadioGroup.checkedButton().text()
        type = type if type != "Auto" else self._detectTextFormat(value.decode())
        text = json.dumps(self._loadJson(value), indent=4, ensure_ascii=False) if type == "JSON" else value.decode()
        self._keyEdit.setText(key.decode())
        self._valueEdit.setText(text)

    def _fetchRedisAtNode(self, index: QtCore.QModelIndex):
        host, port, password, db = (None, None, None, 0)
        item = self._treeModel.itemFromIndex(index)
        while item is not None:
            host = (item.data(QtCore.Qt.UserRole) or {}).get("host", host)
            port = (item.data(QtCore.Qt.UserRole) or {}).get("port", port)
            password = (item.data(QtCore.Qt.UserRole) or {}).get("password", password)
            db = (item.data(QtCore.Qt.UserRole) or {}).get("db", db)
            item = item.parent()
        assert host and port
        logging.debug("host: %s, port: %s, password: %s, db: %s", host, port, password, db)
        return redis.Redis(host=host, port=port, db=db, password=password)
