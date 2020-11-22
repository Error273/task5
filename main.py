import sys

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog
from PyQt5 import QtCore
import sqlite3


class addEditCoffeeForm(QDialog):
    def __init__(self, parent, *id):
        super().__init__(parent, QtCore.Qt.Window)
        self.id = id
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.setModal(True)
        self.setFixedSize(514, 277)

        self.btn.clicked.connect(self.add_or_edit)

        self.db = sqlite3.connect('coffee.db3')
        self.cur = self.db.cursor()

        self.show()

    def add_or_edit(self):
        sort_name = self.sort_name_edit.text().strip()
        degree_of_roasting = self.degree_of_roasting_edit.text().strip()
        type_ = self.type_edit.text().strip()
        taste_description = self.taste_description_edit.text().strip()
        cost = self.cost_edit.text().strip()
        volume = self.volume_edit.text().strip()
        if not all([sort_name, degree_of_roasting, type_, taste_description, cost, volume]):
            self.output.setText('Все поля должны быть заполнены')
            return
        try:
            cost = float(cost)
            volume = float(volume)
        except ValueError:
            self.output.setText('Цена и объем упаковки должны быть числами')
            return

        if self.id:  # если запись добавить
            self.cur.execute("""UPDATE data
                                SET sort_name = ?, 
                                    degree_of_roasting = ?,
                                    type = ?,
                                    taste_description = ?,
                                    cost = ?,
                                    volume = ?
                                WHERE id = ?
            """, [sort_name,degree_of_roasting,type_,taste_description,cost, volume, self.id[0]])
        else:
            self.cur.execute("""INSERT INTO data(sort_name,
                                degree_of_roasting,
                                type,
                                taste_description,
                                cost,
                                volume)
                                VALUES (?, ?, ?, ?, ?, ?)""",
                             [sort_name,degree_of_roasting,type_,taste_description,cost, volume])
        self.db.commit()
        self.parent().update_table()
        self.close()


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.db = sqlite3.connect('coffee.db3')
        self.cur = self.db.cursor()

        self.add_btn.clicked.connect(self.add_coffee)
        self.edit_btn.clicked.connect(self.edit_coffee)

        self.update_table()

    def add_coffee(self):
        addEditCoffeeForm(self)

    def edit_coffee(self):
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        id = [self.tableWidget.item(i, 0).text() for i in rows]
        if id:
            addEditCoffeeForm(self, int(id[0]))


    def update_table(self):
        res = self.cur.execute('SELECT * FROM data').fetchall()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(len(res))
        self.tableWidget.setHorizontalHeaderLabels(['id', 'название сорта', 'степень обжарки',
                                                    'молотый/в зернах', 'описание вкуса', 'цена', 'объем упаковки'])
        for i, row in enumerate(res):
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
                item = self.tableWidget.item(i, j)
                item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.tableWidget.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
