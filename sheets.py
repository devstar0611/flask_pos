from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'client_secret.json'


credentials = None
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)



# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '18G0yuz-vwjF_VOFWDhOc8gjozGobuPo8ZwQpYcxMIHY'

def update_details(upc, title, price, stock, disc, employee, link, imglink, description):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """


    service = build('sheets', 'v4', credentials=credentials)

    # Call the Sheets API
    sheet = service.spreadsheets()

    
    if disc=="":
        discvalue= 0 
    else:
        try:
            price1 = float(price.replace("$", ""))
        except:
            price1 = float(price)


        disc1=float(disc)
        discP = price1 - ((price1*disc1)/100)
        discvalue= str('%.2f' % discP) + ' USD'
     
    if stock=="":
        stockvalue= 1
    else:
        stockvalue= stock
           
    valuerange_Sheet1 = [
                    [
                        upc, 
                        title, 
                        description, 
                        'in stock', 
                        'New', 
                        discvalue, 
                        link,
                        imglink,
                        'Mesa Liquidation',
                        stockvalue
                    ]
                ]
    bodySheet1 = {'values': valuerange_Sheet1}
    
    # Writing
    result = sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, 
                                    range='Sheet1!A:J',
                                    valueInputOption='USER_ENTERED', 
                                    body=bodySheet1).execute()
    
    # values = result.get('values', [])
    
    # print(result)
    
    valuerange_Sheet2 = [
                    [
                        upc, 
                        title, 
                        price, 
                        stock, 
                        disc, 
                        discvalue, 
                        str(datetime.now().strftime("%Y-%m-%d_%H:%M:%S")),
                        employee
                    ]
                ]
    bodySheet2 = {'values': valuerange_Sheet2}
    
    # Writing
    result = sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, 
                                    range='Sheet2!A:H',
                                    valueInputOption='USER_ENTERED', 
                                    body=bodySheet2).execute()
    
    
    # Reading
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range='Sheet2!A:H').execute()
    
    
    values = result.get('values', [])
    
    return {"count":len(values)}
    
# update_details('upc', 'title', '10', '11', '50', 'employee', 'https://www.facebook.com/marketplace/item/199949842174780/', 'https://www.facebook.com/marketplace/item/199949842174780/', 'description')

    
