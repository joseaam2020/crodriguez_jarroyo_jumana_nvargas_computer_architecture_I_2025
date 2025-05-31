from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QTabWidget, QFileDialog, QMessageBox,
    QMenuBar, QTableWidget, QTableWidgetItem, QSplitter, QWidget, QVBoxLayout,
    QHeaderView, QLabel, QHBoxLayout, QPushButton, QToolBar
)
from PySide6.QtCore import (Qt,QRegularExpression)
from PySide6.QtGui import (QAction, QTextCharFormat, QFont, QSyntaxHighlighter, 
                          QColor, QTextDocument)
import sys
import os

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Palabras clave a resaltar
        keywords = [
            "LOOP", "SAXS", "ADD", "SUB", "MUL", "DIV", 
            "OR", "AND", "XOR", "SHRL", "SHLL", 
            "LOAD", "STOR", "STK", "DLT"
        ]
        
        # Formato para palabras clave
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(200, 120, 50))  # Color naranja
        keyword_format.setFontWeight(QFont.Bold)
        
        # Formato para registros (R0-R15)
        register_format = QTextCharFormat()
        register_format.setForeground(QColor(0, 100, 200))  # Color azul
        register_format.setFontWeight(QFont.Bold)

        # Formato para comentarios 
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(150, 150, 150))  # Gris medio
        comment_format.setFontItalic(True)  # Texto en cursiva
        
        # Crear reglas para cada palabra clave (mayúsculas y minúsculas)
        for word in keywords:
            pattern = QRegularExpression(r"\b" + word + r"\b", 
                                       QRegularExpression.CaseInsensitiveOption)
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Regla para registros R0-R15 (insensible a mayúsculas/minúsculas)
        register_pattern = QRegularExpression(
            r"\bR(?:[0-9]|1[0-5])\b", 
            QRegularExpression.CaseInsensitiveOption
        )
        self.highlighting_rules.append((register_pattern, register_format))

         # Regla para comentarios (// hasta fin de línea)
        comment_pattern = QRegularExpression(
            r"//[^\n]*", 
            QRegularExpression.CaseInsensitiveOption
        )
        self.highlighting_rules.append((comment_pattern, comment_format))
    
    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), 
                             match.capturedLength(), 
                             format)

class SimpleTextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyecto 2 Arquitectura de Computadores")
        self.setGeometry(100, 100, 1200, 700)

        self.open_tabs = {}
        self.untitled_count = 1

        self._create_menu()
        self._create_toolbar()
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

    def _create_toolbar(self):
        # Crear una barra de herramientas en la parte superior derecha
        self.toolbar = QToolBar("Control Buttons")
    
        # Botón Run
        run_action = QAction("Run", self)
        run_action.triggered.connect(self.run_code)
        self.toolbar.addAction(run_action)
    
        # Botón Step
        step_action = QAction("Step", self)
        step_action.triggered.connect(self.step_code)
        self.toolbar.addAction(step_action)
        
        # Botón Reset
        reset_action = QAction("Reset", self)
        reset_action.triggered.connect(self.reset_simulation)
        self.toolbar.addAction(reset_action)
        
        # Alinear la barra de herramientas a la derecha
        self.toolbar.setStyleSheet("QToolBar { spacing: 5px; }")
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)  # Corregido aquí 

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

        SyntaxHighlighter(editor.document())

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
                    SyntaxHighlighter(editor.document())

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

    def run_code(self):
        # Implementar la lógica para ejecutar el código
        print("Ejecutando código...")
        QMessageBox.information(self, "Run", "Ejecutando el código completo")

    def step_code(self):
        # Implementar la lógica para ejecutar paso a paso
        print("Ejecutando paso a paso...")
        QMessageBox.information(self, "Step", "Ejecutando instrucción paso a paso")

    def reset_simulation(self):
        # Implementar la lógica para reiniciar la simulación
        print("Reiniciando simulación...")
        QMessageBox.information(self, "Reset", "Reiniciando la simulación")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleTextEditor()
    window.showMaximized()
    sys.exit(app.exec())