#Jordi Lumbreras#
import sys
import matplotlib.pyplot as plt
import pandas as pd

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QLineEdit, QMessageBox, QFormLayout, QDialog, QFileDialog, QGroupBox,
    QMenuBar, QToolBar, QStatusBar, QComboBox, QDateEdit
)
from PyQt6.QtCore import Qt, QSize, QDate
from PyQt6.QtGui import QIcon, QAction


class BibliotecaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestió d'Inventari Biblioteca")
        self.setGeometry(100, 100, 1000, 600)

        # Hoja de estilos
        self.setStyleSheet("""
            /* Fondo de la ventana principal */
            QMainWindow {
                background-color: #eeeeee;  /* Gris muy claro */
                color: #000000;             /* Texto negro por defecto */
            }

            /* Barra de menú */
            QMenuBar {
                background-color: #f0f0f0;  
                color: #000000;
            }
            QMenuBar::item:selected {
                background-color: #4CAF50; 
                color: #ffffff;
            }

            /* Barra de herramientas */
            QToolBar {
                background-color: #f0f0f0; 
                border: 1px solid #cccccc;
                color: #000000;
            }

            /* Cuadros de texto */
            QLineEdit {
                color: #000000;
                background-color: #ffffff;
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }

            /* Botones */
            QPushButton {
                padding: 8px 16px;
                background-color: #4CAF50;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }

            /* Tablas */
            QTableWidget {
                background-color: #ffffff;  /* Fondo blanco */
                color: #000000;             /* Texto negro */
                selection-background-color: #CCE5FF;
                gridline-color: #cccccc;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 4px;
                border: 1px solid #ccc;
                font-weight: bold;
                color: #000000;             /* Texto negro en cabeceras */
            }

            QDialog,
            QMessageBox {
                background-color: #ffffff; /* Fondo blanco */
                color: #000000;           /* Texto negro */
            }

            QDialog QLabel,
            QMessageBox QLabel {
                color: #000000;           /* Asegurarse de que las etiquetas también sean negras */
            }

            /* GroupBox */
            QGroupBox {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                color: #000000;  /* Texto del título en negro */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                background-color: #f0f0f0;
                border-radius: 3px;
                color: #000000;  /* Título del group box en negro */
            }
        """)

        # ---------------- 1) DataFrames ----------------
        # DataFrame para libros
        self.books_df = pd.DataFrame(columns=[
            "Nom", "Autor", "Pàgines", "Gènere", "Sinopsis",
            "Data de publicació", "Edició", "En préstec",
            "Estanteria", "Fila", "Columna",
            "Llogater",
            "Data fi del lloguer"
        ])
        # DataFrame para mobiliario
        self.furniture_df = pd.DataFrame(columns=[
            "Nom",  # e.g. "Cadira", "Ordinador", "Taula", etc.
            "Tipus",  # e.g. "Mobiliari", "Equip informàtic", ...
            "Quantitat",
            "Ubicació"
        ])

        self.initUI()

    def initUI(self):
        # ---------- Menús y ToolBar ---------------------
        self.create_menu_bar()
        self.create_tool_bar()

        # ---------- Widget central y pestañas -----------
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Pestaña 1: Libros
        self.books_tab = QWidget()
        books_layout = QVBoxLayout(self.books_tab)
        self.tab_widget.addTab(self.books_tab, "Llibres")

        # Sección de búsqueda / import / export
        top_group_box = QGroupBox("Cerca i Fitxers (Llibres)")
        top_layout = QHBoxLayout()
        top_group_box.setLayout(top_layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Cerca per nom...")
        self.search_box.textChanged.connect(self.search_books)
        top_layout.addWidget(self.search_box)

        self.import_button = QPushButton("Importar CSV")
        self.import_button.clicked.connect(self.import_csv_books)
        top_layout.addWidget(self.import_button)

        self.export_button = QPushButton("Exportar CSV")
        self.export_button.clicked.connect(self.export_csv_books)
        top_layout.addWidget(self.export_button)

        books_layout.addWidget(top_group_box)

        # Tabla de libros
        self.book_table = QTableWidget()
        # Permitir editar todas las celdas:
        self.book_table.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)
        self.book_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.book_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        books_layout.addWidget(self.book_table)

        # Acciones de libros
        book_actions_group_box = QGroupBox("Accions de Llibres")
        actions_layout = QHBoxLayout()
        book_actions_group_box.setLayout(actions_layout)

        self.add_book_button = QPushButton("Afegir llibre")
        self.add_book_button.clicked.connect(self.add_book)
        actions_layout.addWidget(self.add_book_button)

        self.delete_book_button = QPushButton("Eliminar llibre")
        self.delete_book_button.clicked.connect(self.delete_book)
        actions_layout.addWidget(self.delete_book_button)

        self.view_book_button = QPushButton("Veure fitxa")
        self.view_book_button.clicked.connect(self.view_book_details)
        actions_layout.addWidget(self.view_book_button)

        self.rent_button = QPushButton("Llogar llibre")
        self.rent_button.clicked.connect(self.rent_book_dialog)
        actions_layout.addWidget(self.rent_button)

        self.stats_button = QPushButton("Mètriques i Gràfics")
        self.stats_button.clicked.connect(self.generate_metrics_books)
        actions_layout.addWidget(self.stats_button)

        books_layout.addWidget(book_actions_group_box)

        # Pestaña 2: Mobiliari
        self.furniture_tab = QWidget()
        furniture_layout = QVBoxLayout(self.furniture_tab)
        self.tab_widget.addTab(self.furniture_tab, "Mobiliari")

        # Sección de búsqueda / import / export
        top_group_box_furn = QGroupBox("Cerca i Fitxers (Mobiliari)")
        top_layout_furn = QHBoxLayout()
        top_group_box_furn.setLayout(top_layout_furn)

        self.search_box_furn = QLineEdit()
        self.search_box_furn.setPlaceholderText("Cerca per Nom d'objecte...")
        self.search_box_furn.textChanged.connect(self.search_furniture)
        top_layout_furn.addWidget(self.search_box_furn)

        self.import_button_furn = QPushButton("Importar CSV Mobiliari")
        self.import_button_furn.clicked.connect(self.import_csv_furniture)
        top_layout_furn.addWidget(self.import_button_furn)

        self.export_button_furn = QPushButton("Exportar CSV Mobiliari")
        self.export_button_furn.clicked.connect(self.export_csv_furniture)
        top_layout_furn.addWidget(self.export_button_furn)

        furniture_layout.addWidget(top_group_box_furn)

        # Antoni Catany
        # Tabla mobiliari
        self.furniture_table = QTableWidget()
        self.furniture_table.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)
        self.furniture_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.furniture_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        furniture_layout.addWidget(self.furniture_table)

        # Acciones de mobiliari
        furniture_actions_group_box = QGroupBox("Accions de Mobiliari")
        actions_layout_furn = QHBoxLayout()
        furniture_actions_group_box.setLayout(actions_layout_furn)

        self.add_furniture_button = QPushButton("Afegir ítem")
        self.add_furniture_button.clicked.connect(self.add_furniture_item)
        actions_layout_furn.addWidget(self.add_furniture_button)

        self.delete_furniture_button = QPushButton("Eliminar ítem")
        self.delete_furniture_button.clicked.connect(self.delete_furniture_item)
        actions_layout_furn.addWidget(self.delete_furniture_button)

        self.view_furniture_button = QPushButton("Veure/Editar fitxa")
        self.view_furniture_button.clicked.connect(self.view_furniture_details)
        actions_layout_furn.addWidget(self.view_furniture_button)

        furniture_layout.addWidget(furniture_actions_group_box)

        # Barra de estado
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Llistat de llibres i mobiliari carregat.")

        # Poblamos inicialmente las tablas
        self.update_table_books()
        self.update_table_furniture()

        # Conectamos las señales itemChanged para sincronizar con el DataFrame
        self.book_table.itemChanged.connect(self.on_book_table_item_changed)
        self.furniture_table.itemChanged.connect(self.on_furniture_table_item_changed)

    # ----------------------- MENÚS ----------------------------------------
    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # Menú "Fitxer"
        file_menu = menu_bar.addMenu("Fitxer")

        import_action = QAction("Importar CSV (Llibres)", self)
        import_action.triggered.connect(self.import_csv_books)
        file_menu.addAction(import_action)

        export_action = QAction("Exportar CSV (Llibres)", self)
        export_action.triggered.connect(self.export_csv_books)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Sortir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menú "Ajuda"
        help_menu = menu_bar.addMenu("Ajuda")
        about_action = QAction("Quant a...", self)
        about_action.triggered.connect(self.about_app)
        help_menu.addAction(about_action)

    def create_tool_bar(self):
        tool_bar = QToolBar("Barra d'Eines")
        tool_bar.setIconSize(QSize(16, 16))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tool_bar)

        # Acción de Importar (Llibres)
        import_action = QAction("Importar CSV (Llibres)", self)
        import_action.triggered.connect(self.import_csv_books)
        tool_bar.addAction(import_action)

        # Acción de Exportar (Llibres)
        export_action = QAction("Exportar CSV (Llibres)", self)
        export_action.triggered.connect(self.export_csv_books)
        tool_bar.addAction(export_action)

        tool_bar.addSeparator()

        # Acción de Añadir libro
        add_book_action = QAction("Afegir llibre", self)
        add_book_action.triggered.connect(self.add_book)
        tool_bar.addAction(add_book_action)

    def about_app(self):
        QMessageBox.information(
            self,
            "Quant a aquesta aplicació",
            "Aplicació de gestió d'inventari de biblioteca.\n"
            "Permet gestionar llibres i mobiliari, lloguer de llibres, etc."
        )

    # --------------- LIBROS ---------------------------------------------
    # Importar / Exportar CSV
    def import_csv_books(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecciona un fitxer CSV (Llibres)", "", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                temp_df = pd.read_csv(file_path)
                required_cols = set(self.books_df.columns)
                if not required_cols.issubset(set(temp_df.columns)):
                    QMessageBox.critical(
                        self, "Error",
                        "Les columnes del CSV no coincideixen amb l'estructura esperada."
                    )
                    return
                temp_df = temp_df[list(self.books_df.columns)]
                self.books_df = temp_df.fillna("")
                self.update_table_books()
                QMessageBox.information(self, "Èxit", "Dades de llibres importades correctament!")
                self.statusBar().showMessage(f"Dades de llibres importades des de {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al carregar el fitxer: {str(e)}")

    def export_csv_books(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar fitxer CSV (Llibres)", "", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                self.books_df.to_csv(file_path, index=False)
                QMessageBox.information(self, "Èxit", "Dades de llibres exportades correctament!")
                self.statusBar().showMessage(f"Dades de llibres exportades a {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al guardar el fitxer: {str(e)}")

    def search_books(self):
        search_text = self.search_box.text().strip().lower()
        if not search_text:
            self.update_table_books()
            return
        filtered_df = self.books_df[
            self.books_df["Nom"].astype(str).str.lower().str.contains(search_text, na=False)
        ]
        self.update_table_books(filtered_df)

    def update_table_books(self, df=None):
        """Puebla la tabla de libros con los datos de 'df' (o de self.books_df)."""
        if df is None:
            df = self.books_df

        # Bloqueamos las señales para no disparar 'itemChanged' al rellenar la tabla.
        self.book_table.blockSignals(True)

        self.book_table.setRowCount(len(df))
        self.book_table.setColumnCount(len(df.columns))
        self.book_table.setHorizontalHeaderLabels(df.columns)

        for row in range(len(df)):
            for col in range(len(df.columns)):
                value = str(df.iloc[row, col]) if pd.notna(df.iloc[row, col]) else ""
                self.book_table.setItem(row, col, QTableWidgetItem(value))

        self.book_table.resizeColumnsToContents()
        self.book_table.resizeRowsToContents()

        # Desbloqueamos las señales para que ediciones del usuario sí actualicen el DataFrame.
        self.book_table.blockSignals(False)

    def on_book_table_item_changed(self, item: QTableWidgetItem):
        """Se llama cuando se edita una celda en la tabla de libros, para actualizar self.books_df."""
        row = item.row()
        col = item.column()
        new_value = item.text()
        self.books_df.iat[row, col] = new_value

    def add_book(self):
        new_book = pd.DataFrame([{
            column: "" for column in self.books_df.columns
        }])
        # Por defecto, "En préstec" = "No"
        new_book["En préstec"] = "No"
        self.books_df = pd.concat([self.books_df, new_book], ignore_index=True)
        self.update_table_books()
        QMessageBox.information(self, "Afegit", "S'ha afegit un nou llibre buit a la taula.")
        self.statusBar().showMessage("Nou llibre afegit.")

    def delete_book(self):
        selected_row = self.book_table.currentRow()
        if selected_row >= 0:
            reply = QMessageBox.question(
                self, "Confirmació",
                "Estàs segur que vols eliminar aquest llibre?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.books_df.drop(index=selected_row, inplace=True)
                self.books_df.reset_index(drop=True, inplace=True)
                self.update_table_books()
                self.statusBar().showMessage("Llibre eliminat.")
        else:
            QMessageBox.warning(self, "Atenció", "No s'ha seleccionat cap llibre.")
    # Antoni Catany

    # Jordi Munar
    def view_book_details(self):
        selected_row = self.book_table.currentRow()
        if selected_row >= 0:
            book_data = self.books_df.iloc[selected_row]
            book_dialog = QDialog(self)
            book_dialog.setWindowTitle("Detalls del llibre")
            layout = QFormLayout()

            fields = {}
            for col in self.books_df.columns:
                field = QLineEdit(str(book_data[col]) if pd.notna(book_data[col]) else "")
                layout.addRow(QLabel(col), field)
                fields[col] = field

            save_button = QPushButton("Guardar canvis")

            def save_edits():
                for col, field in fields.items():
                    self.books_df.at[selected_row, col] = field.text()
                self.update_table_books()
                QMessageBox.information(self, "Guardat", "S'han guardat els canvis correctament.")
                book_dialog.accept()

            save_button.clicked.connect(save_edits)
            layout.addWidget(save_button)

            book_dialog.setLayout(layout)
            book_dialog.exec()
        else:
            QMessageBox.warning(self, "Atenció", "No s'ha seleccionat cap llibre.")

    # Pantalla de alquiler (lloguer) de un libro
    def rent_book_dialog(self):
        rent_dialog = QDialog(self)
        rent_dialog.setWindowTitle("Llogar llibre")
        layout = QFormLayout()

        # Campo: Nom del llogater
        llogater_line = QLineEdit()
        layout.addRow(QLabel("Nom del llogater:"), llogater_line)

        # Campo: Llibre que vol llogar (combo con libros NO en préstec)
        available_books = self.books_df[self.books_df["En préstec"] != "Sí"]
        combo_books = QComboBox()
        combo_books.addItem("— Selecciona un llibre —")
        for i, row in available_books.iterrows():
            combo_books.addItem(row["Nom"], i)  # "data" es el índice real
        layout.addRow(QLabel("Llibre a llogar:"), combo_books)

        # Campo: Data de fi del lloguer
        date_end = QDateEdit()
        date_end.setCalendarPopup(True)
        date_end.setDate(QDate.currentDate())
        layout.addRow(QLabel("Data fi del lloguer:"), date_end)

        rent_button = QPushButton("Llogar")

        def do_rent():
            llogater_name = llogater_line.text().strip()
            book_index = combo_books.currentData()  # índice del df
            if not llogater_name or book_index is None:
                QMessageBox.warning(rent_dialog, "Error", "Has d'introduir el nom del llogater i el llibre.")
                return

            # Actualizamos en el DataFrame
            self.books_df.at[book_index, "En préstec"] = "Sí"
            self.books_df.at[book_index, "Llogater"] = llogater_name
            self.books_df.at[book_index, "Data fi del lloguer"] = date_end.date().toString("yyyy-MM-dd")

            self.update_table_books()
            QMessageBox.information(rent_dialog, "Èxit", "El llibre ha estat llogat correctament!")
            self.statusBar().showMessage("Llibre llogat.")
            rent_dialog.accept()

        rent_button.clicked.connect(do_rent)
        layout.addWidget(rent_button)

        rent_dialog.setLayout(layout)
        rent_dialog.exec()

    def generate_metrics_books(self):
        if self.books_df.empty:
            QMessageBox.warning(self, "Advertència", "No hi ha dades disponibles per generar gràfics.")
            return

        genre_counts = self.books_df["Gènere"].value_counts()

        plt.figure(figsize=(8, 5))
        plt.bar(genre_counts.index, genre_counts.values, color="#4CAF50")
        plt.xlabel("Gènere")
        plt.ylabel("Nombre de llibres")
        plt.title("Distribució de llibres per gènere")
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Guardar gráfico localmente
        save_path, _ = QFileDialog.getSaveFileName(self, "Desar gràfic", "", "PNG Files (*.png)")
        if save_path:
            plt.savefig(save_path)
            QMessageBox.information(self, "Èxit", f"Gràfic desat a {save_path}.")

        plt.show()

    # --------------- MOBILIARI -------------------------------------------
    def import_csv_furniture(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecciona un fitxer CSV (Mobiliari)", "", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                temp_df = pd.read_csv(file_path)
                required_cols = set(self.furniture_df.columns)
                if not required_cols.issubset(set(temp_df.columns)):
                    QMessageBox.critical(
                        self, "Error",
                        "Les columnes del CSV de mobiliari no coincideixen amb l'estructura esperada."
                    )
                    return
                temp_df = temp_df[list(self.furniture_df.columns)]
                self.furniture_df = temp_df.fillna("")
                self.update_table_furniture()
                QMessageBox.information(self, "Èxit", "Dades de mobiliari importades correctament!")
                self.statusBar().showMessage(f"Dades de mobiliari importades des de {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al carregar el fitxer: {str(e)}")

    def export_csv_furniture(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar fitxer CSV (Mobiliari)", "", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                self.furniture_df.to_csv(file_path, index=False)
                QMessageBox.information(self, "Èxit", "Dades de mobiliari exportades correctament!")
                self.statusBar().showMessage(f"Dades de mobiliari exportades a {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al guardar el fitxer: {str(e)}")

    def search_furniture(self):
        search_text = self.search_box_furn.text().strip().lower()
        if not search_text:
            self.update_table_furniture()
            return
        filtered_df = self.furniture_df[
            self.furniture_df["Nom"].astype(str).str.lower().str.contains(search_text, na=False)
        ]
        self.update_table_furniture(filtered_df)

    def update_table_furniture(self, df=None):
        """Puebla la tabla de mobiliario con los datos de 'df' (o de self.furniture_df)."""
        if df is None:
            df = self.furniture_df

        # Bloqueamos la señal antes de poblar la tabla
        self.furniture_table.blockSignals(True)

        self.furniture_table.setRowCount(len(df))
        self.furniture_table.setColumnCount(len(df.columns))
        self.furniture_table.setHorizontalHeaderLabels(df.columns)

        for row in range(len(df)):
            for col in range(len(df.columns)):
                value = str(df.iloc[row, col]) if pd.notna(df.iloc[row, col]) else ""
                self.furniture_table.setItem(row, col, QTableWidgetItem(value))

        self.furniture_table.resizeColumnsToContents()
        self.furniture_table.resizeRowsToContents()

        # Desbloqueamos la señal
        self.furniture_table.blockSignals(False)

    def on_furniture_table_item_changed(self, item: QTableWidgetItem):
        """Se llama cuando se edita una celda en la tabla de mobiliario, para actualizar self.furniture_df."""
        row = item.row()
        col = item.column()
        new_value = item.text()
        self.furniture_df.iat[row, col] = new_value

    def add_furniture_item(self):
        new_item = pd.DataFrame([{
            column: "" for column in self.furniture_df.columns
        }])
        self.furniture_df = pd.concat([self.furniture_df, new_item], ignore_index=True)
        self.update_table_furniture()
        QMessageBox.information(self, "Afegit", "S'ha afegit un nou ítem de mobiliari.")
        self.statusBar().showMessage("Nou mobiliari afegit.")

    def delete_furniture_item(self):
        selected_row = self.furniture_table.currentRow()
        if selected_row >= 0:
            reply = QMessageBox.question(
                self, "Confirmació",
                "Estàs segur que vols eliminar aquest ítem de mobiliari?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.furniture_df.drop(index=selected_row, inplace=True)
                self.furniture_df.reset_index(drop=True, inplace=True)
                self.update_table_furniture()
                self.statusBar().showMessage("Ítem de mobiliari eliminat.")
        else:
            QMessageBox.warning(self, "Atenció", "No s'ha seleccionat cap ítem de mobiliari.")

    def view_furniture_details(self):
        selected_row = self.furniture_table.currentRow()
        if selected_row >= 0:
            data = self.furniture_df.iloc[selected_row]
            dialog = QDialog(self)
            dialog.setWindowTitle("Detalls de Mobiliari")
            layout = QFormLayout()

            fields = {}
            for col in self.furniture_df.columns:
                field = QLineEdit(str(data[col]) if pd.notna(data[col]) else "")
                layout.addRow(QLabel(col), field)
                fields[col] = field

            save_button = QPushButton("Guardar canvis")

            def save_changes():
                for col, field in fields.items():
                    self.furniture_df.at[selected_row, col] = field.text()
                self.update_table_furniture()
                dialog.accept()
                QMessageBox.information(self, "Guardat", "S'han guardat els canvis correctament.")

            save_button.clicked.connect(save_changes)
            layout.addWidget(save_button)

            dialog.setLayout(layout)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Atenció", "No s'ha seleccionat cap element de mobiliari.")

    # --------------- GENERAL ---------------------------------------------
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Confirmació",
            "Segur que vols sortir de l'aplicació?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BibliotecaApp()
    window.show()
    sys.exit(app.exec())

# Jordi Munar