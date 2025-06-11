from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QTabWidget, QFileDialog, QMessageBox,
    QMenuBar, QTableWidget, QTableWidgetItem, QSplitter, QWidget, QVBoxLayout,
    QHeaderView, QLabel, QHBoxLayout, QPushButton, QToolBar, QComboBox
)
from PySide6.QtCore import (Qt,QRegularExpression)
from PySide6.QtGui import (QAction, QTextCharFormat, QFont, QSyntaxHighlighter, 
                          QColor, QTextDocument)
import sys
import os
from Pipeline import Pipeline_marcador
from traductor import ensamblar

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

        self.display_format = 'hex'

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

    def update_register_table(self, register_values):
        """Actualiza la tabla de registros con los valores del pipeline"""
        for i in range(16):
            value_item = self.variable_table.item(i, 1)
            value_item.setText(self.format_value(register_values[i]))

    def update_safe_table(self, safe_values):
        """Actualiza la tabla del safe con los valores del pipeline"""
        for i in range(4):
            value_item = self.register_table.item(i, 1)
            value_item.setText(self.format_value(safe_values[i]))

    def update_memory_table(self, memory_values):
        """Actualiza la tabla de memoria con los valores del pipeline"""
        for i, value in enumerate(memory_values):
            val_item = self.memory_table.item(i, 1)
            val_item.setText(self.format_value(value))

    def load_data_file(self):
        """Permite al usuario seleccionar un archivo de datos para cargar en memoria"""
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Data File", 
            "", 
            "All Files (*)"  # Cambiado para aceptar cualquier tipo de archivo
        )
        
        if path:
            self.data_file_path = path  # Guardamos la ruta para usarla luego
            QMessageBox.information(
                self, 
                "Data File Loaded", 
                f"Archivo de datos cargado:\n{os.path.basename(path)}"
            )
    
    def load_key_file(self):
        """Permite al usuario seleccionar un archivo de datos para cargar en memoria"""
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Data File", 
            "", 
            "All Files (*)"  # Cambiado para aceptar cualquier tipo de archivo
        )
        
        if path:
            self.key_file_path = path  # Guardamos la ruta para usarla luego
            QMessageBox.information(
                self, 
                "Key File Loaded", 
                f"Archivo de datos cargado:\n{os.path.basename(path)}"
            )

    def _create_toolbar(self):
        # Crear una barra de herramientas en la parte superior derecha
        self.toolbar = QToolBar("Control Buttons")

        # Selector de formato de visualización
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Hexadecimal", "Decimal", "Binario"])
        self.format_combo.setCurrentText("Hexadecimal")
        self.format_combo.currentTextChanged.connect(self.change_display_format)
        self.toolbar.addWidget(self.format_combo)

        # Botón Load Data
        load_data_action = QAction("Load Data", self)
        load_data_action.triggered.connect(self.load_data_file)
        self.toolbar.addAction(load_data_action)

        # Botón Load Key
        load_key_action = QAction("Load Key", self)
        load_key_action.triggered.connect(self.load_key_file)
        self.toolbar.addAction(load_key_action)
    
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

        # Botón Save Encrypted
        save_enc_action = QAction("Save Encrypted", self)
        save_enc_action.triggered.connect(self.save_encrypted_file)
        self.toolbar.addAction(save_enc_action)
        
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
            name_item = QTableWidgetItem(f"Key {i}")
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

        memory_label = QLabel("Memory")
        self.memory_table = QTableWidget(4096, 2)  # Mostrar todas las 4096 posiciones
        self.memory_table.setHorizontalHeaderLabels(["Address", "Value"])
        self.memory_table.horizontalHeader().setStretchLastSection(True)
        self.memory_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Configurar scroll para mejorar rendimiento con tantas filas
        self.memory_table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        
        for i in range(4096):
            addr_item = QTableWidgetItem(f"{i:04X}")  # Mostrar dirección en hexadecimal
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
    
    def change_display_format(self, format_text):
        """Cambia el formato de visualización de los valores"""
        format_map = {
            "Hexadecimal": "hex",
            "Decimal": "dec",
            "Binario": "bin"
        }
        self.display_format = format_map.get(format_text, "hex")
        # Actualizamos las tablas para reflejar el nuevo formato
        if hasattr(self, 'sb'):
            self.update_register_table(self.sb.registros.regs)
            self.update_safe_table(self.sb.safe.keys)
            memory_values = [self.sb.memory.data_mem.read(i) for i in range(4096)]
            self.update_memory_table(memory_values)

    def format_value(self, value):
        """Formatea un valor según el formato seleccionado"""
        try:
            int_value = int(value)  # Asegurarnos de que es un número entero
            if self.display_format == 'hex':
                return f"0x{int_value:08X}"
            elif self.display_format == 'bin':
                return f"0b{int_value:032b}"
            else:  # decimal
                return str(int_value)
        except (ValueError, TypeError):
            return str(value)  # Si no se puede convertir, devolver el valor original

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
    
    def save_encrypted_file(self):
        if not hasattr(self, 'sb') or not hasattr(self, 'data_file_path'):
            QMessageBox.warning(self, "Error", "No hay datos encriptados para guardar o no se cargó archivo original")
            return
        
        try:
            # Obtener el nombre del archivo original y añadir .enc
            original_path = self.data_file_path
            enc_path = os.path.splitext(original_path)[0] + ".enc"
            
            # Obtener el tamaño original del archivo
            original_size = os.path.getsize(original_path)
            
            # Leer datos encriptados de la memoria
            encrypted_data = bytearray()
            for i in range(0, original_size, 4):
                # Leer palabra de 4 bytes de la memoria
                word = self.sb.memory.data_mem.read((i // 4) + 4, True)  # +4 para saltar el header
                # Convertir a bytes (little-endian) y truncar si es el último bloque
                word_bytes = word.to_bytes(4, byteorder='little')
                remaining_bytes = original_size - i
                encrypted_data.extend(word_bytes[:remaining_bytes])
            
            # Escribir el archivo .enc
            with open(enc_path, 'wb') as f:
                f.write(encrypted_data)
            
            QMessageBox.information(self, "Éxito", f"Archivo encriptado guardado como:\n{enc_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo encriptado:\n{e}")

    def run_code(self):
        editor = self.editor_tabs.currentWidget()
        if editor is None:
            QMessageBox.warning(self, "Error", "No hay ningún editor abierto.")
            return
        
        # Verificar si el archivo está guardado
        current_path = None
        for path, ed in self.open_tabs.items():
            if ed == editor:
                current_path = path
                break
        
        if current_path is None:
            reply = QMessageBox.question(self, 'Archivo no guardado',
                                    "El archivo no está guardado. ¿Desea guardarlo ahora?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
            if reply == QMessageBox.Yes:
                self.save_file_as()
                for path, ed in self.open_tabs.items():
                    if ed == editor:
                        current_path = path
                        break
                if current_path is None:
                    QMessageBox.warning(self, "Error", "Debe guardar el archivo primero.")
                    return
            else:
                QMessageBox.warning(self, "Error", "Debe guardar el archivo primero.")
                return
        
        try:
            ensamblar(current_path, "Proyecto_arqui/procesador/salida.txt")

            # Usamos el archivo de datos si se ha seleccionado uno, sino None
            data_file = getattr(self, 'data_file_path', None)
            key_file = getattr(self, 'key_file_path', None)
            
            sb = Pipeline_marcador("salida.txt", data_file, key_file)

            # Ejecutamos todas las instrucciones
            while not sb.done():
                sb.tick()
                
                # Actualizamos la interfaz después de cada ciclo
                self.update_register_table(sb.registros.regs)
                self.update_safe_table(sb.safe.keys)
                
                # Actualizamos la memoria (primeras 10 posiciones)
                memory_values = [int(sb.memory.data_mem.read(i, True)) for i in range(4096)]
                self.update_memory_table(memory_values)
                
                # Forzamos la actualización de la interfaz
                QApplication.processEvents()

            QMessageBox.information(self, "Éxito", "Ejecución completada")

            if hasattr(self, 'data_file_path'):
                reply = QMessageBox.question(
                    self, 
                    'Guardar encriptado',
                    "¿Desea guardar el archivo encriptado?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.save_encrypted_file()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{e}")

    def step_code(self):
        if not hasattr(self, 'sb') or self.sb.done():
            # Si no hay simulación o ya terminó, comenzar una nueva
            editor = self.editor_tabs.currentWidget()
            if editor is None:
                QMessageBox.warning(self, "Error", "No hay ningún editor abierto.")
                return
            
            current_path = None
            for path, ed in self.open_tabs.items():
                if ed == editor:
                    current_path = path
                    break
            
            if current_path is None:
                QMessageBox.warning(self, "Error", "Debe guardar el archivo primero.")
                return
            
            try:
                ensamblar(current_path, "Proyecto_arqui/procesador/salida.txt")
                data_file = getattr(self, 'data_file_path', None)
                key_file = getattr(self, 'key_file_path', None)

                self.sb = Pipeline_marcador("salida.txt", data_file, key_file)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{e}")
                return
        
        # Ejecutar un solo paso
        if not self.sb.done():
            self.sb.tick()
            
            # Actualizamos la interfaz después de cada ciclo
            self.update_register_table(self.sb.registros.regs)
            self.update_safe_table(self.sb.safe.keys)
                
            # Actualizamos la memoria (primeras 10 posiciones)
            memory_values = [int(self.sb.memory.data_mem.read(i, True)) for i in range(4096)]
            self.update_memory_table(memory_values)
            
            if self.sb.done():
                QMessageBox.information(self, "Fin", "Ejecución completada")

    def reset_simulation(self):
        if hasattr(self, 'sb'):
            del self.sb
        
        # Resetear las tablas a cero
        self.update_register_table([0]*16)
        self.update_safe_table([0]*4)
        self.update_memory_table([0]*10)
        
        QMessageBox.information(self, "Reset", "Simulación reiniciada")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleTextEditor()
    window.showMaximized()
    sys.exit(app.exec())