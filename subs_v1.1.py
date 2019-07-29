# -*- coding: utf-8 -*-
import os
import calendar
import pandas as pd
from datetime import datetime, date
from dbfread import DBF
import time
from generate_xml import add_gen_new
import re
import uuid
import math

basedir = os.path.abspath(os.path.dirname(__file__))

class Empty_string(Exception):
    def __init__(self, value):
        self.msg = value

    def __str__(self):
        return self.msg

class Checking_the_amount(Exception):
    def __init__(self, value):
        self.msg = value

    def __str__(self):
        return self.msg


def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

def isNaN(num):
    return num != num

def check_snils(snils, digits=True):
    if snils:
        #print(snils)
        if len(re.sub(r'[^0-9]+', r'', snils)) != 11:
            return False

        def snils_csum(snils):
            k = range(9, 0, -1)

            pairs = zip(k, [int(x) for x in re.sub(r'[^0-9]+', r'', snils)[:-2]])
            return sum([k * v for k, v in pairs])

        csum = snils_csum(snils)

        while csum > 101:
            csum %= 101
        if csum in (100, 101):
            csum = 0

        return csum == int(re.sub(r'[^0-9]+', r'', snils)[-2:])
    else:
        return False

# Чтение путей файлов и кодов
def path_read(dbf_file):
    try:
        path = []
        kod = []
        for record in DBF(dbf_file, encoding='866'):
            if not record['WAY'] == '':
                path.append(str(record['WAY']))
            if not record['KOD_POST'] == '':
                kod.append(str(record['KOD_POST']))
        path_and_kod = dict(zip(kod, path))
        return path_and_kod
    except PermissionError as e:
        print('Ошибка, нет доступа к файлу: {}'.format(dbf_file))
    except FileNotFoundError as e:
        print('Ошибка, нет такого файла: {}'.format(dbf_file))

# Чтение кодов МСП из dbf файла
def msp_read(dbf_file):
    try:
        msz = []
        kodk = []
        for record in DBF(dbf_file, encoding='866'):
            if not record['ID_MSZ'] == '':
                msz.append(str(record['ID_MSZ']))
            if not record['ID_KAT'] == '':
                kodk.append(str(record['ID_KAT']))
        return msz[0], kodk[0]
    except PermissionError as e:
        print('Ошибка, нет доступа к файлу: {}'.format(dbf_file))
    except FileNotFoundError as e:
        print('Ошибка, нет такого файла: {}'.format(dbf_file))

def write_xml(factes):
    try:
        if factes:

            main_table = pd.DataFrame(factes)
            main_table.sort_values("FamilyName", inplace=True)
            # main_table.drop_duplicates(subset=['SNILS', 'LMSZID', 'dateStart', 'dateFinish'], keep='last', inplace=True)
            # writer = pd.ExcelWriter("Субсидии_{}_{}.xlsx".format(name, dn.strftime('%Y-%m-%d')))
            # main_table.to_excel(writer, 'Субсидии', index=True)
            # writer.save()
            add_gen_new(main_table)
    except Exception as e:
        print('Внимание! Найдены ошибки в файлах, необходимо их устранить и запустить программу еще раз, текст ошибки:', e)

def err(text, filename, index, name, e):
    print('Ошибка {} в файле: {} Index:{} Описание ошибки: {}'.format(text, filename, index + 2, e))
    with open(os.path.join(basedir, '{}_errors.txt'.format(name)), "a", encoding='utf-8') as file:
        file.write('Ошибка {} в файле: {} Index:{} Описание ошибки: {}'.format(text, filename, index + 2, e) + '\n')

def pars_xls(pattern):
    dn = datetime.now()
    msz, kodk = msp_read(os.path.join(basedir, "path\\dbf\\Z_EGISSO.DBF"))
    dict = path_read(os.path.join(basedir, "path\\dbf\\LGOTWAY.DBF"))
    factes = {
        'ID': [],
        'OSZCode': [],
        'SNILS': [],
        'FamilyName': [],
        'FirstName': [],
        'Patronymic': [],
        'Gender': [],
        'BirthDate': [],
        'LMSZID': [],  # Мера соц поддержки ID_MSZ,C,36
        'categoryID': [],  # Код категории ID_KAT,C,36
        'decisionDate': [],
        'dateStart': [],
        'dateFinish': [],
        'usingSign': [],
        'amount': [],
        'measuryCode': [],
        'lastChanging': [],
    }

    for kod, dir in dict.items():
        try:
            for filename in os.listdir(dir):
                name, extension = os.path.splitext(filename)
                if re.search("".join(pattern), name):
                    print(''.center(100, '_') + '\n')
                    if extension.lower() in [".xls", ".xlsx"]:
                        print('Обработка файла: {}'.format(os.path.join(dir, filename)))
                        try:
                            xl = pd.ExcelFile(os.path.join(dir, filename))
                            df = xl.parse(xl.sheet_names[0])
                            i = 0
                            for index, line in df.iterrows():
                                flag_error = False
                                if i >= 5000:
                                    i = 0
                                    write_xml(factes)
                                    for key, value in factes.items():
                                        value.clear()
                                try:
                                    ################ Проверка на ошибки #############################################
                                    if isNaN(line['SNILS']):
                                        err("поля SNILS", os.path.join(dir, filename), index, name, "Пустое поле ['SNILS']")
                                        flag_error = True
                                    else:
                                        if not check_snils(str(line['SNILS'])):
                                            err("поля SNILS", os.path.join(dir, filename), index, name, "Неверный формат СНИЛС")
                                            flag_error = True
                                    if isNaN(line['FM']):
                                        err("поля FM", os.path.join(dir, filename), index, name, "Пустое поле ['FM']")
                                        flag_error = True
                                    if isNaN(line['IM']):
                                        err("поля IM", os.path.join(dir, filename), index, name, "Пустое поле ['IM']")
                                        flag_error = True
                                    if isNaN(line['OT']):
                                        err("поля OT", os.path.join(dir, filename), index, name, "Пустое поле ['OT']")
                                        flag_error = True
                                    if isNaN(line['POL']):
                                        err("поля POL", os.path.join(dir, filename), index, name, "Пустое поле ['POL']")
                                        flag_error = True
                                    if isNaN(line['DTR']):
                                        err("поля DTR", os.path.join(dir, filename), index, name, "Пустое поле ['DTR']")
                                        flag_error = True
                                    if isNaN(line['SUBS']):
                                        err("поля SUBS", os.path.join(dir, filename), index, name, "Пустое поле ['SUBS']")
                                        flag_error = True
                                    else:
                                        if not float(line['SUBS']) > 0:
                                            err("поля SUBS", os.path.join(dir, filename), index, name,
                                                "Сумма начислений поля SUBS, отрицательное число либо ноль")
                                            flag_error = True

                                    # ################ Если ошибок нет #################################################
                                    if not flag_error:
                                        factes['ID'].append(str(uuid.uuid4()))
                                        factes['OSZCode'].append(kod)
                                        factes['SNILS'].append(re.sub(r'[^0-9]+', r'', str(line['SNILS'])))
                                        factes['FamilyName'].append(str(line['FM']).replace(' ', ''))
                                        factes['FirstName'].append(str(line['IM']).replace(' ', ''))
                                        factes['Patronymic'].append(str(line['OT']).replace(' ', ''))
                                        if line['POL'].lower() == "м":
                                            factes['Gender'].append('Male')
                                        else:
                                            factes['Gender'].append('Female')
                                        if type(line['DTR']) == datetime:
                                            factes['BirthDate'].append(line['DTR'].strftime('%Y-%m-%dZ'))
                                        elif type(line['DTR']) == str:
                                            factes['BirthDate'].append(
                                                datetime.strptime(line['DTR'].replace(' ', ''), "%d.%m.%Y").strftime(
                                                    '%Y-%m-%dZ'))
                                        else:
                                            factes['BirthDate'].append(
                                                line['DTR'].to_pydatetime().strftime('%Y-%m-%dZ'))
                                        factes['LMSZID'].append(msz)
                                        factes['categoryID'].append(kodk)
                                        factes['decisionDate'].append(date(int(pattern[1]), int(pattern[0]), 1).strftime('%Y-%m-%dZ'))
                                        factes['dateStart'].append(date(int(pattern[1]), int(pattern[0]), 1).strftime('%Y-%m-%dZ'))
                                        factes['dateFinish'].append(date(int(pattern[1]), int(pattern[0]), calendar.monthrange(int(pattern[1]), int(pattern[0]))[1]).strftime('%Y-%m-%dZ'))
                                        factes['usingSign'].append('0')
                                        factes['amount'].append(toFixed(float(line['SUBS']), 2))
                                        factes['measuryCode'].append(None)
                                        factes['lastChanging'].append(dn.strftime('%Y-%m-%dT%H:%M:%S'))
                                    i+=1
                                except ValueError as e:
                                    print('Ошибка формата в файле: {} Index:{} Описание ошибки: {}'.format(os.path.join(dir, filename), index+2, e))
                                    with open(os.path.join(basedir, '{}_errors.txt'.format(name)), "a", encoding='utf-8') as file:
                                        file.write('Ошибка формата в файле: {} Index:{} Описание ошибки: {}'.format(os.path.join(dir, filename), index+2, e) + '\n')
                                except PermissionError as e:
                                    print('Ошибка, нет доступа к файлу: {}'.format(os.path.join(dir, filename)))
                                    with open(os.path.join(basedir, '{}_errors.txt'.format(name)), "a", encoding='utf-8') as file:
                                        file.write('Ошибка, нет доступа к файлу: {}'.format(os.path.join(dir, filename)) + '\n')
                                except FileNotFoundError as e:
                                    print('Ошибка, нет такого файла: {}'.format(os.path.join(dir, filename)))
                                    with open(os.path.join(basedir, '{}_errors.txt'.format(name)), "a", encoding='utf-8') as file:
                                        file.write('Ошибка, нет такого файла: {}'.format(os.path.join(dir, filename)) + '\n')
                            write_xml(factes)
                        except PermissionError as e:
                            print('Ошибка, нет доступа к файлу: {}'.format(os.path.join(dir, filename)))
                            with open(os.path.join(basedir, '{}_errors.txt'.format(name)), "a",
                                      encoding='utf-8') as file:
                                file.write('Ошибка, нет доступа к файлу: {}'.format(os.path.join(dir, filename)) + '\n')


        except FileNotFoundError as e:
            print('Ошибка, Системе не удается найти указанный путь: {}'.format(dir))

if __name__ == '__main__':
    def Menu():
        """Меню работы с программой"""
        loop = True
        while loop:
            print("""
     1. Генерация xml файлов субсидии
     2. Выход
        """)
            response = input('-> ')

            if response == '1':
                pattern = input('Введите через пробел за какой месяц и год необходимо выгрузть субсидии:' + '\n' + '-> ').split(' ')
                start = time.monotonic()
                if len(pattern) == 2:
                    pars_xls(pattern) #Генерация xml файлов субсидии
                result = time.monotonic() - start
                print("Время работы программы: {:>.3f}".format(result) + " секунд.")
            elif response == '2':  # Выход
                loop = False
            else:
                print('Неверно. Повторите ввод.')

    Menu()
