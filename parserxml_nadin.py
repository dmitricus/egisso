import os
import pandas as pd
import xmltodict
import time
from dbfread import DBF


from generate_xml import alterationBasedOnPreviousErrors_gen, errorsInvalidation_gen, add_gen

basedir = os.path.abspath(os.path.dirname(__file__))

not_fond_snils = {
    'SNILS': []
}

# Чтение снилсов из dbf файла
def snils_read(dbf_file):
    snils = []
    for record in DBF(dbf_file, encoding='866'):
        if not record['STRAH_N'] == '':
            snils.append(str(record['STRAH_N']))
    return snils

# Чтение кодов МСП из dbf файла
def msp_read(dbf_file):
    msp = {}
    for record in DBF(dbf_file, encoding='866'):
        if record['REG_KAT'] == 14:
            msp.update({str(record['ID_MSP']): str(record['ID_KAT'])})
    return msp

# Парсинг XML файлов
def parser_xml(dirpath, msp, snils):
    factes = {
            'ID': [],
            'OSZCode': [],
            'SNILS': [],
            'FamilyName': [],
            'FirstName': [],
            'Patronymic': [],
            'Gender': [],
            'BirthDate': [],
            'LMSZID': [],
            'categoryID': [],
            'decisionDate': [],
            'dateStart': [],
            'dateFinish': [],
            'usingSign': [],
            'amount': [],
            'measuryCode': [],
            'lastChanging': [],
            #'categoryID_new': [],
            }
    print(len(snils))
    # проход по папкам
    for dir in os.listdir(dirpath):
        # Получаем файлы в папках
        for filename in os.listdir(os.path.join(dirpath, dir)):
            # получаем имя файла и его расширанеие
            name, extension = os.path.splitext(filename)
            if extension == ".xml":
                print(os.path.join(os.path.join(dirpath, dir), filename))
                with open(os.path.join(os.path.join(dirpath, dir), filename), 'r', encoding='utf-8') as f:
                    data = xmltodict.parse(f.read())
                    try:
                        for line in data['dat:data']['pac:package']['pac:elements']['pac:fact']:
                            #print(line)
                            #print(type(line['af:MSZ_receiver']['prsn:SNILS']))
                            #not_fond_snils['SNILS'].append(line['af:MSZ_receiver']['prsn:SNILS'])
                            if not line['af:MSZ_receiver']['prsn:SNILS']:
                                print('Пустой снилс, ID - {}, файл: {}'.format(line['af:ID'], os.path.join(os.path.join(dirpath, dirpath), filename)))

                            elif line['af:MSZ_receiver']['prsn:SNILS'] in snils:

                                    factes['ID'].append(line['af:ID'])
                                    factes['OSZCode'].append(line['af:OSZCode'])
                                    factes['SNILS'].append(line['af:MSZ_receiver']['prsn:SNILS'])
                                    factes['FamilyName'].append(line['af:MSZ_receiver']['smev:FamilyName'])
                                    factes['FirstName'].append(line['af:MSZ_receiver']['smev:FirstName'])
                                    factes['Patronymic'].append(line['af:MSZ_receiver']['smev:Patronymic'])
                                    factes['Gender'].append(line['af:MSZ_receiver']['prsn:Gender'])
                                    factes['BirthDate'].append(line['af:MSZ_receiver']['prsn:BirthDate'])
                                    factes['LMSZID'].append(line['af:LMSZID'])
                                    factes['categoryID'].append(line['af:categoryID'])
                                    factes['decisionDate'].append(line['af:decision_date'])
                                    factes['dateStart'].append(line['af:dateStart'])
                                    factes['dateFinish'].append(line['af:dateFinish'])
                                    factes['usingSign'].append(line['af:needsCriteria']['af:usingSign'])
                                    factes['amount'].append(line['af:assignment_info']['af:serviceForm']['af:amount'])
                                    factes['measuryCode'].append(line['af:assignment_info']['af:serviceForm']['af:measuryCode'])
                                    factes['lastChanging'].append(line['pac:lastChanging'])
                                    #factes['categoryID_new'].append(msp[line['af:LMSZID']])

                    except TypeError as te:
                        fact = parser_xml_one(os.path.join(os.path.join(dirpath, dir), filename), msp, snils)
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

                    except KeyError as e:
                        print('Ошибка в файле {}: {}'.format(os.path.join(os.path.join(dirpath, dir), filename), e))
                        with open(os.path.join(basedir, 'errors.txt'), "a", encoding='utf-8') as file:
                            file.write('Ошибка в файле {}: {}'.format(os.path.join(os.path.join(dirpath, dir), filename), e) + '\n')

    # Запускаем генерацию xml документа
    if factes:
        main_table = pd.DataFrame(factes)

        main_table.sort_values("LMSZID", inplace=True)
        #main_table.drop_duplicates(subset=['SNILS', 'LMSZID', 'dateStart', 'dateFinish'], keep='last', inplace=True)

        # writer = pd.ExcelWriter("parser_{}.xlsx".format('test'))
        # main_table.to_excel(writer, 'FACTES', index=True)
        # writer.save()

        # add_gen(main_table)
        errorsInvalidation_gen(main_table)
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

    msp = msp_read('D:\\data\\path\\dbf\\SP_801.DBF')
    snils = snils_read('D:\\data\\path\\dbf\\DETI_KOL.DBF')

    parser_xml(os.path.join('D:\\data\\', 'path\\xml'), msp, snils)

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