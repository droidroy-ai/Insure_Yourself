import openpyxl
import requests
import os

file_name = 'Products.xlsx'
save_path = './saved_pdf'

def download_pdf_in_sheet(sheet):
  for row in sheet.rows:
    for cell in row:
      try:
        if len(cell.hyperlink.target)  > 0:
          pdf_name = str(cell.hyperlink.target).split('/')[-1]
          response = requests.get(cell.hyperlink.target)
          with open(os.path.join(save_path, pdf_name), 'wb') as f:
            f.write(response.content)
            print('Saved', pdf_name)
      except:
        pass


workbook = openpyxl.load_workbook(file_name)
sheet_names = workbook.sheetnames

for name in sheet_names:
  sheet = workbook[name]
  if os.path.exists(save_path):
    download_pdf_in_sheet(sheet) 
  else:
    os.mkdir(save_path)
    download_pdf_in_sheet(sheet)

