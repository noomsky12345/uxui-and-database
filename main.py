import sys
import sqlite3
from PySide6.QtWidgets import QApplication, QTableWidgetItem, QMessageBox
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

# ==========================================
# ส่วนที่ 1: จัดการฐานข้อมูล
# ==========================================
class DatabaseManager:
    def __init__(self, db_name="student.db"): # <--- เปลี่ยนมาใช้ student.db ของคุณ
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # สร้างตารางใหม่ชื่อ student_data เพื่อให้ตรงกับหน้าจอของคุณ
        sql = """
        CREATE TABLE IF NOT EXISTS student_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT,
            salary TEXT
        )
        """
        self.cursor.execute(sql)
        self.conn.commit()

    def add_data(self, name, position, salary):
        sql = "INSERT INTO student_data (name, position, salary) VALUES (?, ?, ?)"
        self.cursor.execute(sql, (name, position, salary))
        self.conn.commit()

    def get_all_data(self):
        sql = "SELECT * FROM student_data"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def update_data(self, record_id, name, position, salary):
        sql = "UPDATE student_data SET name=?, position=?, salary=? WHERE id=?"
        self.cursor.execute(sql, (name, position, salary, record_id))
        self.conn.commit()

    def delete_data(self, record_id):
        sql = "DELETE FROM student_data WHERE id=?"
        self.cursor.execute(sql, (record_id,))
        self.conn.commit()

# ==========================================
# ส่วนที่ 2: จัดการหน้าจอ
# ==========================================
class MainWindow:
    def __init__(self):
        # โหลดหน้าจอ UI ที่คุณเพิ่งส่ง XML มา
        ui_file = QFile("untitled.ui")
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        self.db = DatabaseManager()

        # เชื่อมปุ่มกด
        self.window.pushButton.clicked.connect(self.create_data)   # Create
        self.window.pushButton_2.clicked.connect(self.update_data) # Update
        self.window.pushButton_3.clicked.connect(self.delete_data) # Delete
        self.window.pushButton_4.clicked.connect(self.clear_data)  # Clear
        
        self.window.tableWidget.cellClicked.connect(self.select_data)
        self.load_data()

    def create_data(self):
        name = self.window.lineEdit.text()
        position = self.window.lineEdit_2.text()
        salary = self.window.lineEdit_3.text()

        if name and salary:
            self.db.add_data(name, position, salary)
            QMessageBox.information(self.window, "Success", "บันทึกข้อมูลลง student.db เรียบร้อย!")
            self.clear_data()
            self.load_data()
        else:
            QMessageBox.warning(self.window, "Error", "กรุณากรอกข้อมูลให้ครบถ้วน")

    def load_data(self):
        result = self.db.get_all_data()
        self.window.tableWidget.setRowCount(0)

        for row_number, row_data in enumerate(result):
            self.window.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.window.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def select_data(self):
        row = self.window.tableWidget.currentRow()
        self.selected_id = self.window.tableWidget.item(row, 0).text()
        self.window.lineEdit.setText(self.window.tableWidget.item(row, 1).text())
        self.window.lineEdit_2.setText(self.window.tableWidget.item(row, 2).text())
        self.window.lineEdit_3.setText(self.window.tableWidget.item(row, 3).text())

    def update_data(self):
        if hasattr(self, 'selected_id'):
            name = self.window.lineEdit.text()
            position = self.window.lineEdit_2.text()
            salary = self.window.lineEdit_3.text()

            self.db.update_data(self.selected_id, name, position, salary)
            self.load_data()
            self.clear_data()
            QMessageBox.information(self.window, "Success", "แก้ไขข้อมูลเรียบร้อย")
        else:
            QMessageBox.warning(self.window, "Warning", "กรุณาเลือกรายการที่ต้องการแก้ไข")

    def delete_data(self):
        if hasattr(self, 'selected_id'):
            confirm = QMessageBox.question(self.window, "Confirm", "ต้องการลบข้อมูลนี้ใช่หรือไม่?", 
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.db.delete_data(self.selected_id)
                self.load_data()
                self.clear_data()
                del self.selected_id
        else:
            QMessageBox.warning(self.window, "Warning", "กรุณาเลือกรายการที่ต้องการลบ")

    def clear_data(self):
        self.window.lineEdit.clear()
        self.window.lineEdit_2.clear()
        self.window.lineEdit_3.clear()
        if hasattr(self, 'selected_id'):
            del self.selected_id

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.window.show()
    sys.exit(app.exec())