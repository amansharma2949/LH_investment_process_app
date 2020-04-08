import pandas as pd
from dateutil.relativedelta import relativedelta
import textwrap3
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from statistics import mean

# Set up Google API to access google doc
def get_ticker_data(ticker):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open('Investment Process App').sheet1

    data = sheet.get_all_values()
    headers = data.pop(0)
    df_final = pd.DataFrame(data, columns=headers)
    df_final['Date']= pd.to_datetime(df_final['Date'])

    # Access company of interest
    ticker = ticker
    ticker_data = df_final[df_final['Ticker'] == ticker]

    return ticker_data

# get ticker data table
def get_data_table():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open('Investment Process App').sheet1

    data = sheet.get_all_values()
    headers = data.pop(0)
    df_final = pd.DataFrame(data, columns=headers)
    df_final['Date']= pd.to_datetime(df_final['Date'])

    ticker_data = df_final

    return ticker_data

# Add line breaks to comments
def add_new_line(comment):
    split_text = textwrap3.wrap(comment, width=25)
    final = '<br> '.join(split_text)
    return final

# Get most recent trading day (takes timestamp and return datetime)
def last_trading_day(date):
    closing_day_latest = date

    if (date.weekday() == 5):
        closing_day_latest = date - relativedelta(days=1)

    if (date.weekday() == 6):
        closing_day_latest = date - relativedelta(days=2)

    return closing_day_latest

############################################################################################
# Create table with process metrics

# Take final_df and return time between each research step
def get_lags_ticker(data_input, ticker):
    data = data_input[data_input['Ticker'] == ticker]

    try:
        begin = data[data['Event'] == 'Begin Research']['Date'].values[0]
    except IndexError:
        begin = 0

    try:
        begin = data[data['Event'] == 'Begin Research']['Date'].values[0]
        two_three = data[data['Event'] == 'Pass Level 2/3']['Date'].values[0]
        lag1 = (two_three - begin).astype('timedelta64[D]').astype(int)
    except IndexError:
        lag1 = 0

    try:
        two_three = data[data['Event'] == 'Pass Level 2/3']['Date'].values[0]
        four_five = data[data['Event'] == 'Pass Level 4/5']['Date'].values[0]
        lag2 = (four_five - two_three).astype('timedelta64[D]').astype(int)
    except IndexError:
        lag2 = 0

    try:
        four_five = data[data['Event'] == 'Pass Level 4/5']['Date'].values[0]
        six_seven = data[data['Event'] == 'Pass Level 6/7']['Date'].values[0]
        lag3 = (six_seven - four_five).astype('timedelta64[D]').astype(int)
    except IndexError:
        lag3 = 0

    return lag1, lag2, lag3, begin


# take final_df and return average time between each research step
def get_lags_average(data):
    two_three_lags = []
    four_five_lags = []
    six_seven_lags = []

    for company in data['Ticker'].unique():
        lags = get_lags_ticker(data, company)
        two_three_lags.append(lags[0])
        four_five_lags.append(lags[1])
        six_seven_lags.append(lags[2])

    two_three_filtered = list(filter(lambda num: num != 0, two_three_lags))
    four_five_filtered = list(filter(lambda num: num != 0, four_five_lags))
    six_seven_filtered = list(filter(lambda num: num != 0, six_seven_lags))

    if (len(two_three_filtered) != 0):
        two_three_avg = mean(two_three_filtered)

    if (len(four_five_filtered) != 0):
        four_five_avg = mean(four_five_filtered)

    if (len(six_seven_filtered) != 0):
        six_seven_avg = mean(six_seven_filtered)

    return two_three_avg, four_five_avg, six_seven_avg


# take ticker_data and fill out final_table
def create_table(data_full, ticker):
    process_data = [['Pass Level 2/3', 0, 0], ['Pass Level 4/5', 0, 0], ['Pass Level 6/7', 0, 0]]
    process_data = pd.DataFrame(process_data, columns=['Research Phase', 'Average', ticker])

    print(get_lags_average(data_full)[0])
    process_data.loc[0, ("Average")] = get_lags_average(data_full)[0]
    process_data.loc[1, ("Average")] = get_lags_average(data_full)[1]
    process_data.loc[2, ("Average")] = get_lags_average(data_full)[2]

    process_data.loc[0, (ticker)] = get_lags_ticker(data_full, ticker)[0]
    process_data.loc[1, (ticker)] = get_lags_ticker(data_full, ticker)[1]
    process_data.loc[2, (ticker)] = get_lags_ticker(data_full, ticker)[2]

    return process_data


############################################################################################