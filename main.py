import csv
import os
import datetime
import sys
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem, QDateEdit, QStackedWidget, \
    QVBoxLayout, QLabel


class Main():
    def __init__(self):
        self.user = ''
        self.work_w = ''
        self.main_w = ''
        self.adm_and_menegers = {}
        self.loadAdmAndMenagers()
        print(self.adm_and_menegers)
        self.timer_second = 0
        self.timer = self.getTimerStatus()
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
            if now.minute == int(state[1].split(':')[1]) and now.hour == int(
                    state[1].split(':')[0]) and now.second < int(state[1].split(':')[2]):
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
        self.f = True
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
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        self.timer_start()
        self.update_gui()

    def timer_start(self):
        self.time_left_int = self.DURATION_INT

        self.my_qtimer = QtCore.QTimer(self)
        self.my_qtimer.timeout.connect(self.timer_timeout)
        self.my_qtimer.start(1000)

        self.update_gui()

    def timer_timeout(self):
        if self.f:
            self.time_left_int -= 1
            self.main.main.timer_second -= 1
            if self.time_left_int <= 0:
                self.main.main.timer = False
                self.close()
                self.f = False
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
                win = WarningWindow(self, 'Вошёл: ' + self.main.user + '\nЕго Роль: ' +
                                    self.main.adm_and_menegers[login]['work'])
                win.show()
                self.main.openMangerAndAdminWindow(self.main.adm_and_menegers[login]['work'])
            else:
                win = WarningWindow(self, login + '    ' + password + ': Некорректный пароль')
                win.show()
                self.trys += 1
                print(login + '    ' + password + ': Некорректный пароль')
                self.trys_list.append(login + '    ' + password + ': Некорректный пароль')
        else:
            self.trys += 1
            win = WarningWindow(self, login + '    ' + password + ': Некорректный логин')
            win.show()
            print(login + '    ' + password + ': Некорректный логин')
            self.trys_list.append(login + '    ' + password + ': Некорректный логин')
        if self.trys == 3:
            win = WarningWindow(self,
                                'Вы привысили количество неверных попыток ввода. \nПодождите, Прежде чем пытаться войти снова')
            win.show()
            self.trys = 0
            self.main.timer_second = 60
            self.main.timer = True
            now = datetime.datetime.now()
            file = open('timerStatus.txt', 'w')
            file.write('True\n' + str(now.hour) + ':' + str(now.minute + 1) + ':' + str(now.second))
            self.timer_start(self.main.timer_second)

    def timer_start(self, sec):
        print(sec)
        win = MyTimer(sec, self)
        win.show()

    def exit_func(self):
        exit(0)


class Manager(QMainWindow):
    def __init__(self, main):
        super().__init__(main)
        self.main = main
        uic.loadUi('Manager.ui', self)
        self.table_state = None
        self.table.itemSelectionChanged.connect(self.selectRow)

        self.f_name_hotels = 'hotels.csv'
        self.f_name_admins = 'admins.csv'

        self.showall.clicked.connect(self.showAllHotels)
        self.showalladm.clicked.connect(self.showAllAdmins)
        self.addadm.clicked.connect(self.addAdmin)
        self.createhotel.clicked.connect(self.addHotel)
        self.exit.clicked.connect(self.exit_func)

        self.edithotel.clicked.connect(self.editHotel)
        self.deletehotel.clicked.connect(self.delHotel)

        self.destroyadmslife.clicked.connect(self.delAdmin)

        self.hotel_res = []
        self.admins_res = []
        self.loadHotels()
        self.loadAdmins()

    def editHotel(self):
        temp = [(i.row(), i.text(), i.column()) for i in self.table.selectedItems()]
        temp.sort(key=lambda u: u[2])
        temp = [i[1] for i in temp]
        index = self.hotel_res.index(temp)
        win = EditHotelWindow(self, temp, index)
        win.show()

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

    def selectRow(self):
        self.edithotel.setEnabled(False)
        self.deletehotel.setEnabled(False)
        self.destroyadmslife.setEnabled(False)
        temp = [(i.row(), i.text(), i.column()) for i in self.table.selectedItems()]
        temp.sort(key=lambda u: u[2])
        if self.table_state == 'hotels':
            if len(temp) == len(self.hotel_res[0]):
                self.edithotel.setEnabled(True)
                self.deletehotel.setEnabled(True)
        else:
            if len(temp) == len(self.admins_res[0]):
                self.destroyadmslife.setEnabled(True)

    def showAllHotels(self):
        self.table_state = 'hotels'
        self.loadTable(self.hotel_res)

    def showAllAdmins(self):
        self.table_state = 'admins'
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

    def delAdmin(self):
        temp = [(i.row(), i.text(), i.column()) for i in self.table.selectedItems()]
        temp.sort(key=lambda u: u[2])
        temp = [i[1] for i in temp]
        indx = self.admins_res.index(temp)
        del self.admins_res[indx]
        self.save()

    def addHotel(self):
        win = AddHotelWindow(self)
        win.show()
        self.hide()

    def delHotel(self):
        temp = [(i.row(), i.text(), i.column()) for i in self.table.selectedItems()]
        temp.sort(key=lambda u: u[2])
        temp = [i[1] for i in temp]
        indx = self.hotel_res.index(temp)
        if self.hotel_res[indx][2] == '0':
            del self.hotel_res[indx]
            os.remove('hotels/' + temp[0] + '.csv')
            self.save()
        else:
            win = WarningWindow(self, 'Нельзя удалить гостинницу с которой связаны номера.\n '
                                      'Чтобы удалить номера обратитесь к одному из администраторов гостиницы')
            win.show()


class Admin(QMainWindow):
    def __init__(self, main, hotel):
        super().__init__(main)
        self.hotel = 'hotels/' + hotel + '.csv'
        self.persons_file = 'persons.csv'
        self.main = main
        uic.loadUi('Admin.ui', self)
        self.table_state = None
        self.table.itemSelectionChanged.connect(self.selectRow)

        self.showall.clicked.connect(self.showAllRooms)
        self.createroom.clicked.connect(self.addRoom)
        self.edithotel.clicked.connect(self.editRoom)
        self.deletehotel.clicked.connect(self.deleteRoom)

        self.showpeople.clicked.connect(self.showAllPersons)
        self.addperson.clicked.connect(self.addPerson)
        self.abateperson.clicked.connect(self.editPerson)
        self.destroypersonslife.clicked.connect(self.deletePerson)
        self.givehome.clicked.connect(self.giveHome)
        self.takehome.clicked.connect(self.takeHome)
        self.exit.clicked.connect(self.exit_func)

        self.rooms = []
        self.persons = []
        self.loadPersons()
        self.loadRooms()

    def selectRow(self):
        self.edithotel.setEnabled(False)
        self.deletehotel.setEnabled(False)
        self.destroypersonslife.setEnabled(False)
        self.abateperson.setEnabled(False)
        self.takehome.setEnabled(False)
        temp = [(i.row(), i.text(), i.column()) for i in self.table.selectedItems()]
        temp.sort(key=lambda u: u[2])
        if self.table_state == 'persons':
            if len(temp) == len(self.persons[0]):
                self.destroypersonslife.setEnabled(True)
                self.abateperson.setEnabled(True)
                if temp[-1][1] != 'False':
                    self.takehome.setEnabled(True)
        else:
            if len(temp) == len(self.rooms[0]):
                self.edithotel.setEnabled(True)
                self.deletehotel.setEnabled(True)

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

    def showAllRooms(self):
        self.table_state = 'rooms'
        self.loadTable(self.rooms)

    def loadRooms(self):
        with open(self.hotel, encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='\'')
            self.rooms = [row for index, row in enumerate(reader)]

    def addRoom(self):
        win = AddRoomWindow(self)
        win.show()
        self.hide()

    def editRoom(self):
        temp = [(i.row(), i.text(), i.column()) for i in self.table.selectedItems()]
        temp.sort(key=lambda u: u[2])
        temp = [i[1] for i in temp]
        index = self.rooms.index(temp)
        win = EditRoomWindow(self, temp, index)
        win.show()

    def deleteRoom(self):
        temp = [(i.row(), i.text(), i.column()) for i in self.table.selectedItems()]
        temp.sort(key=lambda u: u[2])
        temp = [i[1] for i in temp]
        if temp[-1] != 'True':
            self.main.saveChanges('Удалил постояльца:' + '; '.join(temp))
            file = open('hotels.csv', 'r', encoding='utf8')
            text = file.read().split('\n')
            file.close()
            file = open('hotels.csv', 'w', encoding='utf8')
            res = []
            for i in text:
                if i.split(';')[0] == self.hotel.split('.')[0][-1]:
                    res.append(';'.join(i.split(';')[:2] + [str(int(i.split(';')[2]) - 1)] + i.split(';')[3:]))
                    continue
                res.append(i)
            file.write('\n'.join(res))
            file.close()
            del self.rooms[self.rooms.index(temp)]
            self.save()
            self.showAllRooms()
        else:
            win = WarningWindow(self, 'Невозможно удалить номер, в котором проживает постоялец.')
            win.show()

    def showAllPersons(self):
        self.table_state = 'persons'
        self.loadTable(self.persons)

    def loadPersons(self):
        with open(self.persons_file, encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='\'')
            self.persons = [row for index, row in enumerate(reader)]

    def addPerson(self):
        win = AddPersonWindow(self)
        win.show()
        self.hide()

    def editPerson(self):
        temp = [(i.row(), i.text(), i.column()) for i in self.table.selectedItems()]
        temp.sort(key=lambda u: u[2])
        temp = [i[1] for i in temp]
        index = self.persons.index(temp)
        win = EditPersonWindow(self, temp, index)
        win.show()

    def deletePerson(self):
        temp = [(i.row(), i.text(), i.column()) for i in self.table.selectedItems()]
        temp.sort(key=lambda u: u[2])
        temp = [i[1] for i in temp]
        print(temp[-1])
        if temp[-1] == 'False':
            self.main.saveChanges('Удалил постояльца:' + '; '.join(temp))
            del self.persons[self.persons.index(temp)]
            self.save()
            self.showAllPersons()
        else:
            win = WarningWindow(self, 'Невозможно удалить постояльца, который проживает в настоящий момент в номере.')
            win.show()

    def giveHome(self):
        win = GiveHomeWindow(self)
        win.show()

    def takeHome(self):
        temp = [(i.row(), i.text(), i.column()) for i in self.table.selectedItems()]
        temp.sort(key=lambda u: u[2])
        temp = [i[1] for i in temp]
        self.persons[self.persons.index(temp)][-1] = 'False'
        indx = 0
        for i in self.rooms:
            if i[0] == temp[-1]:
                indx = self.rooms.index(i)
                break
        self.rooms[indx][-1] = 'False'
        self.save()
        self.main.saveChanges(
            'Выселил постояльца: ' + '; '.join(self.persons[indx]) + ' из номера ' + temp[-1])
        self.showAllPersons()


class GiveHomeWindow(QMainWindow):
    def __init__(self, main):
        super().__init__(main)
        self.main = main
        uic.loadUi('pinok.ui', self)
        self.people.addItems([' '.join(i[:3] + i[-3:-1]) for i in self.main.persons if i[-1] == 'False'])
        self.numberofhostel.addItems([i[0] for i in self.main.rooms if i[-1] == 'False'])
        self.people.setCurrentIndex(0)
        self.numberofhostel.setCurrentIndex(0)
        self.enter.clicked.connect(self.giveHome)
        self.exit.clicked.connect(self.exit_func)

    def giveHome(self):
        people = self.people.itemText(self.people.currentIndex())
        numberofhostel = self.numberofhostel.itemText(self.numberofhostel.currentIndex())
        if all([people, numberofhostel]):
            indx = 0
            for i in self.main.persons:
                if people.split()[-1] == i[-2] and people.split()[-2] == i[-3]:
                    indx = self.main.persons.index(i)
                    break
            self.main.persons[indx][-1] = numberofhostel
            self.main.main.saveChanges(
                'Вселил постояльца: ' + '; '.join(self.main.persons[indx]) + ' в номер ' + numberofhostel)
            indx = 0
            for i in self.main.rooms:
                if numberofhostel == i[0]:
                    indx = self.main.rooms.index(i)
                    break
            self.main.rooms[indx][-1] = 'True'
            self.main.save()
            self.exit_func()
        else:
            win = WarningWindow(self, 'Не все поля заполнены')
            win.show()

    def exit_func(self):
        self.main.loadTable(self.main.persons)
        self.main.show()
        self.close()


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
            self.main.save()
            self.exit_func()
        else:
            win = WarningWindow(self, 'Не все поля заполнены')
            win.show()

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
            self.main.save()
            file = open('hotels/' + number + '.csv', 'w', encoding='utf8')
            file.write('Номер;Количество комнат;Площадь номера;Статус заселённости\n' +
                       '\n'.join([str(i) + ';1;20;False' for i in range(1, int(rooms) + 1)]))
            file.close()
            self.exit_func()
        else:
            win = WarningWindow(self, 'Не все поля заполнены')
            win.show()

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
        brdata = self.brdata.text()
        gender = ''
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
            self.main.persons.append([surname, name, secondname, brdata, gender, phone, seriya, nomer, 'False'])
            self.main.main.saveChanges(
                'Добавил постояльца: ' + '; '.join(
                    [surname, name, secondname, brdata, gender, phone, seriya, nomer, 'False']))
            self.main.save()
            self.exit_func()
        else:
            win = WarningWindow(self, 'Не все поля заполнены')
            win.show()

    def exit_func(self):
        self.main.loadTable(self.main.persons)
        self.main.show()
        self.close()


class AddRoomWindow(QMainWindow):
    def __init__(self, main):
        super().__init__(main)
        uic.loadUi('addnomer.ui', self)
        self.main = main
        self.enter.clicked.connect(self.add)
        self.exit.clicked.connect(self.exit_func)

    def add(self):
        number = self.number.text()
        rooms_2 = self.rooms_2.text()
        sqrt = self.sqrt.text()
        if all([number, rooms_2, sqrt]):
            self.main.rooms.append([number, rooms_2, sqrt, 'False'])
            file = open('hotels.csv', 'r', encoding='utf8')
            text = file.read().split('\n')
            print(text)
            file.close()
            file = open('hotels.csv', 'w', encoding='utf8')
            res = []
            for i in text:
                if i.split(';')[0] == self.main.hotel.split('.')[0][-1]:
                    res.append(';'.join(i.split(';')[:2] + [str(int(i.split(';')[2]) + 1)] + i.split(';')[3:]))
                    continue
                res.append(i)
            print(res)
            file.write('\n'.join(res))
            file.close()

            self.main.main.saveChanges(
                'Добавил номер в свою гостиницу: ' + '; '.join([number, rooms_2, sqrt, 'False']))
            self.main.save()
            self.exit_func()

    def exit_func(self):
        self.main.loadTable(self.main.rooms)
        self.main.show()
        self.close()


class EditHotelWindow(QMainWindow):
    def __init__(self, main, lst, index):
        super().__init__(main)
        self.indx = index
        uic.loadUi('addhot.ui', self)
        self.main = main
        self.nomer = lst[0]
        self.number.setText(lst[0])
        self.floors.setText(lst[1])
        self.rooms.setText(lst[2])
        temp = lst[3].split(', ')
        self.country.setText(temp[0])
        self.city.setText(temp[1])
        self.street.setText(temp[2])
        self.house.setText(temp[3])
        self.floors.setEnabled(False)
        self.rooms.setEnabled(False)

        self.enter.clicked.connect(self.edit)
        self.exit.clicked.connect(self.exit_func)

    def edit(self):
        number = self.number.text()
        floors = self.floors.text()
        rooms = self.rooms.text()
        country = self.country.text()
        city = self.city.text()
        street = self.street.text()
        house = self.house.text()
        if all([number, floors, rooms, country, city, street, house]):
            self.main.hotel_res[self.indx] = [number, floors, rooms, ', '.join([country, city, street, house])]
            os.renames('hotels/' + str(self.nomer) + '.csv', 'hotels/' + str(number) + '.csv')
            print(2)
            for i in self.main.admins_res:
                if i[-1] == self.nomer:
                    i[-1] = number
            print(3)
            self.main.main.saveChanges(
                'Отредактировал гостиницу: ' + '; '.join(
                    [number, floors, rooms, ', '.join([country, city, street, house])]))
            self.main.save()
            self.exit_func()

    def exit_func(self):
        self.main.loadTable(self.main.hotel_res)
        self.main.show()
        self.close()


class EditRoomWindow(QMainWindow):
    def __init__(self, main, lst, index):
        super().__init__(main)
        self.indx = index
        uic.loadUi('addnomer.ui', self)
        self.main = main
        self.number.setText(lst[0])
        self.rooms_2.setText(lst[1])
        self.sqrt.setText(lst[2])

        self.enter.clicked.connect(self.edit)
        self.exit.clicked.connect(self.exit_func)

    def edit(self):
        number = self.number.text()
        rooms_2 = self.rooms_2.text()
        sqrt = self.sqrt.text()
        if all([number, rooms_2, sqrt]):
            self.main.rooms[self.indx] = [number, rooms_2, sqrt, self.main.rooms[self.indx][-1]]
            self.main.main.saveChanges(
                'Отредактировал номер: ' + '; '.join(self.main.rooms[self.indx]))
            self.main.save()
            self.exit_func()
        else:
            win = WarningWindow(self, 'Не все поля заполнены')
            win.show()

    def exit_func(self):
        self.main.loadTable(self.main.rooms)
        self.main.show()
        self.close()


class EditPersonWindow(QMainWindow):
    def __init__(self, main, lst, index):
        super().__init__(main)
        self.indx = index
        uic.loadUi('tupielyudishki.ui', self)
        self.main = main
        self.surname.setText(lst[0])
        self.name.setText(lst[1])
        self.secondname.setText(lst[2])
        self.brdata.setDate(QtCore.QDate(*list(map(int, lst[3].split('.')))))
        if lst[4] == 'Ж':
            self.female.setChecked(True)
        elif lst[4] == 'М':
            self.male.setChecked(True)
        else:
            self.alian.setChecked(True)
        self.phone.setText(lst[5])
        self.seriya.setText(lst[6])
        self.nomer.setText(lst[7])

        self.enter.clicked.connect(self.edit)
        self.exit.clicked.connect(self.exit_func)

    def edit(self):
        surname = self.surname.text()
        name = self.name.text()
        secondname = self.secondname.text()
        brdata = self.brdata.text()
        gender = ''
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
            self.main.persons[self.indx] = [surname, name, secondname, brdata, gender, phone, seriya, nomer,
                                            self.main.persons[self.indx][-1]]
            self.main.main.saveChanges(
                'Отредактировал человека: ' + '; '.join(self.main.persons[self.indx]))
            self.main.save()
            self.exit_func()
        else:
            win = WarningWindow(self, 'Не все поля заполнены')
            win.show()

    def exit_func(self):
        self.main.loadTable(self.main.persons)
        self.main.show()
        self.close()


class WarningWindow(QMainWindow):
    def __init__(self, main, text):
        super().__init__(main)
        self.setGeometry(50, 50, 500, 500)
        self.warning = QLabel(self)
        self.warning.setText(text)
        self.warning.resize(self.warning.sizeHint())
        self.warning.move(250 - self.warning.width() // 2, 250 - self.warning.height() // 2)


if __name__ == '__main__':
    Main()
