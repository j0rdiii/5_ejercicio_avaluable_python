import sys
import matplotlib.pyplot as plt
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget,
    QLineEdit, QMessageBox, QFormLayout, QDialog, QTableWidgetItem, QFileDialog
)


class BibliotecaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestió d'Inventari Biblioteca")
        self.setGeometry(100, 100, 900, 600)
        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Cerca per nom...")
        self.search_box.textChanged.connect(self.search_books)
        layout.addWidget(self.search_box)

        self.import_button = QPushButton("Importar CSV")
        self.import_button.clicked.connect(self.import_csv)
        layout.addWidget(self.import_button)

        self.export_button = QPushButton("Exportar CSV")
        self.export_button.clicked.connect(self.export_csv)
        layout.addWidget(self.export_button)

        self.book_table = QTableWidget()
        layout.addWidget(self.book_table)

        self.add_book_button = QPushButton("Afegir llibre")
        self.add_book_button.clicked.connect(self.add_book)
        layout.addWidget(self.add_book_button)

        self.delete_book_button = QPushButton("Eliminar llibre seleccionat")
        self.delete_book_button.clicked.connect(self.delete_book)
        layout.addWidget(self.delete_book_button)

        self.view_book_button = QPushButton("Veure fitxa del llibre")
        self.view_book_button.clicked.connect(self.view_book_details)
        layout.addWidget(self.view_book_button)

        self.rent_button = QPushButton("Llogar un llibre")
        self.rent_button.clicked.connect(self.rent_book)
        layout.addWidget(self.rent_button)

        self.stats_button = QPushButton("Generar mètriques i gràfics")
        self.stats_button.clicked.connect(self.generate_metrics)
        layout.addWidget(self.stats_button)

        self.central_widget.setLayout(layout)

        self.books_df = pd.DataFrame(columns=["Nom", "Autor", "Pàgines", "Gènere", "Sinopsis", "Data de publicació",
                                              "Edició", "En préstec", "Estanteria", "Fila", "Columna"])

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecciona un fitxer CSV", "", "CSV Files (*.csv)")
        if file_path:
            try:
                temp_df = pd.read_csv(file_path)
                if set(temp_df.columns) != set(self.books_df.columns):
                    QMessageBox.critical(self, "Error",
                                         "Les columnes del CSV no coincideixen amb l'estructura esperada.")
                    return
                self.books_df = temp_df
                self.update_table()
                QMessageBox.information(self, "Èxit", "Dades importades correctament!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al carregar el fitxer: {str(e)}")

    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar fitxer CSV", "", "CSV Files (*.csv)")
        if file_path:
            try:
                self.books_df.to_csv(file_path, index=False)
                QMessageBox.information(self, "Èxit", "Dades exportades correctament!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al guardar el fitxer: {str(e)}")

    def search_books(self):
        search_text = self.search_box.text().strip().lower()
        if not search_text:
            self.update_table()
            return
        filtered_df = self.books_df[self.books_df["Nom"].astype(str).str.lower().str.contains(search_text, na=False)]
        self.update_table(filtered_df)

    def update_table(self, df=None):
        if df is None:
            df = self.books_df

        self.book_table.setRowCount(len(df))
        self.book_table.setColumnCount(len(df.columns))
        self.book_table.setHorizontalHeaderLabels(df.columns)

        for row in range(len(df)):
            for col in range(len(df.columns)):
                value = str(df.iloc[row, col]) if pd.notna(df.iloc[row, col]) else ""
                self.book_table.setItem(row, col, QTableWidgetItem(value))

    def add_book(self):
        new_book = pd.DataFrame([{column: "" for column in self.books_df.columns}])
        self.books_df = pd.concat([self.books_df, new_book], ignore_index=True)
        self.update_table()

    def delete_book(self):
        selected_row = self.book_table.currentRow()
        if selected_row >= 0:
            reply = QMessageBox.question(self, "Confirmació", "Estàs segur que vols eliminar aquest llibre?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.books_df.drop(index=selected_row, inplace=True)
                self.books_df.reset_index(drop=True, inplace=True)
                self.update_table()

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
            save_button.clicked.connect(lambda: self.save_book_details(selected_row, fields, book_dialog))
            layout.addWidget(save_button)

            book_dialog.setLayout(layout)
            book_dialog.exec()

    def save_book_details(self, selected_row, fields, dialog):
        for col, field in fields.items():
            self.books_df.at[selected_row, col] = field.text()
        self.update_table()
        dialog.accept()

    def rent_book(self):
        selected_row = self.book_table.currentRow()
        if selected_row >= 0:
            self.books_df.at[selected_row, "En préstec"] = "Sí"
            self.update_table()
            QMessageBox.information(self, "Èxit", "El llibre ha estat llogat correctament!")

    def generate_metrics(self):
        if self.books_df.empty:
            QMessageBox.warning(self, "Advertència", "No hi ha dades disponibles per generar gràfics.")
            return
        genre_counts = self.books_df["Gènere"].value_counts()
        plt.figure(figsize=(8, 5))
        plt.bar(genre_counts.index, genre_counts.values)
        plt.xlabel("Gènere")
        plt.ylabel("Nombre de llibres")
        plt.title("Distribució de llibres per gènere")
        plt.xticks(rotation=45)
        plt.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BibliotecaApp()
    window.show()
    sys.exit(app.exec())
