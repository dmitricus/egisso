# -*- coding: utf-8 -*-
from lxml import etree
import os
from lxml.builder import ElementMaker
import uuid
import random
import datetime
from decimal import Decimal

basedir = os.path.abspath(os.path.dirname(__file__))

# Шаблоны генерации xml документов

def number(num=None):
    if num:
        with open(os.path.join(basedir, 'number.dat'), "w", encoding='utf-8') as file:
            file.write('{}'.format(num))
    else:
        with open(os.path.join(basedir, 'number.dat'), "r", encoding='utf-8') as file:
            return file.read()

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

# 1.5	Добавление факта назначения
def add_gen(factes):
    print(len(factes))

    smev = "urn://x-artefacts-smev-gov-ru/supplementary/commons/1.0.1"
    egisso = "urn://egisso-ru/types/basic/1.0.3"
    prsn = "urn://egisso-ru/types/prsn-info/1.0.2"
    af = "urn://egisso-ru/types/assignment-fact/1.0.2"
    pac = "urn://egisso-ru/types/package-RAF/1.0.2"
    dat = "urn://egisso-ru/msg/10.06.S/1.0.1"

    NSMAP = {
                'smev': smev,
                'egisso': egisso,
                'prsn': prsn,
                'af': af,
                'pac': pac,
                'dat': dat,
            }

    root = etree.Element("{%s}data" % dat, nsmap=NSMAP)
    #root.attrib['xmlns'] = "urn://egisso-ru/types/package-RAF/1.0.5"
    package = etree.SubElement(root, "{%s}package" % pac)
    packageId = etree.SubElement(package, "{%s}packageID" % pac)
    packageId.text = str(uuid.uuid4())
    elements = etree.SubElement(package, "{%s}elements" % pac)


    for index, line in factes.iterrows():
        # Информация о назначении
        fact = etree.SubElement(elements, "{%s}fact" % pac)
        etree.SubElement(fact, "{%s}ID" % af).text = line['ID']
        etree.SubElement(fact, "{%s}OSZCode" % af).text = line['OSZCode']
        mszReceiver = etree.SubElement(fact, "{%s}MSZ_receiver" % af)
        etree.SubElement(mszReceiver, "{%s}SNILS" % prsn).text = line['SNILS']
        etree.SubElement(mszReceiver, "{%s}FamilyName" % smev).text = line['FamilyName']
        etree.SubElement(mszReceiver, "{%s}FirstName" % smev).text = line['FirstName']
        etree.SubElement(mszReceiver, "{%s}Patronymic" % smev).text = line['Patronymic']
        etree.SubElement(mszReceiver, "{%s}Gender" % prsn).text = line['Gender']
        etree.SubElement(mszReceiver, "{%s}BirthDate" % prsn).text = line['BirthDate']
        etree.SubElement(fact, "{%s}LMSZID" % af).text = line['LMSZID']
        etree.SubElement(fact, "{%s}categoryID" % af).text = line['categoryID_new']
        etree.SubElement(fact, "{%s}decision_date" % af).text = line['decisionDate']
        etree.SubElement(fact, "{%s}dateStart" % af).text = line['dateStart']
        etree.SubElement(fact, "{%s}dateFinish" % af).text = line['dateFinish']
        needsCriteria = etree.SubElement(fact, "{%s}needsCriteria" % af)
        etree.SubElement(needsCriteria, "{%s}usingSign" % af).text = line['usingSign']
        assignmentInfo = etree.SubElement(fact, "{%s}assignment_info" % af)
        serviceForm = etree.SubElement(assignmentInfo, "{%s}serviceForm" % af)
        etree.SubElement(serviceForm, "{%s}amount" % af).text = line['amount']
        etree.SubElement(serviceForm, "{%s}measuryCode" % af).text = line['measuryCode']
        etree.SubElement(fact, "{%s}lastChanging" % pac).text = line['lastChanging']

    tree = etree.ElementTree(root)
    xml_str = etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')

    with open(os.path.join(basedir, "path\\xml\\0988_10.06.S_{}.xml".format(packageId.text)), "w", encoding='utf-8') as f:
        f.write(xml_str.decode('UTF-8'))
        print("Создан файл: ", os.path.join(basedir, "path\\xml\\0988_10.06.S_{}.xml".format(packageId.text)))

# Добавление факта назначения по версии 10.06.S-1.0.4.XSD
def add_gen_new(factes):

    if not len(factes) == 0:
        ns0 = "urn://egisso-ru/types/package-RAF/1.0.3"
        ns1 = "urn://egisso-ru/types/assignment-fact/1.0.3"
        ns2 = "urn://egisso-ru/types/prsn-info/1.0.3"
        ns3 = "urn://x-artefacts-smev-gov-ru/supplementary/commons/1.0.1"
        ns4 = "urn://egisso-ru/types/basic/1.0.4"
        ns5 = "urn://egisso-ru/msg/10.06.S/1.0.2"

        NSMAP = {
                    'ns0': ns0,
                    'ns1': ns1,
                    'ns2': ns2,
                    'ns3': ns3,
                    'ns4': ns4,
                    'ns5': ns5,

                }

        root = etree.Element("{%s}data" % ns5, nsmap=NSMAP)
        #root.attrib['xmlns'] = "urn://egisso-ru/types/package-RAF/1.0.5"
        package = etree.SubElement(root, "{%s}package" % ns0)
        packageId = etree.SubElement(package, "{%s}packageID" % ns0)
        packageId.text = str(uuid.uuid4())
        elements = etree.SubElement(package, "{%s}elements" % ns0)


        for index, line in factes.iterrows():
            # Информация о назначении
            fact = etree.SubElement(elements, "{%s}fact" % ns0)
            etree.SubElement(fact, "{%s}ID" % ns1).text = line['ID']
            etree.SubElement(fact, "{%s}OSZCode" % ns1).text = line['OSZCode']
            mszReceiver = etree.SubElement(fact, "{%s}MSZ_receiver" % ns1)
            etree.SubElement(mszReceiver, "{%s}SNILS" % ns2).text = line['SNILS']
            etree.SubElement(mszReceiver, "{%s}FamilyName" % ns3).text = line['FamilyName']
            etree.SubElement(mszReceiver, "{%s}FirstName" % ns3).text = line['FirstName']
            if line['Patronymic']:
                etree.SubElement(mszReceiver, "{%s}Patronymic" % ns3).text = line['Patronymic']
            etree.SubElement(mszReceiver, "{%s}Gender" % ns2).text = line['Gender']
            etree.SubElement(mszReceiver, "{%s}BirthDate" % ns2).text = line['BirthDate']
            reason_persons = etree.SubElement(fact, "{%s}reason_persons" % ns1)
            prsnInfo = etree.SubElement(reason_persons, "{%s}prsnInfo" % ns2)
            try:
                etree.SubElement(prsnInfo, "{%s}SNILS" % ns2).text = line['rp_SNILS']
                etree.SubElement(prsnInfo, "{%s}FamilyName" % ns3).text = line['rp_FamilyName']
                etree.SubElement(prsnInfo, "{%s}FirstName" % ns3).text = line['rp_FirstName']
                if line['rp_Patronymic']:
                    etree.SubElement(prsnInfo, "{%s}Patronymic" % ns3).text = line['rp_Patronymic']
                etree.SubElement(prsnInfo, "{%s}Gender" % ns2).text = line['rp_Gender']
                etree.SubElement(prsnInfo, "{%s}BirthDate" % ns2).text = line['rp_BirthDate']
            except KeyError as e:
                etree.SubElement(prsnInfo, "{%s}SNILS" % ns2).text = line['SNILS']
                etree.SubElement(prsnInfo, "{%s}FamilyName" % ns3).text = line['FamilyName']
                etree.SubElement(prsnInfo, "{%s}FirstName" % ns3).text = line['FirstName']
                if line['Patronymic']:
                    etree.SubElement(prsnInfo, "{%s}Patronymic" % ns3).text = line['Patronymic']
                etree.SubElement(prsnInfo, "{%s}Gender" % ns2).text = line['Gender']
                etree.SubElement(prsnInfo, "{%s}BirthDate" % ns2).text = line['BirthDate']

            etree.SubElement(fact, "{%s}LMSZID" % ns1).text = line['LMSZID']
            etree.SubElement(fact, "{%s}categoryID" % ns1).text = line['categoryID']
            etree.SubElement(fact, "{%s}decision_date" % ns1).text = line['decisionDate']
            etree.SubElement(fact, "{%s}dateStart" % ns1).text = line['dateStart']
            etree.SubElement(fact, "{%s}dateFinish" % ns1).text = line['dateFinish']
            needsCriteria = etree.SubElement(fact, "{%s}needsCriteria" % ns1)
            etree.SubElement(needsCriteria, "{%s}usingSign" % ns1).text = line['usingSign']
            assignmentInfo = etree.SubElement(fact, "{%s}assignment_info" % ns1)
            serviceForm = etree.SubElement(assignmentInfo, "{%s}monetary_form" % ns1)
            etree.SubElement(serviceForm, "{%s}amount" % ns1).text = line['amount']
            etree.SubElement(fact, "{%s}lastChanging" % ns0).text = line['lastChanging']
            #if line['previosID']:
            #    etree.SubElement(fact, "{%s}previosID" % ns1).text = line['previosID']

        tree = etree.ElementTree(root)
        xml_str = etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')

        num = number()
        with open(os.path.join(basedir, "path\\xml\\0988_10.06.S_{}.xml".format(packageId.text)), "w", encoding='utf-8') as f:
            f.write(xml_str.decode('UTF-8'))
            print("Создан файл: ", os.path.join(basedir, "path\\xml\\0988_10.06.S_{}.xml".format(packageId.text)))
        number(int(num) + 1)


# 1.5	Изменение в связи с выявлением ошибки в ранее загруженном факте назначения
def alterationBasedOnPreviousErrors_gen(factes):
    print(len(factes))
    ns6 = "urn://egisso-ru/msg/10.06.S/1.0.4"
    ns2 = "urn://egisso-ru/types/assignment-fact/1.0.5"
    ns3 = "urn://egisso-ru/types/prsn-info/1.0.3"
    ns4 = "urn://x-artefacts-smev-gov-ru/supplementary/commons/1.0.1"
    ns5 = "urn://egisso-ru/types/basic/1.0.4"
    xsi = "http://www.w3.org/2001/XMLSchema-instance"

    smev = "urn://x-artefacts-smev-gov-ru/supplementary/commons/1.0.1"
    egisso = "urn://egisso-ru/types/basic/1.0.3"
    prsn = "urn://egisso-ru/types/prsn-info/1.0.2"
    af = "urn://egisso-ru/types/assignment-fact/1.0.2"
    pac = "urn://egisso-ru/types/package-RAF/1.0.2"
    dat = "urn://egisso-ru/msg/10.06.S/1.0.1"

    NSMAP = {
                'smev': smev,
                'egisso': egisso,
                'prsn': prsn,
                'af': af,
                'pac': pac,
                'dat': dat,
            }

    root = etree.Element("{%s}data" % dat, nsmap=NSMAP)
    root.attrib['xmlns'] = "urn://egisso-ru/types/package-RAF/1.0.5"
    package = etree.SubElement(root, "{%s}package" % pac)
    packageId = etree.SubElement(package, "{%s}packageId" % pac)
    packageId.text = str(uuid.uuid4())
    elements = etree.SubElement(package, "{%s}elements" % pac)

    for index, line in factes.iterrows():
        # Изменение информации о назначении
        alterationBasedOnPreviousErrors = etree.SubElement(elements, "alterationBasedOnPreviousErrors")
        uid_abope = str(uuid.uuid4())
        etree.SubElement(alterationBasedOnPreviousErrors, "uuid").text = uid_abope
        etree.SubElement(alterationBasedOnPreviousErrors, "assignmentFactUuid").text = line['ID']
        fact = etree.SubElement(alterationBasedOnPreviousErrors, "fact", nsmap={'xsi': xsi}, attrib={'{%s}type' % xsi: 'tFactAssignment'})
        etree.SubElement(fact, "{%s}oszCode" % ns2).text = line['OSZCode']
        mszReceiver = etree.SubElement(fact, "{%s}mszReceiver" % ns2)
        etree.SubElement(mszReceiver, "{%s}SNILS" % ns3).text = line['SNILS']
        etree.SubElement(mszReceiver, "{%s}FamilyName" % ns4).text = line['FamilyName']
        etree.SubElement(mszReceiver, "{%s}FirstName" % ns4).text = line['FirstName']
        etree.SubElement(mszReceiver, "{%s}Patronymic" % ns4).text = line['Patronymic']
        etree.SubElement(mszReceiver, "{%s}Gender" % ns3).text = line['Gender']
        etree.SubElement(mszReceiver, "{%s}BirthDate" % ns3).text = line['BirthDate']
        etree.SubElement(fact, "{%s}lmszId" % ns2).text = line['LMSZID']
        etree.SubElement(fact, "{%s}categoryId" % ns2).text = line['categoryID_new']
        etree.SubElement(fact, "{%s}decisionDate" % ns2).text = line['decisionDate']
        etree.SubElement(fact, "{%s}dateStart" % ns2).text = line['dateStart']
        needsCriteria = etree.SubElement(fact, "{%s}needsCriteria" % ns2)
        etree.SubElement(needsCriteria, "{%s}usingSign" % ns2).text = line['usingSign']
        assignmentInfo = etree.SubElement(fact, "{%s}assignmentInfo" % ns2)
        monetaryForm = etree.SubElement(assignmentInfo, "{%s}monetaryForm" % ns2)
        etree.SubElement(monetaryForm, "{%s}amount" % ns2).text = line['amount']
        etree.SubElement(monetaryForm, "{%s}measuryCode" % ns2).text = line['measuryCode']
        etree.SubElement(fact, "uuid").text = uid_abope

    tree = etree.ElementTree(root)
    xml_str = etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')

    with open(os.path.join(basedir, "path\\xml\\0988_10.06.S_{}.xml".format(packageId.text)), "w", encoding='utf-8') as f:
        f.write(xml_str.decode('UTF-8'))
        print("Создан файл: ", os.path.join(basedir, "path\\xml\\0988_10.06.S_{}.xml".format(packageId.text)))


# 1.1	Прекращение факта назначения в связи с перерасчетом назначения по версии 10.06.S-1.0.4.XSD
def terminationBasedOnRecalculation_gen(factes):
    print(len(factes))
    ns6 = "urn://egisso-ru/msg/10.06.S/1.0.4"
    ns2 = "urn://egisso-ru/types/assignment-fact/1.0.5"
    ns3 = "urn://egisso-ru/types/prsn-info/1.0.3"
    ns4 = "urn://x-artefacts-smev-gov-ru/supplementary/commons/1.0.1"
    ns5 = "urn://egisso-ru/types/basic/1.0.4"
    xsi = "http://www.w3.org/2001/XMLSchema-instance"

    NSMAP = {
        'ns6': ns6,
        'ns2': ns2,
        'ns3': ns3,
        'ns4': ns4,
        'ns5': ns5,
    }

    root = etree.Element("{%s}data" % ns6, nsmap=NSMAP)
    root.attrib['xmlns'] = "urn://egisso-ru/types/package-RAF/1.0.5"
    package = etree.SubElement(root, "package")
    packageId = etree.SubElement(package, "packageId")
    packageId.text = str(uuid.uuid4())
    elements = etree.SubElement(package, "elements")

    for index, line in factes.iterrows():
        #if line['amount'] == '6284,65':
        # Удаление информации о назначении
        terminationBasedOnRecalculation = etree.SubElement(elements, "terminationBasedOnRecalculation")
        etree.SubElement(terminationBasedOnRecalculation, "uuid").text = str(uuid.uuid4())
        etree.SubElement(terminationBasedOnRecalculation, "assignmentFactUuid").text = line['previosID']
        etree.SubElement(terminationBasedOnRecalculation, "dateFinish").text = line['dateFinish']

    tree = etree.ElementTree(root)
    xml_str = etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    with open(os.path.join(basedir, "path\\xml\\0988_10.06.S_{}.xml".format(packageId.text)), "w", encoding='utf-8') as f:
        f.write(xml_str.decode('UTF-8'))
        print("Создан файл: ", os.path.join(basedir, "path\\xml\\0988_10.06.S_{}.xml".format(packageId.text)))

# 1.7	Удаление ошибочно загруженных записей
def errorsInvalidation_gen(factes):
    print(len(factes))
    ns6 = "urn://egisso-ru/msg/10.06.S/1.0.4"
    ns2 = "urn://egisso-ru/types/assignment-fact/1.0.5"
    ns3 = "urn://egisso-ru/types/prsn-info/1.0.3"
    ns4 = "urn://x-artefacts-smev-gov-ru/supplementary/commons/1.0.1"
    ns5 = "urn://egisso-ru/types/basic/1.0.4"
    xsi = "http://www.w3.org/2001/XMLSchema-instance"

    NSMAP = {
        'ns6': ns6,
        'ns2': ns2,
        'ns3': ns3,
        'ns4': ns4,
        'ns5': ns5,
    }

    root = etree.Element("{%s}data" % ns6, nsmap=NSMAP)
    root.attrib['xmlns'] = "urn://egisso-ru/types/package-RAF/1.0.5"
    package = etree.SubElement(root, "package")
    packageId = etree.SubElement(package, "packageId")
    packageId.text = str(uuid.uuid4())
    elements = etree.SubElement(package, "elements")

    for index, line in factes.iterrows():

        # Удаление информации о назначении
        errorsInvalidation = etree.SubElement(elements, "errorsInvalidation")
        etree.SubElement(errorsInvalidation, "uuid").text = str(uuid.uuid4())
        etree.SubElement(errorsInvalidation, "assignmentFactUuid").text = line['ID']

    tree = etree.ElementTree(root)
    xml_str = etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')

    with open(os.path.join(basedir, "path\\xml\\0988_10.06.S_{}.xml".format(packageId.text)), "w", encoding='utf-8') as f:
        f.write(xml_str.decode('UTF-8'))
        print("Создан файл: ", os.path.join(basedir, "path\\xml\\0988_10.06.S_{}.xml".format(packageId.text)))