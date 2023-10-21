import pandas as pd
from pandas import DataFrame
# import msoffcrypto
import openpyxl as xl
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Fill, fills, PatternFill, GradientFill, Font
from openpyxl.styles import Alignment
from openpyxl import formatting

import datetime
import os


from generator_utils import copy_range
from utils import resource_path

def generate(df : DataFrame):
    # df = pd.read_csv('./output.csv')
    try:
        df = df.drop(columns=['Unnamed: 0'], axis=1, ) 
    except Exception as e:
        # print(e)
        pass
    
    df.sort_values(by='league', inplace=True)
    # print(df)
    
    leagues = {
        
    }
    
    rows = df.iterrows()
    
    for row in rows:
        row = row[1]
        home = row['home']
        away = row['away']
        
        league_match = {
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
            'Hand':'',
            'HT Odds':'',
            'TGO':'',
            'LO2':'',
            'Diff':'',
            'TG':'',        
        }
        
        for key in row.keys():
            if key == 'league': continue
            if key == 'home' or key == 'away':
                league_match['teams'] = f'{row["home"]} vs {row["away"]}'
                continue
            
            league_match[key] = row[key]
            
        if row['league'] not in leagues:
            leagues[f'{row["league"]}'] = []
    
        leagues[f'{row["league"]}'].append(league_match)
    
    wb = xl.load_workbook(resource_path('Myfile-decrypted.xlsx'))
    ws = wb.active
    
    headers = ws['A2' : 'AM2'][0]
    headers = [x.value for x in headers]
    current = 2
    
    for key in leagues.keys():
        copy_range('A2:BI2', ws, current - 2)
        for i, header in enumerate(headers):
            if i == 0:
                ws.cell(row=current, column=i+1).value = key
                continue
            # ws.cell(row=current, column=(i+1)).value = header
        current += 1
        
        for match in leagues[key]:
            # ws.cell(row=current, culumn=)
            for prop in match.keys():
                if prop == 'teams':
                    ws.cell(row=current, column=1).value = match['teams']
                    continue
                
                col = headers.index(prop) + 1
                
                cell = ws.cell(row=current, column=col)

                val = match[prop]
                cell.alignment = Alignment(horizontal='center', vertical="center")
                
                if prop == "5H" or prop == "5A" or prop == "L3H" or prop == "L3A":
                    if val >= 7:
                        cell.fill = PatternFill("solid", fgColor="663300")
                    elif val >= 6:
                        cell.fill = PatternFill("solid", fgColor="000099")
                    elif val >= 5:
                        cell.fill = PatternFill("solid", fgColor="000000")
                    elif val >= 4:
                        cell.fill = PatternFill("solid", fgColor="FF00FF")
                    elif val >= 3:
                        cell.fill = PatternFill("solid", fgColor="FF8000")
                    elif val >= 2:
                        cell.fill = PatternFill("solid", fgColor="56B0F0")
                    elif val >= 1:
                        cell.fill = PatternFill("solid", fgColor="059C00")
                    elif val >= 0:
                        cell.fill = PatternFill("solid", fgColor="FF0000")                
                
                if prop == 'Stat':
                    cell.fill = PatternFill("solid", fgColor="C6EFCE")
                    continue
                
                if prop == "For":
                    cell.fill = PatternFill("solid", fgColor="56B0F0")
                    continue

                if prop == "Res":
                    continue
                
                cell.value = match[prop]

            current += 1
    
    
    try:
        os.mkdir('./output')
        pass
    except OSError as e:
        # print(e)
        pass
    
    now = datetime.datetime.now()
    name = str(now).split('.')[0].replace(':', '')
    # print(name)
    wb.save(f'./output/{name}.xlsx')