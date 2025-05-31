from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QTabWidget, QFileDialog, QMessageBox,
    QMenuBar, QTableWidget, QTableWidgetItem, QSplitter, QWidget, QVBoxLayout,
    QHeaderView,QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
import sys
import os


class SimpleTextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyecto 2 Arquitectura de Computadores")
        self.setGeometry(100, 100, 1200, 700)

        self.open_tabs = {}
        self.untitled_count = 1

        self._create_menu()
        self._create_main_layout()

    def _create_menu(self):
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("File")

        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(self.new_tab)
        file_menu.addAction(new_tab_action)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

    def _create_main_layout(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # --- Panel izquierdo: Editor ---
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_tab)
        self.new_tab()

        # --- Panel central: Registers + Safe ---
        center_panel = QWidget()
        center_layout = QVBoxLayout()
        center_panel.setLayout(center_layout)

        var_label = QLabel("Registers")
        self.variable_table = QTableWidget(16, 2)
        self.variable_table.setHorizontalHeaderLabels(["Name", "Value"])
        self.variable_table.horizontalHeader().setStretchLastSection(True)
        self.variable_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(16):
            name_item = QTableWidgetItem(f"R{i}")
            name_item.setFlags(Qt.ItemIsEnabled)
            value_item = QTableWidgetItem("0")
            self.variable_table.setItem(i, 0, name_item)
            self.variable_table.setItem(i, 1, value_item)

        reg_label = QLabel("Safe")
        self.register_table = QTableWidget(4, 2)
        self.register_table.setHorizontalHeaderLabels(["Name", "Value"])
        self.register_table.horizontalHeader().setStretchLastSection(True)
        self.register_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(4):
            name_item = QTableWidgetItem(f"Key 1{i}")
            name_item.setFlags(Qt.ItemIsEnabled)
            value_item = QTableWidgetItem("0")
            self.register_table.setItem(i, 0, name_item)
            self.register_table.setItem(i, 1, value_item)

        center_layout.addWidget(var_label)
        center_layout.addWidget(self.variable_table)
        center_layout.addWidget(reg_label)
        center_layout.addWidget(self.register_table)

        # --- Panel derecho: Memoria ---
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        memory_label = QLabel("Memoria")
        self.memory_table = QTableWidget(10, 2)
        self.memory_table.setHorizontalHeaderLabels(["Address", "Value"])
        self.memory_table.horizontalHeader().setStretchLastSection(True)
        self.memory_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(10):
            addr_item = QTableWidgetItem(f"{i:02X}")
            addr_item.setFlags(Qt.ItemIsEnabled)
            val_item = QTableWidgetItem("0")
            self.memory_table.setItem(i, 0, addr_item)
            self.memory_table.setItem(i, 1, val_item)

        right_layout.addWidget(memory_label)
        right_layout.addWidget(self.memory_table)

        # --- Splitter principal: Editor | Registers+Safe | Memoria ---
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self.editor_tabs)
        main_splitter.addWidget(center_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(0, 3)  # Editor
        main_splitter.setStretchFactor(1, 2)  # Registers/Safe
        main_splitter.setStretchFactor(2, 2)  # Memoria

        layout = QVBoxLayout()
        layout.addWidget(main_splitter)
        main_widget.setLayout(layout)

    def new_tab(self):
        editor = QTextEdit()
        tab_name = f"untitled {self.untitled_count}"
        self.untitled_count += 1
        self.editor_tabs.addTab(editor, tab_name)
        self.editor_tabs.setCurrentWidget(editor)

    def close_tab(self, index):
        editor = self.editor_tabs.widget(index)
        for path, ed in list(self.open_tabs.items()):
            if ed == editor:
                del self.open_tabs[path]
                break
        self.editor_tabs.removeTab(index)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File")
        if path:
            if path in self.open_tabs:
                index = self.editor_tabs.indexOf(self.open_tabs[path])
                self.editor_tabs.setCurrentIndex(index)
                return

            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    editor = QTextEdit()
                    editor.setPlainText(content)
                    self.editor_tabs.addTab(editor, os.path.basename(path))
                    self.editor_tabs.setCurrentWidget(editor)
                    self.open_tabs[path] = editor
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open file:\n{e}")

    def save_file(self):
        editor = self.editor_tabs.currentWidget()
        for path, ed in self.open_tabs.items():
            if ed == editor:
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(editor.toPlainText())
                        return
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Could not save file:\n{e}")
                    return
        self.save_file_as()

    def save_file_as(self):
        editor = self.editor_tabs.currentWidget()
        path, _ = QFileDialog.getSaveFileName(self, "Save File As")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
                    self.open_tabs[path] = editor
                    self.editor_tabs.setTabText(self.editor_tabs.indexOf(editor), os.path.basename(path))
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not save file:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleTextEditor()
    window.showMaximized()
    sys.exit(app.exec())
