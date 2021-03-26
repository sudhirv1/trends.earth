"""
/***************************************************************************
 LDMP - A QGIS plugin
 This plugin supports monitoring and reporting of land degradation to the UNCCD 
 and in support of the SDG Land Degradation Neutrality (LDN) target.
                              -------------------
        begin                : 2021-02-25
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Conservation International
        email                : trends.earth@conservation.org
 ***************************************************************************/
"""

__author__ = 'Luigi Pirelli / Kartoza'
__date__ = '2021-03-03'

import qgis.core
from functools import partial
from qgis.PyQt.QtCore import (
    QModelIndex,
    Qt,
    QCoreApplication,
    QObject,
    pyqtSignal,
    QRectF,
    QRect,
    QAbstractItemModel,
    QSize
)
from qgis.PyQt.QtWidgets import (
    QStyleOptionViewItem,
    QToolButton,
    QMenu,
    QStyledItemDelegate,
    QItemDelegate,
    QWidget,
    QAction
)
from qgis.PyQt.QtGui import (
    QPainter,
    QIcon
)
from LDMP.models.datasets import (
    Dataset,
    Datasets
)
from LDMP.models.algorithms import AlgorithmDescriptor
from LDMP import __version__, log, tr
from LDMP.gui.WidgetDatasetItem import Ui_WidgetDatasetItem


class DatasetItemDelegate(QStyledItemDelegate):

    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.parent = parent

        # manage activate editing when entering the cell (if editable)
        self.enteredCell = None
        self.parent.entered.connect(self.manageEditing)

    def manageEditing(self, index: QModelIndex):
        # close previous editor
        if index == self.enteredCell:
            return
        else:
            if self.enteredCell:
                self.parent.closePersistentEditor(self.enteredCell)
        self.enteredCell = index

        # do nothing if cell is not editable
        model = index.model()
        flags = model.flags(index)
        if not (flags & Qt.ItemIsEditable):
            return

        # activate editor
        item = model.data(index, Qt.ItemDataRole)
        self.parent.openPersistentEditor(self.enteredCell)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        # get item and manipulate painter basing on idetm data
        model = index.model()
        item = model.data(index, Qt.ItemDataRole)

        # if a Dataset => show custom widget
        if isinstance(item, Dataset):
            # get default widget used to edit data
            editorWidget = self.createEditor(self.parent, option, index)
            editorWidget.setGeometry(option.rect)

            # then grab and paint it
            pixmap = editorWidget.grab()
            del editorWidget
            painter.drawPixmap(option.rect.x(), option.rect.y(), pixmap)
        else:
            super().paint(painter, option, index)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex):
        model = index.model()
        item = model.data(index, Qt.ItemDataRole)

        if isinstance(item, Dataset):
            widget = self.createEditor(None, option, index) # parent swet to none otherwise remain painted in the widget
            size = widget.size()
            del widget
            return size

        return super().sizeHint(option, index)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        # get item and manipulate painter basing on item data
        model = index.model()
        item = model.data(index, Qt.ItemDataRole)
        if isinstance(item, Dataset):
            return DatasetEditorWidget(item, parent=parent)
        else:
            return super().createEditor(parent, option, index)

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        editor.setGeometry(option.rect)

class DatasetEditorWidget(QWidget, Ui_WidgetDatasetItem):

    def __init__(self, dataset: Dataset, parent=None):
        super(DatasetEditorWidget, self).__init__(parent)
        self.setupUi(self)
        self.setAutoFillBackground(True)  # allows hiding background prerendered pixmap
        self.dataset = dataset
        self.pushButtonLoad.clicked.connect(self.load_dataset)
        self.pushButtonDetails.clicked.connect(self.show_details)
        self.pushButtonDelete.clicked.connect(self.delete_dataset)

        self.pushButtonDelete.setIcon(
            QIcon(':/plugins/LDMP/icons/mActionDeleteSelected.svg'))
        self.pushButtonDetails.setIcon(
            QIcon(':/plugins/LDMP/icons/mActionPropertiesWidget.svg'))
        self.pushButtonLoad.setIcon(
            QIcon(':/plugins/LDMP/icons/mActionAddRasterLayer.svg'))

        self.labelDatasetName.setText(self.dataset.name)
        self.labelCreationDate.setText(
            self.dataset.creation_date.strftime('%Y-%m-%d %H:%M:%S'))
        self.labelSourceName.setText(self.dataset.source)
        self.labelRunId.setText(self.dataset.run_id)

    def show_details(self):
        log(f"Details button clicked for dataset {self.dataset.name!r}")

    def load_dataset(self):
        log(f"Load button clicked for dataset {self.dataset.name!r}")

    def delete_dataset(self):
        log(f"Delete button clicked for dataset {self.dataset.name!r}")