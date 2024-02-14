from PyQt5.QtWidgets import (
   QFrame, QHBoxLayout, QLabel, QPushButton, QWidget, QMenu, QAction
)

from PyQt5.QtCore import Qt, QEvent, QSize
from PyQt5.QtGui import QPixmap, QIcon, QImage

class MenuItems(QWidget):

    def __init__(self, main_window) -> None:
        super().__init__(None)
        self.main_window = main_window

        self.is_menu_open = False
        self.lay = QHBoxLayout(self)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(3)


        self.file_label = self.get_lbl("File")
        self.file_label.mousePressEvent = self.mpEvent
        edit_label = self.get_lbl("Edit")

        self.lay.addWidget(self.file_label)
        self.lay.addWidget(edit_label)

    def mpEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = self.file_label.pos()
            pos.setY(pos.y() + 10)
            self.show_file_menu(pos)
        else:
            super().mousePressEvent(event)
            
            
    def show_file_menu(self, pos):
        context_menu = QMenu(self)

        new_file = QAction("New", self)
        new_file.setShortcut("Ctrl+N")
        new_file.triggered.connect(self.main_window.new_file)
        context_menu.addAction(new_file)

        save_file = QAction("Save", self)
        save_file.setShortcut("Ctrl+S")
        save_file.triggered.connect(self.main_window.save_file)
        context_menu.addAction(save_file)

        save_as = QAction("Save As", self)
        save_as.setShortcut("Ctrl+Shift+S")
        save_as.triggered.connect(self.main_window.save_as)
        context_menu.addAction(save_as)

        context_menu.exec_(pos)

    def get_lbl(self, txt):
        lbl = QLabel(txt)
        lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        lbl.setStyleSheet("""
        QLabel {
            font-size: 14px; 
            color: white; 
            margin-right: 10px; 
            border: none;
            border-radius: 5px;
        }
        QLabel::hover {
           background: rgba(255, 255, 255, 0.1);
        }
        """)
        lbl.mousePressEvent = lambda e: self.main_window.menu_clicked(e, txt)
        return lbl



class Heading(QFrame):

    def __init__(self, main_window) -> None:
        super().__init__(None)
        self.main_window = main_window
        self.setFixedHeight(40)
        
        main_layout = QHBoxLayout(self)
        img_logo = QImage(25, 25, QImage.Format.Format_Alpha8)
        img_logo.fill(Qt.GlobalColor.transparent)
        logo = QPixmap.fromImage(img_logo)
        self.title_lbl = QLabel()
        self.title_lbl.setStyleSheet(f"font-family: Arial; font-size: 16px; font-weight: 500; color: white; margin-left: 10px; border: none;") 
        self.title_lbl.setPixmap(logo)
        # main_layout.addWidget(self.title_lbl, alignment=Qt.AlignmentFlag.AlignLeft) 

        menu = MenuItems(self.main_window)
        main_layout.addWidget(menu, alignment=Qt.AlignmentFlag.AlignLeft) 

        self.path_lbl = QLabel("")
        self.path_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: white; margin-right: 10px; border: none;") 
        main_layout.addWidget(self.path_lbl, alignment=Qt.AlignmentFlag.AlignCenter)  

        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(4, 0, 4, 0)
        nav_layout.setSpacing(10)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self._icon_close = QIcon("./src/icons/close_icon.png")
        self._icon_minimize = QIcon("./src/icons/minimize_icon.png")
        self._icon_restore = QIcon("./src/icons/restore_icon.png")   

        self._transparent_bg = "background: transparent; border: none;"

        btn_size = 15

        close_lbl = QPushButton()
        close_lbl.setIcon(self._icon_close)
        close_lbl.setIconSize(QSize(btn_size, btn_size))
        close_lbl.setCursor(Qt.PointingHandCursor)
        close_lbl.clicked.connect(self.main_window.window().close)
        close_lbl.setStyleSheet(self._transparent_bg)


        minimize_lbl = QPushButton()
        minimize_lbl.setIcon(self._icon_minimize)
        minimize_lbl.setIconSize(QSize(btn_size, btn_size))
        minimize_lbl.setCursor(Qt.PointingHandCursor)
        minimize_lbl.clicked.connect(self.main_window.window().showMinimized)
        minimize_lbl.setStyleSheet(self._transparent_bg)
        
        restore_lbl = QPushButton()
        restore_lbl.setIcon(self._icon_restore)
        restore_lbl.setIconSize(QSize(btn_size, btn_size))
        restore_lbl.setCursor(Qt.PointingHandCursor)
        restore_lbl.clicked.connect(self.restore_window)
        restore_lbl.setStyleSheet(self._transparent_bg)
        
        nav_layout.addWidget(minimize_lbl)
        nav_layout.addWidget(restore_lbl)
        nav_layout.addWidget(close_lbl)

        main_layout.addLayout(nav_layout)
             

    def restore_window(self):
        if self.main_window.window().isMaximized():
            self.main_window.window().showNormal() 
            self.main_window.centralWidget().setStyleSheet(self.main_window.frame_stlye)
        else:
            self.main_window.window().showMaximized()   
            self.main_window.centralWidget().setStyleSheet(self.main_window.frame_style_no_border)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseMove:
            if event.buttons() == Qt.LeftButton and self.underMouse():
                # Calculate the movement offset
                delta = event.globalPos() - self.drag_position
                # Move the main window
                self.window().move(delta)

        elif event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton and self.underMouse():
                # Save the current mouse position for later use
                self.drag_position = event.globalPos() - self.window().pos()

        return super().eventFilter(obj, event)