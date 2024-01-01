import os
import sys
import sqlite3
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from test5_ui import Ui_MainWindow

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect(resource_path("database.sqlite"))

        self.figure = plt.figure()
        self.ax = self.figure.add_subplot()
        self.canvas = FigureCanvas(self.figure)
        self.tabWidget.currentChanged.connect(self.tab_change)
        self.widget_graph.layout().removeWidget(self.changebox)
        self.changebox.deleteLater()
        self.widget_graph.layout().addWidget(self.canvas)

        lst_for_critboxgr = ['Фонд', 'Количество КП, сделанных сотрудником',
                             'Количество лифтов проданных в регион', 'Количество лифтов с МП',
                             'Количество с дизайном', 'Количество лифтов с сейсмической защитой']
        self.critboxgr.addItems(lst_for_critboxgr)
        self.critboxgr.currentIndexChanged.connect(self.updateCriboxgrItems)

        self.dateEdit.dateChanged.connect(lambda date: self.dateEdit_2.setMinimumDate(date.addDays(1)))
        self.dateEdit_2.dateChanged.connect(lambda date: self.dateEdit.setMaximumDate(date.addDays(-1)))

        self.pushButton_graph.clicked.connect(self.graphfunc)

        cur = self.con.cursor()
        self.comboBox_3.addItem('')
        self.comboBox_3.addItems([item[0] for item in cur.execute('SELECT proj FROM Projects')])

        self.comboBox_2.addItem('')
        self.comboBox_2.addItems([item[0] for item in cur.execute('SELECT region FROM regions')])

        self.comboBox.addItem('')
        self.comboBox.addItems([item[0] for item in cur.execute('SELECT name FROM managers')])

        self.comboBox_4.addItem('')
        self.comboBox_4.addItems([item[0] for item in cur.execute('SELECT emp FROM employ')])

        lst_of_suit = []
        month = 3
        year = 2021
        while year != 2023 or month != 11:
            if month == 13:
                month = 1
                year += 1
            else:
                lst_of_suit.append(('00' + str(month))[-2:] + '.' + str(year))
                month += 1
        self.comboBox_5.addItem('')
        self.comboBox_5.addItems(lst_of_suit)

        self.tablebox.addItem('agreement')
        self.tablebox.addItem('KP')
        self.tablebox.addItem('OL')
        self.tablebox.addItem('Projects')
        self.tablebox.addItem('regions')
        self.tablebox.addItem('managers')
        self.tablebox.addItem('employ')
        self.tablebox.addItem('contragents')
        self.tablebox.currentIndexChanged.connect(self.updateElboxItems)

        self.count_edit.setText('100')

        self.pushButton_filter.clicked.connect(self.OLtableFunc)

        self.pushButton_data.clicked.connect(self.table_function)

        self.elbox.addItems(
            ['id', 'date', 'num', 'summ', 'sale', 'count', 'contragent', 'region', 'manager'])

        self.dobox.addItem('Выбрать')
        self.dobox.addItem('Удалить')

        self.elbox.currentIndexChanged.connect(self.updateCritboxItems)

        self.critbox.addItem('Больше')
        self.critbox.addItem('Меньше')
        self.critbox.addItem('Равно')
        self.critbox.addItem('Содержит строку')
        self.critbox.addItem('Не содержит строку')

        self.tableboxgr.addItem('Да')
        self.tableboxgr.addItem('Нет')

        self.critboxgr.currentIndexChanged.connect(self.elerUpdate)
        self.eler = 'fond'

        cur = self.con.cursor()
        res = cur.execute('SELECT * FROM OL WHERE pack LIKE "%.202%"').fetchall()
        self.label_17.setText('Количество проданых лифтов: ' + str(len(res)))

        res = cur.execute('SELECT createby FROM OL WHERE pack LIKE "%.202%"').fetchall()
        lib = {}
        for el in res:
            if el not in lib.keys():
                lib[el] = 1
            else:
                lib[el] += 1
        m = ''
        for el in lib.keys():
            if lib[el] == max(lib.values()):
                m = el[0]
                break
        sender = f'SELECT emp FROM employ WHERE id = {m}'
        res = list(cur.execute(sender).fetchall())
        self.label_20.setText('Самый эффективный сотрудник: ' + str(res[0][0]))

        res = list(cur.execute('SELECT eqcost FROM OL WHERE pack LIKE "%.202%"').fetchall())
        res = map(lambda x: int(x[0].replace(' ', '')), res)
        c = max(res)
        self.label_18.setText('Самое дорогое оборудование: ' + str(c))

        res = list(cur.execute('SELECT summ FROM agreement WHERE id > 0').fetchall())
        res = map(lambda x: x[0], res)
        c = max(res)
        self.label_21.setText('Самая дорогая партия: ' + str(c))

        res = list(cur.execute('SELECT sale FROM agreement WHERE id > 0').fetchall())
        res = map(lambda x: x[0], res)
        c = max(res)
        self.label_22.setText('Самая большая скидка: ' + str(c) + '%')

        res = list(cur.execute('SELECT region FROM agreement WHERE id > 0').fetchall())
        res = list(map(lambda x: x[0], res))
        c = len(res)
        self.label_23.setText('Партий поступило в Москву: ' + str(c))

        res = cur.execute('SELECT fond FROM OL WHERE id > 0').fetchall()
        count = 0
        for el in res:
            if el[0] == 'Да':
                count += 1
        count = round(count / 108819 * 100, 2)
        self.label_24.setText('Процентное количество фондовых лифтов: ' + str(count) + '%')

        res = cur.execute('SELECT nomp FROM OL WHERE id > 0').fetchall()
        count = 0
        for el in res:
            if el[0] == 'Да':
                count += 1

        count = round(count / 108819 * 100, 2)
        self.label_26.setText('Процентное количество с машинным помещением: ' + str(count) + '%')

        res = list(cur.execute('SELECT summ FROM agreement WHERE id > 0').fetchall())
        res = map(lambda x: x[0], res)
        c = sum(res)
        self.label_16.setText('Суммарная прибыль: ' + str(c))

        res = list(cur.execute('SELECT count FROM agreement WHERE id > 0').fetchall())
        res = map(lambda x: x[0], res)
        m_el = list(res)[0]

        for el in list(res)[1:]:
            try:
                if el > m_el:
                    m_el = el
            except TypeError:
                pass

        self.label_25.setText('Максимальное количество в 1 партии: ' + str(m_el))
        res = cur.execute('SELECT design FROM OL WHERE id > 0').fetchall()
        count = 0

        for el in res:
            if el[0] == 'Комфорт':
                count += 1

        count = round(count / 108819 * 100, 2)
        self.label_19.setText('Процентное количество с дизайном "Комфорт": ' + str(count) + '%')

        self.label_27.setText('')

    def keyPressEvent(self, event):
        # Функция считывания нажатия на клавишу esc
        if event.key() == Qt.Key_Escape:
            self.show_dialog()

    def show_dialog(self):
        # Функция закрытия программы при работе в диалоговом окне
        dialog = QMessageBox()
        dialog.setWindowTitle("Закрыть программу?")
        dialog.setText("Вы действительно хотите закрыть программу?")
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.No)
        result = dialog.exec_()

        if result == QMessageBox.Yes:
            QApplication.quit()

    def tab_change(self, index):
        # Функция обновления статусбар
        self.statusBar().clearMessage()

    def updateElboxItems(self, index):
        # Функция обновления элементов
        self.elbox.clear()
        lst = []
        if index == 0:
            lst = ['id', 'date', 'num', 'summ', 'sale', 'count', 'contragent', 'region', 'manager']

        elif index == 1:
            lst = ['id', 'date', 'num', 'summ', 'employer', 'manager', 'contragent']

        elif index == 2:
            lst = ['id', 'date', 'num', 'createby', 'facnum', 'adressfin', 'agreem', 'contragent', 'eqcost', 'model',
                   'pack', 'datemade', 'fond', 'nomp', 'design', 'firedef', 'ibp', 'vent', 'seism', 'transmmgn']

        elif index == 3:
            lst = ['id', 'proj', 'typee', 'liftingcapac', 'speed']

        elif index == 4:
            lst = ['id', 'region']

        elif index == 5:
            lst = ['id', 'name']

        elif index == 6:
            lst = ['id', 'emp']

        elif index == 7:
            lst = ['id', 'name']

        self.elbox.addItems(lst)

    def updateCritboxItems(self):
        # Функция обновления элементов
        if self.elbox.count() != 0:
            self.critbox.clear()

            text_table = self.tablebox.currentText()
            text_el = self.elbox.currentText()

            text = 'SELECT ' + text_el + ' FROM ' + text_table + ' WHERE id = 1'
            cur = self.con.cursor()
            result = list(cur.execute(f"""{text}""").fetchall())

            test_data = result[0][0]

            if type(test_data) == int:
                self.critbox.addItem('Меньше')
                self.critbox.addItem('Больше')
                self.critbox.addItem('Равно')
                self.count_edit.setText('100')
            else:
                self.critbox.addItem('Содержит строку')
                self.critbox.addItem('Не содержит строку')
                self.count_edit.setText('A')

    def elerUpdate(self, index):
        # Функция обновления элементов
        if index == 0:
            self.eler = 'fond'
        elif index == 1:
            self.eler = 'createby'
        elif index == 2:
            self.eler = 'adressfin'
        elif index == 3:
            self.eler = 'nomp'
        elif index == 4:
            self.eler = 'design'
        elif index == 5:
            self.eler = 'seism'

    def updateCriboxgrItems(self, index):
        # Функция обновления элементов
        self.tableboxgr.clear()

        if index == 0:
            self.tableboxgr.addItems(['Да', 'Нет'])

        elif index == 1:
            cur = self.con.cursor()
            self.tableboxgr.addItems([item[0] for item in cur.execute("SELECT emp FROM employ").fetchall()])

        elif index == 2:
            cur = self.con.cursor()
            self.tableboxgr.addItems([item[0] for item in cur.execute("SELECT region FROM regions").fetchall()])

        elif index == 3:
            self.tableboxgr.addItems(['Да', 'Нет'])

        elif index == 4:
            self.tableboxgr.addItems(['Комфорт', 'Стандарт', 'Премиум'])

        elif index == 5:
            self.tableboxgr.addItems(['до 6 баллов', 'выше 7 баллов'])

    def OLtableFunc(self):
        # Функция запроса ОЛ
        names = ['Дата', 'Номер КП', 'Номер заказа', 'Регион', 'Заказчик', 'Товар', 'Проект', 'Сотрудник', 'Менеджер',
                 'Фонд',
                 'Дизайн', 'Машинное помещение', 'Сейсмичность', 'Стоимость', 'Номер договора', 'Огнестойкость', 'ИБП',
                 'Вентилятор', 'ММГН']
        self.statusBar().clearMessage()
        self.table_filter.clear()

        sp_of_1 = [1 for i in range(19)]
        sp_of_2 = []

        sp = []
        cur = self.con.cursor()
        model = self.comboBox_3.currentText()

        if model != '':
            sp.append(model)
            sp_of_1[6] = 0
        adressfin = self.comboBox_2.currentText()
        if adressfin != '':
            adressfin = list(cur.execute(f'SELECT region FROM regions WHERE region = "{adressfin}"'))[0][0]
            sp.append(adressfin)
            sp_of_1[3] = 0

        manager = self.comboBox.currentText()
        if manager != '':
            manager = list(cur.execute(f'SELECT name FROM managers WHERE name = "{manager}"'))[0][0]
            sp.append(manager)
            sp_of_1[8] = 0
        emp = self.comboBox_4.currentText()

        if emp != '':
            emp = list(cur.execute(f'SELECT emp FROM employ WHERE emp = "{emp}"'))[0][0]
            sp.append(emp)
            sp_of_1[7] = 0
        pack = self.comboBox_5.currentText()

        if pack != '':
            sp.append(pack)
            sp_of_1[5] = 0
        sp_st = []

        for el in sp:
            if el == model:
                sp_st.append(f'OL.model = "{el}"')

            elif el == adressfin:
                sp_st.append(f'regions.region = "{str(adressfin)}"')

            elif el == manager:
                sp_st.append(f'managers.name = "{str(manager)}"')

            elif el == emp:
                sp_st.append(f'employ.emp = "{str(emp)}"')

            elif el == pack:
                sp_st.append(f'pack LIKE "%{pack}"')

        sender = ' AND '.join(sp_st)

        if sender == '':
            sender = 'OL.id > 0'

        for i in range(len(sp_of_1)):
            if sp_of_1[i] == 1:
                sp_of_2.append(names[i])

        select_vib = 'OL.date, OL.num, OL.facnum'
        if adressfin == '':
            select_vib += ', regions.region'
        select_vib += ', contragents.name'
        if pack == '':
            select_vib += ', OL.pack'
        if model == '':
            select_vib += ', OL.model'
        if emp == '':
            select_vib += ', employ.emp'
        if manager == '':
            select_vib += ', managers.name'

        select_vib += ', OL.fond'
        select_vib += ', OL.design'
        select_vib += ', OL.ibp'
        select_vib += ', OL.seism, OL.eqcost, OL.agreem,OL.firedef, OL.ibp, OL.vent, OL.transmmgn'

        leftjoin = 'LEFT JOIN regions ON OL.adressfin = regions.id'
        leftjoin += ' LEFT JOIN KP ON OL.num = KP.num'
        leftjoin += ' LEFT JOIN Projects ON OL.model = Projects.proj'
        leftjoin += ' LEFT JOIN managers ON KP.manager = managers.id'
        leftjoin += ' LEFT JOIN employ ON OL.createby = employ.id'
        leftjoin += ' LEFT JOIN contragents ON OL.contragent = contragents.id'

        sender1 = 'SELECT ' + select_vib + ' FROM OL ' + leftjoin + ' WHERE (' + sender + ')'

        res = cur.execute(sender1).fetchall()

        if len(res) == 0:
            self.statusbar.showMessage("Элементов не найдено")
            self.table_filter.setRowCount(0)
            self.table_filter.setColumnCount(0)
            self.table_filter.clear()
        else:
            self.statusbar.showMessage("Найдено  элементов: " + str(len(res)))
            self.table_filter.setRowCount(len(res))
            self.table_filter.setColumnCount(len(res[0]))

            for i in range(len(res)):
                for j in range(len(res[0])):
                    item = QTableWidgetItem(str(res[i][j]))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table_filter.setItem(i, j, item)
            self.table_filter.setHorizontalHeaderLabels(sp_of_2)

    def table_function(self):
        # Функция просмотра таблиц базы данных по 1 критерию
        self.statusBar().clearMessage()
        SP = [['id', 'date', 'num', 'summ', 'sale', 'count', 'contragent', 'region', 'manager'],
              ['id', 'date', 'num', 'summ', 'employer', 'manager', 'contragent'],
              ['id', 'date', 'num', 'createby', 'facnum', 'adressfin', 'agreem', 'contragent', 'eqcost', 'model',
               'pack', 'datemade', 'fond', 'nomp', 'design', 'firedef', 'ibp', 'vent', 'seism', 'transmmgn'],
              ['id', 'proj', 'typee', 'liftingcapac', 'speed'], ['id', 'region'], ['id', 'name'], ['id', 'emp'],
              ['id', 'name']]

        if self.lineEdit.text() != '':
            sender = self.lineEdit.text()
            cur = self.con.cursor()
            result = cur.execute(sender).fetchall()
            self.table_data.setRowCount(len(result))
            self.table_data.setColumnCount(len(result[0]))
            for i in range(len(result)):
                for j in range(len(result[0])):
                    self.table_data.setItem(i, j, QTableWidgetItem(str(result[i][j])))
        else:
            table = self.tablebox.currentText()
            do = self.dobox.currentText()
            el = self.elbox.currentText()
            crit = self.critbox.currentText()
            count = self.count_edit.text()
            transform_lib = {
                'Больше': '>',
                'Меньше': '<',
                'Равно': '='
            }

            if do == 'Выбрать':
                if crit in transform_lib.keys():
                    crit = transform_lib[crit]
                    sender = 'SELECT * FROM ' + table + ' WHERE ' + el + ' ' + crit + ' ' + count
                else:
                    if crit == 'Содержит строку':
                        sender = 'SELECT * FROM ' + table + ' WHERE ' + el + ' LIKE ' + f'"%{count}%"'

                    else:
                        sender = 'SELECT * FROM ' + table + ' WHERE ' + el + ' NOT LIKE ' + f'"%{count}%"'
                cur = self.con.cursor()
                result = cur.execute(sender).fetchall()

                if len(result) == 0:
                    self.table_data.clear()
                    self.table_data.setRowCount(0)
                    self.table_data.setColumnCount(0)
                    self.statusbar.showMessage("Элементов не найдено")
                else:
                    self.statusbar.showMessage("Найдено  элементов: " + str(len(result)))
                    self.table_data.setRowCount(len(result))
                    self.table_data.setColumnCount(len(result[0]))
                    for i in range(len(result)):
                        for j in range(len(result[0])):
                            item = QTableWidgetItem(str(result[i][j]))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.table_data.setItem(i, j, item)
                    self.table_data.setHorizontalHeaderLabels(SP[self.tablebox.currentIndex()])

            elif do == 'Удалить':
                if crit in transform_lib.keys():
                    crit = transform_lib[crit]
                    sender = 'DELETE FROM ' + table + ' WHERE ' + el + ' ' + crit + ' ' + count
                else:
                    if crit == 'Содержит строку':
                        sender = 'DELETE FROM ' + table + ' WHERE ' + el + ' LIKE ' + f'"%{count}%"'
                    else:
                        sender = 'DELETE FROM ' + table + ' WHERE ' + el + ' NOT LIKE ' + f'"%{count}%"'
                cur = self.con.cursor()
                cur.execute(sender).fetchall()
                self.con.commit()

    def graphfunc(self):
        # Функция построения графика или диаграммы
        self.statusBar().clearMessage()
        self.ax.clear()

        selected_date_st = self.dateEdit.date()
        month_st, year_st = map(int, selected_date_st.toString('MM.yyyy').split('.'))
        selected_date_en = self.dateEdit_2.date()
        month_en, year_en = map(int, selected_date_en.toString('MM.yyyy').split('.'))
        text_of_crit = self.critboxgr.currentText()
        text_of_table = self.tableboxgr.currentText()

        if text_of_crit == 'Количество КП, сделанных сотрудником':
            cur = self.con.cursor()
            text_of_table = list(cur.execute(f"SELECT id FROM employ WHERE emp = '{self.tableboxgr.currentText()}'"))
            text_of_table = str(text_of_table[0][0])

        elif text_of_crit == 'Количество лифтов проданных в регион':
            cur = self.con.cursor()
            text_of_table = list(
                cur.execute(f"SELECT id FROM regions WHERE region = '{self.tableboxgr.currentText()}'"))
            text_of_table = str(text_of_table[0][0])

        lst_of_suit = []
        month = month_st
        year = year_st

        while year <= year_en:
            if year < year_en:
                while month <= 12:
                    lst_of_suit.append(('00' + str(month))[-2:] + '.' + str(year))
                    month = month + 1

                if month == 13:
                    month = 1
                    year = year + 1

            if year == year_en:
                while month <= month_en:
                    lst_of_suit.append(('00' + str(month))[-2:] + '.' + str(year))
                    month = month + 1
                year = year + 1
        x = []
        y = []
        t_lib = {}
        cur = self.con.cursor()

        for el in lst_of_suit:
            sender = f'SELECT * FROM OL WHERE(pack LIKE "{el}" AND {self.eler} = "{text_of_table}")'
            res = cur.execute(sender).fetchall()
            t_lib[el] = len(res)
            x.append(el[:-5] + '.' + el[-2:])
            y.append(len(res))

        if self.graph.isChecked():
            self.ax.cla()
            if not any(y):
                self.ax.cla()
                y = [1]
                self.ax.pie(y, colors='w', autopct='Элементов не найдено', radius=1.5)
                self.canvas.draw()
            else:
                self.ax.set_aspect('auto')
                self.ax.set_ylabel('количество')
                self.ax.set_xlabel('период, мес')
                self.ax.bar(x, y, alpha=0.5)
                self.ax.grid(True)
                self.ax.plot(x, y, color='green', marker='o', markersize=7)
                self.canvas.draw()

        elif self.diagr.isChecked():
            if not any(y):
                self.ax.cla()
                y = [1]
                self.ax.pie(y, colors='w', autopct='Элементов не найдено', radius=1.5)
                self.canvas.draw()
            else:
                x_p, y_p = [], []
                for i in range(len(y)):
                    if y[i] != 0:
                        x_p.append(x[i])
                        y_p.append(y[i])
                x, y = x_p, y_p
                self.ax.pie(y, labels=x, autopct='%1.1f%%')
                self.canvas.draw()
        else:
            self.statusbar.showMessage("Выберите вид вывода данных")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
