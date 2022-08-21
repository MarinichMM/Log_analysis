# -*- coding: UTF-8 -*-
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QFileDialog
import threading
import toml
import os
import pandas as pd
import csv
import os.path
import re
import sys
import time

def read_toml(file_path):
    with open(file_path, "r") as f:
        return toml.load(f)
config = read_toml('Config_file.ini')


name_a_shared_csv = config['Name_a_shared_csv'] # имя общего csv файла для одного лог файла
CPU_load = config['CPU_load']
User_byte = config['User_bytes']

def creating_a_shared_csv(name_folder):
    if os.path.exists(f'{name_a_shared_csv}.csv') != True:
        files = os.listdir(path=f"{name_folder}")
        with open(f'{name_folder}\{name_a_shared_csv}.csv', 'w', newline='') as file:
            header = [(
                'Дата',
                'Время',
                'ID пользователя',
                'Суть проблемы',
                'Значение проблемного показателя'
            )]
            writer = csv.writer(file, delimiter=';')
            writer.writerows(header)
            i = 0
            while i < len(files):
                if files[i] != f'{name_a_shared_csv}.csv':
                    anime = pd.read_csv(f'{name_folder}\{files[i]}', encoding='windows-1251', sep=';', skiprows=[0], header=None)


                    r = anime[anime[9] >= 0]
                    r = r.sort_values(by=[9], ascending=False).head(1)

                    zn_bytes = int(r[9][:1])
                    if zn_bytes > User_byte:
                        name_user = r[2][:1]
                        name_user = list(name_user)[0].split('@')[0]
                        message = 'Проблемы с каналом связи'

                        date, time, users_butes = r[0][:1].item(), r[1][:1].item(), str(r[9][:1].item()) + '  кол-во байт в очереди'
                        frame = [date, time, name_user, message, users_butes]

                        writer = csv.writer(file, delimiter=';')
                        writer.writerow(frame)


                    CPU = anime[anime[3] >= 0]
                    CPU = CPU.sort_values(by=[3], ascending=False).head(1)

                    load_CPU = int(CPU[3][:1])
                    if load_CPU > CPU_load:
                        name_user = CPU[2][:1]
                        name_user = list(name_user)[0].split('@')[0]
                        message = 'Загрузка ЦП'

                        date, time, load = CPU[0][:1].item(), CPU[1][:1].item(), str(CPU[3][:1].item()) + '%' + '  загрузка ЦП'
                        frame = [date, time, name_user, message, load]

                        writer = csv.writer(file, delimiter=';')
                        writer.writerow(frame)

                i += 1


def create_user_csv(ID_user, name_folder, folder_path_log):
    #name_user = ID_user.split('@')[0]
    #print('Name_user:::', name_user) # 1
    #folder_path = os.getcwd()
    #print('Name_folder:', name_folder) # vs_stat_svc_000000a06aab935d@ua7dv.trueconf.name#vcs
    #print('Folder_path:', folder_path) # C:\Users\marinich\PycharmProjects\Marinich  !!! пока не использую
    #print('Folder_path_log:', folder_path_log) # C:/TrueConf/svc_logs/vs_stat_svc_000000a06aab935d@ua7dv.trueconf.name#vcs.txt

    if '/' in ID_user:
        name_user = ID_user.split('/')[0]
        name_user = name_user.split('@')[0]

    elif '!' in ID_user:
        name_user = ID_user.split('!')[1]

    else:
        name_user = ID_user.split('@')[0]


    if os.path.exists(f'{name_folder}/{name_user}.csv') != True:
        with open(f'{name_folder}\{name_user}.csv', 'w', newline='') as file:
            header = [(
                'Дата',
                'Время',
                'ID пользователя',
                'Загрузка ЦП',
                'rcv',
                'audio',
                'Bndph',
                'Bndes',
                'Pkt',
                'Bytes',
                'vpart'
            )]
            writer = csv.writer(file, delimiter=';')
            writer.writerows(header)
            with open(f'{folder_path_log}', 'r') as f: # r'C:\Users\marinich\Desktop\vs_stat_svc_00000065214657dc@ua7dv.trueconf.name#vcs.txt'
                while True:
                    row_data = f.readline()
                    ch = r'(\)'.split('(')[1].split(')')[0]
                    row_data = row_data.replace(ch, '!')
                    if not row_data:
                        break
                    patter = r"(\d{2}/\d{2}/\d{4})\s(\d{2}:\d{2}:\d{2})\|\s+"f'({ID_user})'r"\s\:\s+\d+\,\s+(\d+)\s\|\s+(\d+)\s+\S\s+(\d+)\,\s+\d+\S\,\s+(\d+)\,\s+(\d+)\,\s+(\d+)\,\s+(\d+)\|\s+(\d+\s+\S\s+\d+)\,"
                    line_user = re.findall(patter, row_data)
                    if line_user != []:
                        date, time, load, rcv, audio, bndhp, bndes, pkt, users_butes, vpart = line_user[0][0], line_user[0][1], line_user[0][3], line_user[0][4], line_user[0][5], line_user[0][6], line_user[0][7], line_user[0][8], line_user[0][9], line_user[0][10]

                        lst = [date, time, name_user, load, rcv, audio, bndhp, bndes, pkt, users_butes, vpart]

                        writer = csv.writer(file, delimiter=';') # ,lineterminator="\r"
                        writer.writerow(lst)





def parse(row_data,name_folder, folder_path_log):
    ch = r'(\)'.split('(')[1].split(')')[0]
    row_data = row_data.replace(ch, '!')
    pattern = r"(\d{2}/\d{2}/\d{4})\s(\d{2}:\d{2}:\d{2})\|\s+(\S+)\s\:\s+\d+\,\s+(\d+)\s\|\s+\d+\s+\S\s+\d+\,\s+\d+\S\,\s+(\d+)\,\s+\d+\,\s+(\d+)\,\s+(\d+)\|"
    line = re.findall(pattern, row_data)
    if line != []:
        #print(line) # [('01/08/2022', '17:03:13', '1@ua7dv.trueconf.name/456764466', '70', '65535', '500', '40')]
        ID_user, load, pkt, users_bytes = line[0][2], line[0][3], line[0][5], line[0][6]
        users_bytes = int(users_bytes)

        if users_bytes > User_byte:
            if not os.path.isdir(name_folder):
                os.mkdir(name_folder)
            create_user_csv(ID_user, name_folder, folder_path_log)





class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        self.setWindowTitle('Парсер svc_logs')
        self.setGeometry(300, 200, 600, 300)

        self.createMenuBar()

        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setReadOnly(True)   # запрещает пользователю редактировать текст

        self.setCentralWidget(self.text_edit)

        self.button = QtWidgets.QPushButton(self)
        self.button.move(200, 250)
        self.button.setText('Анализ')
        self.button.setFixedWidth(200) # укзываем ширину кнопки
        self.button.setFixedHeight(40) # указываем высоту кнопки
        self.button.setEnabled(False)
        self.button.clicked.connect(self.flow1)



    def start_analysis(self):

        self.text_edit.append('Начало выполнения скрипта...\n\n')
        self.button.setEnabled(False)
        print('Начало выполнения скрипта...')
        try:
            start_time = time.time()
            i = 0
            ch = 0
            while i < len(self.fnames):
                with open(self.fnames[i], 'r') as f:
                    name_folder = '.'.join(self.fnames[i].split('/')[-1].split('.')[:-1])
                    #print('Name_folder:', name_folder) # vs_stat_svc_000000a06aab935d@ua7dv.trueconf.name#vcs
                    folder_path_log = self.fnames[i]
                    #print('Folder_path_log:', folder_path_log) # C:/TrueConf/svc_logs/vs_stat_svc_000000a06aab935d@ua7dv.trueconf.name#vcs.txt
                    while True:
                        row_data = f.readline()

                        if not row_data:
                            break
                        if re.sub(r"\s+$", "", row_data).endswith('|'):
                            parse(row_data, name_folder, folder_path_log)

                    if os.path.isdir(name_folder):
                        creating_a_shared_csv(name_folder)
                    i += 1



            self.text_edit.append('\n')
            self.text_edit.append('Конец выполнения...')
            print('Конец выполнения ...')
            print("--- %s seconds ---" % (time.time() - start_time))
            self.text_edit.append("--- %s seconds ---" % round ((time.time() - start_time), 3))


        except FileNotFoundError:
            print('No such File')
        self.button.setEnabled(False)

# ---------------ПОТОК------------------
    def flow1(self):  # метод вызова функции start_analysis в отдельном потоке
        t = threading.Thread(target=self.start_analysis)
        t.start()
# --------------------------------------

    def createMenuBar(self):
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        fileMenu = QMenu('&Файл', self)
        self.menuBar.addMenu(fileMenu)

        fileMenu.addAction('Открыть', self.action_clicked)
        fileMenu.addSeparator()
        fileMenu.addAction('Выход из программы', self.action_clicked)



    @QtCore.pyqtSlot()
    def action_clicked(self):

        action = self.sender()
        if action.text() == 'Открыть':
            print('Open')
            self.fnames = QFileDialog.getOpenFileNames(self)[0]   # QFileDialog.getOpenFileNames(self)[0] для открытия нескольких файлов

            if self.fnames != None and self.fnames != [] :
                self.button.setEnabled(True)

            self.text_edit.clear()

        elif action.text() == 'Выход из программы':
            sys.exit(app.exec_())




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

# САБИЛЬНАЯ ВЕРСИЯ!