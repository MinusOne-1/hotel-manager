import csv
import datetime
import sys
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem, QDateEdit, QStackedWidget, QVBoxLayout, QLabel


class Main():
    def __init__(self):
        self.user = ''
        self.work_w = ''
        self.main_w = ''
        self.adm_and_menegers = {}
        self.loadAdmAndMenagers()
        print(self.adm_and_menegers)
        self.timer = self.getTimerStatus()
        self.timer_second = 0
        self.openLoginWindow()

    def loadAdmAndMenagers(self):
        res = []
        with open('admins.csv', encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='\'')
            res = [[row[0], row[1], 'admin', row[-1]] for index, row in enumerate(reader)]
            res = res[1:]
        with open('managers.csv', encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='\'')
            res.extend([[row[0], row[1], 'manager', 'all'] for index, row in enumerate(reader) if index != 0])
        for i in res:
            self.adm_and_menegers[i[0]] = {'password': i[1], 'work': i[2], 'hotel': i[3]}

    def getTimerStatus(self):
        file = open('timerStatus.txt', 'r')
        state = file.readlines()
        file.close()
        if 'False' in state[0]:
            return False
        else:
            now = datetime.datetime.now()
            if now.minute == int(state[1].split(':')[1]) and now.hour == int(state[1].split(':')[0]) and now.second < int(state[1].split(':')[2]):
                self.timer_second = 60 - int(state[1].split(':')[2])
                self.timer_second -= now.second
            elif now.minute == int(state[1].split(':')[1]) - 1 and now.hour == int(state[1].split(':')[0]):
                self.timer_second = 60 - (now.second - int(state[1].split(':')[2]))
            else:
                file = open('timerStatus.txt', 'w')
                file.write('False')
                file.close()
                return False
            return True

    def openMangerAndAdminWindow(self, work):
        if work == 'admin':
            self.openAdminWindow(self.adm_and_menegers[self.user.split()[0]]['hotel'])
        if work == 'manager':
            self.openManagerWindow()

    def openLoginWindow(self):
        app = QApplication(sys.argv)
        self.main_w = Login(self)
        self.main_w.show()
        sys.exit(app.exec())

    def openAdminWindow(self, hotel):
        open_win = Admin(self.main_w, hotel)
        open_win.show()
        self.work_w = open_win
        self.main_w.hide()

    def openManagerWindow(self):
        open_win = Manager(self.main_w)
        open_win.show()
        self.work_w = open_win
        self.main_w.hide()


class MyTimer(QMainWindow):
    def __init__(self, DURATION_INT, main):
        super().__init__(main)
        self.main = main
        self.DURATION_INT = DURATION_INT
        self.time_left_int = self.DURATION_INT
        self.widget_counter_int = 0

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        vbox = QVBoxLayout()
        central_widget.setLayout(vbox)

        self.pages_qsw = QStackedWidget()
        vbox.addWidget(self.pages_qsw)
        self.time_passed_qll = QLabel()
        vbox.addWidget(self.time_passed_qll)

        self.timer_start()
        self.update_gui()

    def timer_start(self):
        self.time_left_int = self.DURATION_INT

        self.my_qtimer = QtCore.QTimer(self)
        self.my_qtimer.timeout.connect(self.timer_timeout)
        self.my_qtimer.start(1000)

        self.update_gui()

    def timer_timeout(self):
        self.time_left_int -= 1
        if self.time_left_int == 0:
            self.main.main.timer = False
            self.close()
        self.update_gui()

    def update_gui(self):
        self.time_passed_qll.setText(str(self.time_left_int))



class Login(QMainWindow):
    def __init__(self, main):
        super().__init__()
        uic.loadUi('okoshko.ui', self)
        self.main = main
        self.enter.clicked.connect(self.login_func)
        self.exit.clicked.connect(self.exit_func)
        self.trys = 0
        self.trys_list = []
        if self.main.timer:
            self.timer_start(self.main.timer_second)

    def saveChanges(self, action):
        file = open('change_list.txt', 'r', encoding='utf8')
        text = file.read()
        file.close()
        file = open('change_list.txt', 'w', encoding='utf8')
        file.write(text + '\n' + self.main.user + ':' + action)

    def login_func(self):
        if self.main.timer:
            return 0
        login = self.login.text()
        password = self.password.text()
        if login in self.main.adm_and_menegers.keys():
            if password == self.main.adm_and_menegers[login]['password']:
                self.main.user = login + ' ' + password
                print('Вошёл: ' + self.main.user)
                self.main.openMangerAndAdminWindow(self.main.adm_and_menegers[login]['work'])

            else:
                self.trys += 1
                print(login + '    ' + password + ': Некорректный пароль')
                self.trys_list.append(login + '    ' + password + ': Некорректный пароль')
        else:
            self.trys += 1
            print(login + '    ' + password + ': Некорректный логин')
            self.trys_list.append(login + '    ' + password + ': Некорректный логин')
        if self.trys == 3:
            self.trys = 0
            self.main.timer = True
            now = datetime.datetime.now()
            file = open('timerStatus.txt', 'w')
            file.write('True\n' + str(now.hour) + ':' + str(now.minute + 1) + ':' + str(now.second))
            self.timer_start(60)

    def timer_start(self, sec):
        print(sec)
        win = MyTimer(sec, self)
        win.show()

    def exit_func(self):
        exit(0)


class Person():
    def __init__(self, **kwargs):
        self.data = kwargs
        self.roomed = False

    def __str__(self):
        return ';'.join(self.data.values()) + str(self.roomed)

    def editOneData(self, key, new_value):
        self.data[key] = new_value

    def giveRoom(self):
        self.roomed = True

    def takeRoom(self):
        self.roomed = False


class Manager(QMainWindow):
    def __init__(self, main):
        super().__init__(main)
        self.main = main
        uic.loadUi('Manager.ui', self)

        self.f_name_hotels = 'hotels.csv'
        self.f_name_admins = 'admins.csv'

        self.showall.clicked.connect(self.showAllHotels)
        self.showalladm.clicked.connect(self.showAllAdmins)
        self.addadm.clicked.connect(self.addAdmin)
        self.createhotel.clicked.connect(self.addHotel)
        self.exit.clicked.connect(self.exit_func)

        self.hotel_res = []
        self.admins_res = []
        self.loadHotels()
        self.loadAdmins()

    def save(self):
        with open(self.f_name_admins, 'w', newline='', encoding="utf8") as csvfile:
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='\'', quoting=csv.QUOTE_MINIMAL)
            for i in self.admins_res:
                writer.writerow(i)

        with open(self.f_name_hotels, 'w', newline='', encoding="utf8") as csvfile:
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='\'', quoting=csv.QUOTE_MINIMAL)

            for i in self.hotel_res:
                writer.writerow(i)

    def exit_func(self):
        self.main.show()
        self.save()
        self.close()

    def showAllHotels(self):
        self.loadTable(self.hotel_res)

    def showAllAdmins(self):
        self.loadTable(self.admins_res)

    def loadTable(self, list_):
        title = list_[0]
        self.table.setColumnCount(len(title))
        self.table.setHorizontalHeaderLabels(title)
        self.table.setRowCount(0)
        for i in range(len(list_[1:])):
            self.table.setRowCount(self.table.rowCount() + 1)
            for j, elem in enumerate(list_[1:][i]):
                self.table.setItem(i, j, QTableWidgetItem(elem))

        self.table.resizeColumnsToContents()

    def loadHotels(self):
        with open(self.f_name_hotels, encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='\'')
            self.hotel_res = [row for index, row in enumerate(reader)]

    def loadAdmins(self):
        with open(self.f_name_admins, encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='\'')
            self.admins_res = [row for index, row in enumerate(reader)]

    def addAdmin(self):
        win = AddAdminWindow(self)
        win.show()
        self.hide()

    def addHotel(self):
        win = AddHotelWindow(self)
        win.show()
        self.hide()


class Admin(QMainWindow):
    def __init__(self, main, hotel):
        super().__init__(main)
        self.hotel = 'hotels/' + hotel + '.csv'
        self.persons_file = 'persons.csv'
        self.main = main
        uic.loadUi('Admin.ui', self)
        self.showall.clicked.connect(self.showAllRooms)
        self.showpeople.clicked.connect(self.showAllPersons)
        self.addperson.clicked.connect(self.addPerson)
        self.rooms = []
        self.persons = []
        self.loadPersons()
        self.loadRooms()

    def save(self):
        with open(self.hotel, 'w', newline='', encoding="utf8") as csvfile:
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='\'', quoting=csv.QUOTE_MINIMAL)
            for i in self.rooms:
                writer.writerow(i)

        with open(self.persons_file, 'w', newline='', encoding="utf8") as csvfile:
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='\'', quoting=csv.QUOTE_MINIMAL)
            for i in self.persons:
                writer.writerow(i)

    def exit_func(self):
        self.main.show()
        self.save()
        self.close()

    def showAllRooms(self):
        self.loadTable(self.rooms)

    def showAllPersons(self):
        self.loadTable(self.persons)

    def loadTable(self, list_):
        title = list_[0]
        self.table.setColumnCount(len(title))
        self.table.setHorizontalHeaderLabels(title)
        self.table.setRowCount(0)
        for i in range(len(list_[1:])):
            self.table.setRowCount(self.table.rowCount() + 1)
            for j, elem in enumerate(list_[1:][i]):
                self.table.setItem(i, j, QTableWidgetItem(elem))

        self.table.resizeColumnsToContents()

    def loadRooms(self):
        with open(self.hotel, encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='\'')
            self.rooms = [row for index, row in enumerate(reader)]

    def loadPersons(self):
        with open(self.persons_file, encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='\'')
            self.persons = [row for index, row in enumerate(reader)]

    def addPerson(self):
        win = AddPersonWindow(self)
        win.show()
        self.hide()

    def addHotel(self):
        win = AddHotelWindow(self)
        win.show()
        self.hide()


class AddAdminWindow(QMainWindow):
    def __init__(self, main):
        super().__init__(main)
        uic.loadUi('addadm.ui', self)
        self.main = main
        self.hotel.addItems([i[0] for i in self.main.hotel_res])
        self.enter.clicked.connect(self.add)
        self.exit.clicked.connect(self.exit_func)

    def add(self):
        login = self.login.text()
        password = self.password.text()
        surname = self.surname.text()
        name = self.name.text()
        secondname = self.secondname.text()
        phone = self.phone.text()
        hotel = self.hotel.itemText(self.hotel.currentIndex())
        if all([login, password, surname, name, secondname, phone, hotel]):
            self.main.admins_res.append([login, password, surname, name, secondname, phone, hotel])
            self.main.main.saveChanges(
                'Добавил администратора: ' + '; '.join([login, password, surname, name, secondname, phone, hotel]))
            self.exit_func()
        else:
            pass

    def exit_func(self):
        self.main.loadTable(self.main.admins_res)
        self.main.show()
        self.close()


class AddHotelWindow(QMainWindow):
    def __init__(self, main):
        super().__init__(main)
        uic.loadUi('addhot.ui', self)
        self.main = main
        self.enter.clicked.connect(self.add)
        self.exit.clicked.connect(self.exit_func)

    def add(self):
        number = self.number.text()
        floors = self.floors.text()
        rooms = self.rooms.text()
        country = self.country.text()
        city = self.city.text()
        street = self.street.text()
        house = self.house.text()
        if all([number, floors, rooms, country, city, street, house]):
            self.main.hotel_res.append([number, floors, rooms, ', '.join([country, city, street, house])])
            self.main.main.saveChanges(
                'Добавил гостиницу: ' + '; '.join([number, floors, rooms, ', '.join([country, city, street, house])]))
            self.exit_func()
        else:
            pass

    def exit_func(self):
        self.main.loadTable(self.main.hotel_res)
        self.main.show()
        self.close()


class AddPersonWindow(QMainWindow):
    def __init__(self, main):
        super().__init__(main)
        uic.loadUi('tupielyudishki.ui', self)
        self.main = main
        self.enter.clicked.connect(self.add)
        self.exit.clicked.connect(self.exit_func)

    def add(self):
        surname = self.surname.text()
        name = self.name.text()
        secondname = self.secondname.text()
        t = QDateEdit()
        t.date()
        brdata = self.brdata.text()
        gender = ''
        print(self.female.isChecked())
        if self.female.isChecked():
            gender = 'Ж'
        if self.male.isChecked():
            gender = 'М'
        if self.alian.isChecked():
            gender = 'И'

        phone = self.phone.text()
        seriya = self.seriya.text()
        nomer = self.nomer.text()
        if all([surname, name, secondname, brdata, gender, phone, seriya, nomer]):
            self.main.hotel_res.append([surname, name, secondname, brdata, gender, phone, seriya, nomer])
            self.main.main.saveChanges(
                'Добавил постояльца: ' + '; '.join([surname, name, secondname, brdata, gender, phone, seriya, nomer]))
            self.exit_func()
        else:
            pass

    def exit_func(self):
        self.main.loadTable(self.main.persons)
        self.main.show()
        self.close()


if __name__ == '__main__':
    Main()
