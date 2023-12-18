from openpyxl.utils import rows_from_range
from openpyxl import load_workbook
from openpyxl.worksheet.cell_range import CellRange
from copy import copy


def copy_range(range_str, sheet, offset):
    """ Copy cell values and style to the new row using offset"""
    for row in rows_from_range(range_str):
        for cell in row:
            if sheet[cell].value is not None:  # Don't copy other cells in merged unit
                dst_cell = sheet[cell].offset(row=offset, column=0)
                src_cell = sheet[cell]

                # Copy Cell value
                dst_cell.value = src_cell.value

                # Copy Cell Styles
                dst_cell.font = copy(src_cell.font)
                dst_cell.alignment = copy(src_cell.alignment)
                dst_cell.border = copy(src_cell.border)
                dst_cell.fill = copy(src_cell.fill)

                dst_cell.number_format = src_cell.number_format


def get_league_match():
    return {
            'teams': '',
            'HF' : '',
            'AF' : '',
            '3H': '',
            '3W':'',
            'H':'',
            'A':'',
            'HH': '',
            'HA':'',
            'H2H':'',
            'H2A':'',
            'FM':'',
            'GD':'',
            'LH':'',
            'LA':'',
            'Hand': '',
            'H%': '',
            'A%':'',
            '5H': '',
            '5A':'',
            'L3H':'',
            'L3A':'',
            'Stat':'',
            'For':'',
            'Res':'',
            'BF':'',
            'Bet':'',
            'RES':'',
            'SH':'',
            'SA':'',
            'O-O':'',
            'L-O':'',
            'Diff':'',
            'Hand2':'',
            'HT Odds':'',
            'TGO':'',
            'LO2':'',
            'Diff2':'',
            'TG':'',
            'TG-HT': '',
            'TG-2H': ''      
        }