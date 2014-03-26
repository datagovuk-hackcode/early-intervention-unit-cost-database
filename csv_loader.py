# coding: utf-8
from database import *
import ucsv
import os
import re

r = re.compile(r'[^\d\.]')

confidence_map = {
    'R' : 'Low',
    'A' : 'Medium',
    'G' : 'High'
}

outcome_category = OutcomeCategory("")
outcome_detail = OutcomeDetail("")
level_1_agency = Agency(1, "")
level_2_agency = Agency(2, "")
unit = Unit("")

entry_list = []

count = 0

for filename in os.listdir('csvs'):
    with open('csvs/' + filename, 'r+') as csvfile:
        csvreader = ucsv.UnicodeReader(csvfile, delimiter=',', quotechar='"')
        for row in csvreader:
            if (
                outcome_category is None or
                outcome_category.name != row[0]
            ):
                outcome_category = OutcomeCategory.get_by_name(row[0])

            if (
                outcome_detail is None or
                outcome_detail.name != row[1]
            ):
                outcome_detail = OutcomeDetail.get_by_name(row[1])

            if (
                level_1_agency is None or
                level_1_agency.name != row[4]
            ):
                level_1_agency = Agency.get_by_name(row[4])

            if (
                level_2_agency is None or
                level_2_agency.name != row[5]
            ):
                level_2_agency = Agency.get_by_name(row[5])

            if (
                level_2_agency is None and
                row[5] != ""
            ):
                raise Exception('Level 2 Agency ' + row[5] + ' does not exist')

            if (
                unit is None or
                unit.name != row[6]
            ):
                unit = Unit.get_by_name(row[6])

            if (
                outcome_detail is not None and
                outcome_detail not in outcome_category.details
            ):
                outcome_category.details.append(outcome_detail)
                db.session.commit()

            if (
                level_2_agency is not None and
                level_2_agency not in level_1_agency.children
            ):
                level_1_agency.children.append(level_2_agency)
                db.session.commit()

            parent = None

            while len(entry_list) != 0:
                if (
                    row[2].startswith(entry_list[-1].code) and
                    row[2] != entry_list[-1].code
                ):
                    parent = entry_list[-1]
                    break
                else:
                    entry_list.pop()

            entry = Entry(
                outcome_category,
                outcome_detail,
                row[2],
                row[3],
                level_1_agency,
                level_2_agency,
                unit,
                cdecimal.Decimal(re.sub(r,'',row[7])),
                int(row[8][0:4]),
                row[10],
                row[13],
                confidence_map[row[11]],
                row[12],
                parent
            )

            db.session.add(entry)

            entry_list.append(entry)

            count += 1

            if count >= 25:
                db.session.commit()
                count = 0

db.session.commit()
