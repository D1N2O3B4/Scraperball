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
    
    df.sort_values(by='League', inplace=True)
    # print(df)
    
    leagues = {
        
    }
    
    rows = df.iterrows()
    
    for row in rows:
        row = row[1]
        home = row['Home']
        away = row['Away']
        
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
            'Hand2':'',
            'HT Odds':'',
            'TGO':'',
            'LO2':'',
            'Diff2':'',
            'TG':'',
            'TG-HT': '',
            'TG-2H': ''      
        }
        
        for key in row.keys():
            if key == 'League': continue
            if key == 'Home' or key == 'Away':
                league_match['teams'] = f'{row["Home"]} vs {row["Away"]}'
                continue
            # if key == "Hand2" or key == "Diff2" or key == "TG-HT" or key == "TG-2H": continue
            league_match[key] = row[key]
        if row['League'] not in leagues:
            leagues[f'{row["League"]}'] = []
    
        leagues[f'{row["League"]}'].append(league_match)
    
    wb = xl.load_workbook(resource_path('Myfile-decrypted.xlsx'))
    ws = wb.active
    
    headers = ws['A2' : 'BI2'][0]
    headers = [x.value for x in headers]
    current = 2
    start = None
    for key in leagues.keys():

        # if key == "Hand2" or key == "Diff2" or key == "TG-HT" or key == "TG-2H": continue
        
        if start is not None:
            ws.row_dimensions.group(start, current - 1, hidden=False)

        copy_range('A2:BI2', ws, current - 2)
        for i, header in enumerate(headers):
            if i == 0:
                if key == "Diff2" or key == "Hand2":
                    key = key.replace('2', '')
                ws.cell(row=current, column=i+1).value = key
                continue
            # ws.cell(row=current, column=(i+1)).value = header
        current += 1
        start = current
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

                if prop == "Res":
                    if match[prop] == 'SHW' or match[prop] == "MHW":
                        cell.fill = PatternFill("solid", fgColor="56B0F0")
                    elif match[prop] == 'SAW' or match[prop] == "MAW":
                        cell.fill = PatternFill("solid", fgColor="FF0000")
                    else:
                        cell.fill = PatternFill("solid", fgColor="A6A6A6")
                    continue

                if prop == "H" or prop == "A":
                    if val == 'W':
                        cell.fill = PatternFill("solid", fgColor="56B0F0")
                    elif val == 'L':
                        cell.fill = PatternFill("solid", fgColor="FF0000")
                
                if prop == "H2H":
                    if val >= 1:
                        cell.fill = PatternFill("solid", fgColor="0D1E5E")
                    elif val >= 0.33:
                        cell.fill = PatternFill("solid", fgColor="808170")
                    else:
                        cell.fill = PatternFill("solid", fgColor="FF0000")
                        
                if prop == "5H" or prop == "5A" or prop == "L3H" or prop == "L3A":
                    cell.value = val[0]
                    last_goals = val[1]
                    # print(last_goals)
                    if last_goals >= 7:
                        cell.fill = PatternFill("solid", fgColor="663300")
                    elif last_goals == 6:
                        cell.fill = PatternFill("solid", fgColor="000099")
                    elif last_goals == 5:
                        cell.fill = PatternFill("solid", fgColor="000000")
                    elif last_goals == 4:
                        cell.fill = PatternFill("solid", fgColor="FF00FF")
                    elif last_goals == 3:
                        cell.fill = PatternFill("solid", fgColor="FF8000")
                    elif last_goals == 2:
                        cell.fill = PatternFill("solid", fgColor="56B0F0")
                    elif last_goals == 1:
                        cell.fill = PatternFill("solid", fgColor="059C00")
                    elif last_goals == 0:
                        cell.fill = PatternFill("solid", fgColor="FF0000")  
                    continue              
                
                if prop == 'Stat':
                    cell.fill = PatternFill("solid", fgColor="C6EFCE")
                    continue
                
                if prop == "For":
                    cell.fill = PatternFill("solid", fgColor="56B0F0")
                    continue

                
                if prop == "BF":
                    bf = val
                    bf_val = (bf[0]/bf[1]) * 100
                    if bf_val >= 80:
                        cell.fill = PatternFill("solid", fgColor="56B0F0")
                    elif bf_val >= 40:
                        cell.fill = PatternFill("solid", fgColor="424A41")
                    else:
                        cell.fill = PatternFill("solid", fgColor="356DB9")
                    
                    # for_cell = ws.cell(row=current, column=col - 2)
                    # fr = for_cell.value
                    # print(fr)
                    # if int(fr) >= 50:
                    #     bf[0] += 1
                    cell.value = bf_val
                    continue
                
                if prop == "Hand":
                    if float(val) == 0.0 or float(val) == -0.0:
                        cell.value = 'L'
                        continue
                    # if float(val) < 0:
                        # cell.fill = PatternFill("solid", fgColor="FF0000")
                    elif float(val) > 0:
                        cell.fill = PatternFill("solid", fgColor="55AFE9")
                    
                if prop == "O-O" or prop == "L-O" or prop == "TGO" or prop == "LO2":
                    if float(val) < 1.95:
                        cell.fill = PatternFill("solid", fgColor="55AFE9")
                    else:
                        cell.fill = PatternFill("solid", fgColor="FF0000")
                
                if prop == "Diff" or prop == "Diff2":
                    if int(val) < 0:
                        cell.fill = PatternFill("solid", fgColor="FF0000")
                    else:
                        cell.fill = PatternFill("solid", fgColor="56B0F0")

                cell.value = match[prop]

            current += 1
    if start is not None:
        ws.row_dimensions.group(start, current - 1, hidden=False)
    
    cell = ws.cell(row=current, column=1)
    cell.value = cell.value
    
    
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