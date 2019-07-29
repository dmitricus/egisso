import os
import xml.etree.ElementTree as et
import numpy as np
import pandas as pd
import xmltodict
import time
from dbfread import DBF
import json
from pandas.io.json import json_normalize



from lxml import etree, objectify
from generate_xml import alterationBasedOnPreviousErrors_gen, errorsInvalidation_gen, add_gen,\
    terminationBasedOnRecalculation_gen, add_gen_new

basedir = os.path.abspath(os.path.dirname(__file__))

# что еще нужно доработать:
# оптимизацая работы (ускорение), попробовать использовать lxml парсинг
# распаралелить процессы парсинга, один процесс на файл, очереди
# сделать обвязку замера времени выполнения, использование процессора и максимальное использования памяти
# чтение пнапрямую из архива

#data['dat:data']['pac:package']['pac:packageID'] - >
# ['af:ID', 'af:OSZCode', 'af:MSZ_receiver', 'af:LMSZID', 'af:categoryID', 'af:decision_date', 'af:dateStart', 'af:dateFinish', 'af:needsCriteria', 'af:assignment_info', 'pac:lastChanging']
#'af:needsCriteria' - >
#'af:assignment_info' - >
#'af:MSZ_receiver' - > 'prsn:SNILS', 'smev:FamilyName', 'smev:FirstName', 'smev:Patronymic', 'prsn:Gender', 'prsn:BirthDate'

not_fond_snils = {
    'SNILS': []
}


def snils_read(dbf_file):
    snils = []
    for record in DBF(dbf_file, encoding='866'):
        if not record['STRAH_N'] == '':
            snils.append(str(record['STRAH_N']))
    return snils

def msp_read(dbf_file):
    msp = {}
    for record in DBF(dbf_file, encoding='866'):
        if record['REG_KAT'] == 14:
            msp.update({str(record['ID_MSP']): str(record['ID_KAT'])})
    return msp

def parser_xml(dirpath):
    factes = {
            'ID': [],
            'OSZCode': [],
            'SNILS': [],
            'FamilyName': [],
            'FirstName': [],
            'Patronymic': [],
            'Gender': [],
            'BirthDate': [],
            'rp_SNILS': [],
            'rp_FamilyName': [],
            'rp_FirstName': [],
            'rp_Patronymic': [],
            'rp_Gender': [],
            'rp_BirthDate': [],
            'LMSZID': [],
            'categoryID': [],
            'decisionDate': [],
            'dateStart': [],
            'dateFinish': [],
            'usingSign': [],
            'amount': [],
            #'measuryCode': [],
            'lastChanging': [],
            'previosID': [],
            }

    for dir in os.listdir(dirpath):
        for filename in os.listdir(os.path.join(dirpath, dir)):
            name, extension = os.path.splitext(filename)
            if extension == ".xml":
                print(os.path.join(os.path.join(dirpath, dir), filename))
                if filename == '0988000003_10.06.S_223.xml':
                    with open(os.path.join(os.path.join(dirpath, dir), filename), 'r', encoding='utf-8') as f:
                        data = xmltodict.parse(f.read())

                        try:
                            for line in data['ns5:data']['ns0:package']['ns0:elements']['ns0:fact']:
                                if line['ns1:MSZ_receiver']['ns2:SNILS'] == '12933801357':
                                    factes['ID'].append(line['ns1:ID'])
                                    factes['OSZCode'].append(line['ns1:OSZCode'])
                                    factes['SNILS'].append(line['ns1:MSZ_receiver']['ns2:SNILS'])
                                    factes['FamilyName'].append(line['ns1:MSZ_receiver']['ns3:FamilyName'])
                                    factes['FirstName'].append(line['ns1:MSZ_receiver']['ns3:FirstName'])
                                    try:
                                        factes['Patronymic'].append(line['ns1:MSZ_receiver']['ns3:Patronymic'])
                                    except KeyError:
                                        factes['Patronymic'].append(None)
                                    factes['Gender'].append(line['ns1:MSZ_receiver']['ns2:Gender'])
                                    factes['BirthDate'].append(line['ns1:MSZ_receiver']['ns2:BirthDate'])
                                    factes['rp_SNILS'].append(line['ns1:reason_persons']['ns2:prsnInfo']['ns2:SNILS'])
                                    factes['rp_FamilyName'].append(line['ns1:reason_persons']['ns2:prsnInfo']['ns3:FamilyName'])
                                    factes['rp_FirstName'].append(line['ns1:reason_persons']['ns2:prsnInfo']['ns3:FirstName'])
                                    try:
                                        factes['rp_Patronymic'].append(line['ns1:reason_persons']['ns2:prsnInfo']['ns3:Patronymic'])
                                    except KeyError:
                                        factes['rp_Patronymic'].append(None)
                                    factes['rp_Gender'].append(line['ns1:reason_persons']['ns2:prsnInfo']['ns2:Gender'])
                                    factes['rp_BirthDate'].append(line['ns1:reason_persons']['ns2:prsnInfo']['ns2:BirthDate'])
                                    factes['LMSZID'].append(line['ns1:LMSZID'])
                                    factes['categoryID'].append(line['ns1:categoryID'])
                                    factes['decisionDate'].append(line['ns1:decision_date'])
                                    factes['dateStart'].append(line['ns1:dateStart'])
                                    factes['dateFinish'].append(line['ns1:dateFinish'])
                                    factes['usingSign'].append(line['ns1:needsCriteria']['ns1:usingSign'])
                                    factes['amount'].append(line['ns1:assignment_info']['ns1:monetary_form']['ns1:amount'])
                                    factes['lastChanging'].append(line['ns0:lastChanging'])
                                    try:
                                        factes['previosID'].append(line['ns0:previosID'])
                                    except KeyError:
                                        factes['previosID'].append(None)


                        except TypeError as te:
                            #fact = parser_xml_one(os.path.join(os.path.join(dirpath, dir), filename), msp, snils)
                            '''
                            if fact:
                                factes['ID'].append(fact['ID'])
                                factes['OSZCode'].append(fact['OSZCode'])
                                factes['SNILS'].append(fact['SNILS'])
                                factes['FamilyName'].append(fact['FamilyName'])
                                factes['FirstName'].append(fact['FirstName'])
                                factes['Patronymic'].append(fact['Patronymic'])
                                factes['Gender'].append(fact['Gender'])
                                factes['BirthDate'].append(fact['BirthDate'])
                                factes['LMSZID'].append(fact['LMSZID'])
                                factes['categoryID'].append(fact['categoryID'])
                                factes['decisionDate'].append(fact['decisionDate'])
                                factes['dateStart'].append(fact['dateStart'])
                                factes['dateFinish'].append(fact['dateFinish'])
                                factes['usingSign'].append(fact['usingSign'])
                                factes['amount'].append(fact['amount'])
                                factes['measuryCode'].append(fact['measuryCode'])
                                factes['lastChanging'].append(fact['lastChanging'])
                                # factes['categoryID_new'].append(msp[fact['LMSZID']])
                            '''
                            print('Ошибка', te)
                        except KeyError as e:
                            print('Ошибка в файле {}: KeyError {}'.format(os.path.join(os.path.join(dirpath, dir), filename), e))
                            with open(os.path.join(basedir, 'errors.txt'), "a", encoding='utf-8') as file:
                                file.write('Ошибка в файле {}: {}'.format(os.path.join(os.path.join(dirpath, dir), filename), e) + '\n')

    # Запускаем генерацию xml документа
    for key, fact in factes.items():
        print(key, fact)
    if factes:
        main_table = pd.DataFrame(factes)
        main_table.sort_values("FamilyName", inplace=True)
        #main_table.drop_duplicates(subset=['SNILS', 'LMSZID', 'dateStart', 'dateFinish'], keep='last', inplace=True)

        #writer = pd.ExcelWriter("12933801357.xlsx")
        #main_table.to_excel(writer, 'FACTES', index=True)
        #writer.save()

        add_gen_new(main_table)
        terminationBasedOnRecalculation_gen(main_table)

        # errorsInvalidation_gen(main_table)
        # alterationBasedOnPreviousErrors_gen(main_table)

def parser_xml_one(filename, msp, snils):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = xmltodict.parse(f.read())

        #not_fond_snils['SNILS'].append(
            #data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:MSZ_receiver']['prsn:SNILS'])

        print(filename)
        if not data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:MSZ_receiver']['prsn:SNILS']:
            print('Пустой снилс, ID - {}, файл: {}'.format(data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:ID'], os.path.join(filename)))

        #elif any(map(snils.__contains__, (data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:MSZ_receiver']['prsn:SNILS']))):
        elif data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:MSZ_receiver']['prsn:SNILS'] in snils:
            return {
                    'ID': data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:ID'],
                    'OSZCode': data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:OSZCode'],
                    'SNILS': data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:MSZ_receiver']['prsn:SNILS'],
                    'FamilyName': data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:MSZ_receiver']['smev:FamilyName'],
                    'FirstName': data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:MSZ_receiver']['smev:FirstName'],
                    'Patronymic': data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:MSZ_receiver']['smev:Patronymic'],
                    'Gender': data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:MSZ_receiver']['prsn:Gender'],
                    'BirthDate': data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:MSZ_receiver']['prsn:BirthDate'],
                    'LMSZID': data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:LMSZID'],
                    'categoryID': data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:categoryID'],
                    'decisionDate': data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:decision_date'],
                    'dateStart': data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:dateStart'],
                    'dateFinish': data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:dateFinish'],
                    'usingSign': data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:needsCriteria']['af:usingSign'],
                    'amount': data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:assignment_info']['af:serviceForm']['af:amount'],
                    'measuryCode': data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:assignment_info']['af:serviceForm'][
                        'af:measuryCode'],
                    'lastChanging': data['dat:data']['pac:package']['pac:elements']['pac:fact']['pac:lastChanging'],
                    #'categoryID_new': msp[data['dat:data']['pac:package']['pac:elements']['pac:fact']['af:LMSZID']],
                    }

    except Exception as e:
        print('Ошибка: {}'.format(e))

if __name__ == '__main__':
    # Замеряем время выполнения скрипта
    start = time.monotonic()

    parser_xml(os.path.join('F:\\IKO\\!ЕГИССО\\Выгрузка факта назначения из ЭСРН\\20190318_с_детьми_уходФБ_проверка изм_размеров\\'))

    result = time.monotonic() - start
    print("Program time: {:>.3f}".format(result) + " seconds.")
    '''
    # Список не найденных снилсов
    snils_df = pd.DataFrame(not_fond_snils)
    snils_df.sort_values("SNILS", inplace=True)
    snils_df.drop_duplicates(subset='SNILS', keep='last', inplace=True)
    i = 0
    for snils_line in snils:
        if not snils_line in snils_df['SNILS'].tolist():
            i+=1
            with open(os.path.join(basedir, 'snils.txt'), "a", encoding='utf-8') as file:
                file.write('{}: {}\n'.format(i, snils_line))
    '''