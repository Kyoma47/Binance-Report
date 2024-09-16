import gspread
from google.oauth2.service_account import Credentials

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

credentials = Credentials.from_service_account_file("gcp-credentials.json", scopes=scopes)
client = gspread.authorize(credentials=credentials)

# https://docs.google.com/spreadsheets/d/13qBnldQcoPsPLIinNIlhnkHj45wYzCu-J_J5iPsWBBs/edit?gid=520047181#gid=520047181
sheet_id = "13qBnldQcoPsPLIinNIlhnkHj45wYzCu-J_J5iPsWBBs"
workbook = client.open_by_key(sheet_id)

values = [
    ["Name", "Price", "Quality"],
    ["Basketball", 29.99, 1],
    ["Jeans", 39.99, 4],
    ["Soap", 7.99, 3],
]

sheets_names = map( lambda x: x.title, workbook.worksheets() )
new_worksheet_name = "Values"

if new_worksheet_name in sheets_names : 
    sheet = workbook.worksheet( new_worksheet_name )
else : 
    sheet = workbook.add_worksheet(new_worksheet_name, rows=10, cols=10)

sheet.clear()

# update cells (one by one):
'''
for i,row in enumerate(values):
    for j,value in enumerate(row):
        sheet.update_cell(i+1, j+1, value)
'''

# Update range of cells : 
sheet.update(values, "A1:C{}".format(len(values)) )

sheet.update_cell(len(values)+1, 2, "=sum(B2:B4)" )
sheet.update_cell(len(values)+1, 3, "=sum(C2:C4)" )

# Formating Headers : 
sheet.format("A1:C1", {"textFormat": {"bold":True} })
