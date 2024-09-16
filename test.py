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

# Select worksheets objects : 
sheets = workbook.worksheets()
print( sheets )
print()

# Select name of work sheets : 
sheets = map( lambda x: x.title, workbook.worksheets() )
L = list( sheets )
print(L)
print()

# Select work sheet by name : 
test_sheet = workbook.worksheet("Test")

# change name of a worksheet : 
# test_sheet.update_title("Hello world !")

# Update cell : 
test_sheet.update_acell("A1", "this is first cell")
test_sheet.update_cell(1, 2, 'xxxxxx')
test_sheet.update_cell(2, 1, 'yyyyyy')

# Find cell by content :
cell = test_sheet.find("BTC")
print(cell)
print(cell.row, cell.col, cell.address)

# Basic formatting : 
test_sheet.format("A1", {"textFormat": {"bold":True} })


