from pathlib import Path
import shutil
from typing import Callable
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *
import os

from editor import Editor


class FileManager(QTreeView):
    def __init__(self, tab_view, set_new_tab=None):
        super(FileManager, self).__init__(None)
        
        self.set_new_tab = set_new_tab
        self.tab_view = tab_view

        self.is_editing = False
        self.edit_done_cb = None
        self.current_edit_index = None

        self.manager_font = QFont("FiraCode", 13)
        
        
        self.model: QFileSystemModel = QFileSystemModel()
        self.model.setRootPath(os.getcwd())
        # File system filters
        self.model.setFilter(
            QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files | QDir.Drives
        )
        self.model.setReadOnly(False)

        ### NEW
        self.setFocusPolicy(Qt.NoFocus)
        self.setFont(self.manager_font)
        self.setModel(self.model)
        self.setRootIndex(self.model.index(os.getcwd()))
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QTreeView.SelectRows)
        self.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        # Add custom context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        # handling click
        self.clicked.connect(self.tree_view_clicked)
        self.setIndentation(10)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Hide header and hide other columns except for name
        self.setHeaderHidden(True)
        self.setColumnHidden(1, True)
        self.setColumnHidden(2, True)
        self.setColumnHidden(3, True)

        # enable drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        

    def tree_view_clicked(self, index: QModelIndex):
        path = self.model.filePath(index)
        f = Path(path)
        self.set_new_tab(f)

    def delete_path(self, path: Path):
        """delete file or folder with path"""
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    def custom_rename(self, index: QModelIndex, callback: Callable[[QModelIndex], None]):
        self.openPersistentEditor(index)
        self.is_editing = True
        self.current_edit_index = index
        self.edit_done_cb = callback


    def show_dialog(self, title, msg) -> int:
        dialog = QMessageBox(self)
        dialog.setFont(self.manager_font)
        dialog.font().setPointSize(14)
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(QIcon(":/icons/close-icon.svg"))
        dialog.setText(msg)
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.No)
        dialog.setIcon(QMessageBox.Warning)
        return dialog.exec_()

    def show_context_menu(self, pos: QPoint):
        """Context menu for tree widget"""
        ix = self.indexAt(pos)
        menu = QMenu()
        menu.addAction("New File")
        menu.addAction("New Folder")
        menu.addAction("Rename")
        menu.addAction("Delete")
        action = menu.exec_(self.viewport().mapToGlobal(pos))

        if ix.column() == 0:
            if action:
                if action.text() == "Rename":
                    prev_name = self.model.fileName(ix)
                    def rename_callback(i):
                        new_name = self.model.fileName(i)
                        if prev_name == new_name:
                            return
                        for editor in self.tab_view.findChildren(Editor):
                            if editor.name == prev_name:
                                editor.name = new_name
                                self.tab_view.setTabText(
                                    self.tab_view.indexOf(editor), new_name
                                )
                                self.tab_view.repaint()
                                editor.full_path = Path(self.model.rootPath()) / new_name
                                self.current_file = Path(editor.full_path)
                                break

                    self.custom_rename(ix, rename_callback)

                elif action.text() == "Delete":
                    # check if selection is more
                    dialog = self.show_dialog(
                        "Delete", "Are you sure you want to delete this file?"
                    )
                    if dialog == QMessageBox.Yes:
                        if self.selectionModel().hasSelection():
                            for i in self.selectionModel().selectedRows():
                                path = Path(self.model.filePath(i))
                                self.delete_path(path)
                                for editor in self.tab_view.findChildren(Editor):
                                    if editor.name == path.name:
                                        self.tab_view.removeTab(
                                            self.tab_view.indexOf(editor)
                                        )
                elif action.text() == "New Folder":
                    # add a new item to tree view model and make it ediable
                    idx = self.model.mkdir(self.rootIndex(), "New Folder")
                    # edit that index
                    self.edit(idx)
                elif action.text() == "New File":
                    # find file with name "file" in tree view
                    f = Path(self.model.rootPath()) / "file"
                    count = 1
                    while f.exists():
                        f = Path(f.parent / f"file{count}")
                        count += 1
                    f.touch()
                    idx = self.model.index(str(f.absolute()))
                    self.edit(idx)

                else:
                    pass


    def keyPressEvent(self, event: QKeyEvent) -> None:
        if self.is_editing:
            self.closePersistentEditor(self.current_edit_index)
            self.is_editing = False
            self.edit_done_cb(self.current_edit_index)
        return super().keyPressEvent(event)

    # item drop
    def dropEvent(self, e: QDropEvent) -> None:
        """Drop event for tree view"""
        root_path = Path(self.model.rootPath())
        if e.mimeData().hasUrls():
            for url in e.mimeData().urls():
                path = Path(url.toLocalFile())
                if path.is_dir():
                    shutil.copytree(path, root_path / path.name)
                else:
                    shutil.copy(path, root_path / path.name)
        e.accept()

        return super().dropEvent(e)

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        """Drag enter event for tree view"""
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()
