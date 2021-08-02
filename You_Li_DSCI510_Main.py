import argparse
import csv
import datetime
import sqlite3
from collections import OrderedDict
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import prettytable as pt
import pycountry
import pygal
import requests
from bs4 import BeautifulSoup
from pygal.style import LightColorizedStyle as LCS, RotateStyle as RS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

parser = argparse.ArgumentParser()
parser.add_argument('--static')
args = parser.parse_args()


# For Coronavirus Dataset:
# store a specific country's all confirmed cases each day in a list that starts with the country name
def get_confirmed_cases(country_code, country_name, case_url):
    confirmed_cases = [country_code, country_name, 'Confirmed Cases']
    day_one = requests.get(case_url).json()
    if not day_one:  # Some countries do not report their data so it will be an empty list so return a none object
        return None
    else:
        for day in day_one:
            confirmed_cases.append(day['Confirmed'])
        return confirmed_cases


# Store a specific country's all deaths cases each day in a list that starts with the country name
def get_deaths_cases(country_code, country_name, case_url):
    deaths_cases = [country_code, country_name, 'Deaths']
    day_one = requests.get(case_url).json()
    if not day_one:
        return None
    else:
        for day in day_one:
            deaths_cases.append(day['Deaths'])
        return deaths_cases


# Store a specific country's new cases each day in a list that starts with the country name
def get_new_cases(country_code, country_name, case_url):
    new_cases = [country_code, country_name, 'New Cases']
    day_one = requests.get(case_url).json()
    ind = 0
    if not day_one:
        return None
    else:
        while ind < len(day_one):
            # noinspection PyBroadException
            try:
                new_case = day_one[ind + 1]['Confirmed'] - day_one[ind]['Confirmed']
                new_cases.append(new_case)
                ind += 1
            except:
                # This exception catches the index error of the last date
                break
        return new_cases


# For Vaccine information Dataset:
# Scrape the table on OUR WORLD IN DATA Website it uses lazy loading for its web design so import selenium library
def dynamic_table_scraper(url):
    # Hide the browser backstage
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(options=chrome_options)

    browser.get(url)
    wait = WebDriverWait(browser, 10).until(
        lambda driver: driver.find_element_by_xpath('/html/body/main/figure/div/div[1]/div/table'))
    # wait for loading in browser
    soup = BeautifulSoup(browser.page_source, "html.parser")
    browser.close()
    return soup


# Linear regression info formula
def get_lr_stats(x, y, model):
    message0 = 'The linear regression formula is ' + ' y' + '=' + str(model.intercept_) + ' + ' + str(
        model.coef_[0]) + 'x'
    y_prd = model.predict(x)
    regression = sum((y_prd - np.mean(y)) ** 2)  # ESS
    residual = sum((y - y_prd) ** 2)  # RSS
    total = sum((y - np.mean(y)) ** 2)  # TSS
    r_square = 1 - residual / total  # R^2
    message1 = ('R^2： ' + str(r_square) + '；' + '\n' + 'TSS： ' + str(total) + '；' + '\n')
    message2 = ('RSS： ' + str(regression) + '；' + '\nESS： ' + str(residual) + '；' + '\n')
    message3 = 'The statistical exam data for regression formula is:\n'
    return print(message0 + '\n' + message3 + message1 + message2)


if args.static:
    conn = sqlite3.connect(args.static)
    cur = conn.cursor()

else:

    # For Coronavirus dataset:
    # Create table headers (Date) use a country as an individual example
    coronavirus_table_headers = ['ISO Code', 'Country', 'Status']

    chinaurl = "https://api.covid19api.com/total/country/china?from=2021-01-01T00:00:00Z&to=2021-04-30T00:00:00Z"
    china = requests.get(chinaurl).json()

    for day in china:
        coronavirus_table_headers.append(day['Date'][0:10])  # Get the table header lists of dates

    # Get the country list that contains "Slug" and corresponding country name
    url = "https://api.covid19api.com/countries"
    countries = requests.get(url).json()

    # Create a csv file that store all the coronavirus cases of all countries each day
    print('Now starting scraping the Coronavirus information for each available country')
    with open('coronavirus_info.csv', 'w', encoding='utf-8', newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(coronavirus_table_headers)  # Write the table headers
        for country in countries:
            # noinspection PyBroadException
            try:
                day_one_url = "https://api.covid19api.com/total/country/" + country[
                    "Slug"] + "?from=2021-01-01T00:00:00Z&to=2021-04-30T00:00:00Z"  # Get all country API url
                new_case_url = "https://api.covid19api.com/total/country/" + country[
                    "Slug"] + "?from=2020-12-31T00:00:00Z&to=2021-04-30T00:00:00Z"
                f_csv.writerow(get_confirmed_cases(country['ISO2'], country['Country'], day_one_url))
                f_csv.writerow(get_deaths_cases(country['ISO2'], country['Country'], day_one_url))
                f_csv.writerow(get_new_cases(country['ISO2'], country['Country'], new_case_url))
                print("The Coronavirus information of %s has already been scraped" % country['Country'])
            except:
                # If the country do not report data and this exception catches that NoneType error and skip to next country
                print('Sorry! %s Coronavirus information is not available!' % country['Country'])
                continue

    # For Vaccine Dataset:
    # Scrape the total doses for each country and store in a dictionary
    vaccine = defaultdict(list)
    print('Now starting scraping the total doses of vaccination information')
    total_dose = dynamic_table_scraper('https://ourworldindata.org/grapher/cumulative-covid-vaccinations?tab=table')
    tables = total_dose.findAll('table', {'class': 'data-table'})[0]
    for row in tables.findAll('tr')[2:]:
        try:
            if 'million' in row.find('td', {'class': 'dimension dimension-end'}).text.split():
                vaccine[row.find('td').text].append(
                    eval(row.find('td', {'class': 'dimension dimension-end'}).text.split()[-2]) * 1000000)
            elif len(row.find('td', {'class': 'dimension dimension-end'}).text.split()) == 1:
                vaccine[row.find('td').text].append(
                    int(row.find('td', {'class': 'dimension dimension-end'}).text.replace(",", "")))
            else:
                vaccine[row.find('td').text].append(
                    int(row.find('td', {'class': 'dimension dimension-end'}).text.split()[-1].replace(',', '')))
        except:
            continue

    # Scrape the cumulative per hundred vaccine data and store in above dictionary
    print('Now starting scraping the cumulative per hundred vaccination information')
    cumulative_per_hundred = dynamic_table_scraper(
        'https://ourworldindata.org/grapher/covid-vaccination-doses-per-capita?tab=table')
    tables = cumulative_per_hundred.findAll('table', {'class': 'data-table'})[0]
    for row in tables.findAll('tr')[2:]:
        try:
            if len(row.find('td', {'class': 'dimension dimension-end'}).text.split()) > 1:
                vaccine[row.find('td').text].append(
                    row.find('td', {'class': 'dimension dimension-end'}).text.split()[-1])
            else:
                vaccine[row.find('td').text].append(row.find('td', {'class': 'dimension dimension-end'}).text)
        except:
            continue

    # Scrape the daily new vaccine per hundred
    print('Now starting scraping the new vaccination per hundred information')
    daily_per_hundred = dynamic_table_scraper(
        'https://ourworldindata.org/grapher/daily-covid-vaccination-doses-per-capita?tab=table')
    tables = daily_per_hundred.findAll('table', {'class': 'data-table'})[0]
    for row in tables.findAll('tr')[2:]:
        try:
            if len(row.find('td', {'class': 'dimension dimension-end'}).text.split()) > 1:
                vaccine[row.find('td').text].append(
                    row.find('td', {'class': 'dimension dimension-end'}).text.split()[-1])
            else:
                vaccine[row.find('td').text].append(row.find('td', {'class': 'dimension dimension-end'}).text)
        except:
            continue

    # Scrape the share of population vaccine data
    print('Now starting scraping the share of population vaccination information')
    share = dynamic_table_scraper('https://ourworldindata.org/grapher/share-people-vaccinated-covid?tab=table')
    tables = share.findAll('table', {'class': 'data-table'})[0]
    for row in tables.findAll('tr')[2:]:
        try:
            if len(row.find('td', {'class': 'dimension dimension-end'}).text.split()) > 1:
                vaccine[row.find('td').text].append(
                    row.find('td', {'class': 'dimension dimension-end'}).text.split()[-1])
            else:
                vaccine[row.find('td').text].append(row.find('td', {'class': 'dimension dimension-end'}).text)
        except:
            continue

    dictionary = vaccine
    table_headers = ['Country name', 'Total Doses', 'Accumulated vaccine per 100 people',
                     'Daily vaccine per 100 people',
                     'Share of population got one vaccine']

    # write the data into a CSV file

    with open('vaccine_info.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(table_headers)
        for key, val in dictionary.items():
            val.insert(0, key)
            writer.writerow(val)

    # For GDP dataset:
    gdp_url = 'https://api.worldbank.org/v2/en/country/all/indicator/NY.GDP.PCAP.CD?per_page=300&source=2&date=2019'
    gdp_r = requests.get(gdp_url)
    soup = BeautifulSoup(gdp_r.content, 'html.parser')
    gdp_table_headers = ['Country Code', 'Country Name', 'GDP']

    with open('gdp_per_capita.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(gdp_table_headers)
        gdp_countries = soup.findAll('wb:data')
        for gdp_country in gdp_countries[1:]:
            if gdp_country.find('wb:value').text:
                gdp_country_list = [gdp_country.find('wb:country').get('id'), gdp_country.find('wb:country').text,
                                    gdp_country.find('wb:value').text]
                writer.writerow(gdp_country_list)

    print('Now converting the csv files into sqlite database,please wait!')

    # Convert three csv datasets into sqlite database
    conn = sqlite3.connect("final_project.db")
    cur = conn.cursor()
    df_coronavirus = pd.read_csv('coronavirus_info.csv')
    df_coronavirus.to_sql('coronavirus_info', conn, if_exists='replace', index=False)
    df_vaccine = pd.read_csv('vaccine_info.csv')
    df_vaccine.to_sql('vaccine_info', conn, if_exists='replace', index=False)
    df_gdp = pd.read_csv('gdp_per_capita.csv')
    df_gdp.to_sql('gdp_per_capita', conn, if_exists='replace', index=False)
    cur.execute("DELETE FROM vaccine_info WHERE instr(`Daily vaccine per 100 people`, '%')>0")
    cur.execute("ALTER TABLE vaccine_info ADD COLUMN 'ISO Code' TEXT")
    conn.commit()

# Not Proceed until user inputs the correct information and format
while True:
    try:
        country = input("Please input a country you want to look up for coronavirus and vaccine info\n")
        user_country = country
        country_code = pycountry.countries.search_fuzzy(user_country)[0].alpha_2
        break
    except:
        print("Please reenter a correct country name!")
        continue

while True:
    user_date = input('Please input a date you want to look up the global COVID-19 info between 2021-01-01 and '
                      '2021-04-30 in the format YYYY-MM-DD:\n')
    user_date = datetime.datetime.strptime(user_date, "%Y-%m-%d").date()

    if datetime.datetime.strptime('2021-01-01', "%Y-%m-%d").date() <= user_date < datetime.datetime.strptime(
            '2021-05-01', "%Y-%m-%d").date():
        break
    print('Please input the correct date')

# Coronavirus trend visualization asking the user to input a country
dates = pd.date_range('20210101', '20210430').strftime("%Y-%m-%d").to_list()
dates = pd.to_datetime(dates)
try:
    # Plot the confirmed cases trend
    cur.execute("SELECT * From Coronavirus_info WHERE `ISO Code`=?", (country_code,))
    confirmed_cases = list(cur.fetchall()[0][3:])
    conn.commit()
    plt.figure("Total Confirmed Cases")
    confirmed_title = 'Confirmed COVID-19 Cases within 2021 in %s' % user_country
    plt.title(confirmed_title)
    plt.xlabel("Date")
    plt.ylabel("Total Confirmed Cases Number")
    plt.plot(dates, confirmed_cases, color='orange')
    plt.xticks(rotation=90)
    plt.savefig("confirmed_cases.jpg")
except:
    pass

try:
    # Plot deaths cases trend
    cur.execute("SELECT * From Coronavirus_info WHERE `ISO Code`=?", (country_code,))
    death = cur.fetchall()[1][3:]
    conn.commit()
    plt.figure("Total Deaths Cases")
    death_title = 'Deaths COVID-19 Cases within 2021 in %s' % user_country
    plt.title(death_title)
    plt.xlabel("Date")
    plt.ylabel("Total Deaths Cases Number")
    plt.plot(dates, death, color='orange')
    plt.xticks(rotation=90)
    plt.savefig("deaths.jpg")
except:
    pass

try:
    # Plot daily new cases trend
    cur.execute("SELECT * From Coronavirus_info WHERE `ISO Code`=?", (country_code,))
    new_cases = cur.fetchall()[2][3:]
    conn.commit()
    plt.figure("Daily New Cases")
    new_title = 'Daily New COVID-19 Cases within 2021 in %s' % user_country
    plt.title(new_title)
    plt.xlabel("Date")
    plt.ylabel("New Cases Number")
    plt.plot(dates, new_cases, color='orange')
    plt.xticks(rotation=90)
    plt.savefig("new_cases.jpg")
except:
    pass

plt.show()

print('Now performing the linear regression analysis!')

# Add country ISO 2-digit code into vaccine_info table
cur.execute("SELECT * FROM vaccine_info")
countries = cur.fetchall()
country_code_dict = {}

for country in countries:
    try:
        country_code_dict[country[0]] = pycountry.countries.search_fuzzy(country[0])[0].alpha_2
    except:
        continue

for key, val in country_code_dict.items():
    cur.execute("UPDATE vaccine_info SET `ISO Code`=? WHERE `Country name`=?", (val, key))
    conn.commit()

# Data Adjusting for country code---Hard Core
cur.execute("UPDATE vaccine_info SET `ISO Code`='KR' WHERE `Country name`='South Korea'")
cur.execute("UPDATE vaccine_info SET `ISO Code`='LA' WHERE `Country name`='Laos'")
cur.execute("UPDATE vaccine_info SET `ISO Code`='CV' WHERE `Country name`='Cape Verde'")
cur.execute("UPDATE vaccine_info SET `ISO Code`='CD' WHERE `Country name`='Democratic Republic of Congo'")
cur.execute("DELETE FROM vaccine_info WHERE `Country name`='Africa'")
conn.commit()
# Delete all the continent and world info
cur.execute("DELETE FROM vaccine_info WHERE `ISO CODE` is NULL")
conn.commit()

# Draw the scatter and linear regression plot
cur.execute(
    "SELECT `GDP` ,`Accumulated vaccine per 100 people`FROM gdp_per_capita, vaccine_info WHERE "
    "gdp_per_capita.`Country CODE`=vaccine_info.`ISO CODE`")
pairs = cur.fetchall()
conn.commit()

GDP = []
Accumulated = []
df_dict = {}

for pair in pairs:
    GDP.append(pair[0])
    Accumulated.append(pair[1])

df_dict['GDP'] = GDP
df_dict['Accumulated vaccine per 100 people'] = Accumulated

# Linear Regression and convert into correct dataframe format
examOrder = OrderedDict(df_dict)
examDf = pd.DataFrame(df_dict)
x_exam = examDf.loc[:, "GDP"]
y_exam = examDf.loc[:, "Accumulated vaccine per 100 people"]

x_train, x_test, y_train, y_test = train_test_split(x_exam, y_exam, train_size=0.8)

print('There are %d total data' % x_exam.shape[0])
print('There are %d total train data' % x_train.shape[0])
print('There are %d total test data' % x_test.shape[0])

x_train = x_train.values.reshape(-1, 1)
y_train = y_train.values.reshape(-1, 1)
model = LinearRegression()
model.fit(x_train, y_train)

plt.scatter(x_train, y_train, color='blue', label="train data")
plt.scatter(x_test, y_test, color="red", label="test data")
y_train_pred = model.predict(x_train)
plt.plot(x_train, y_train_pred, color='black', linewidth=3, label="best line")
plt.legend(loc=2)
plt.xlabel("GDP per capita")
plt.ylabel("Accumulated vaccine per 100 people")
plt.savefig("scatter&regression.jpg")
plt.show()

# Print out the statistical exam data
get_lr_stats(x_train, y_train, model)

# Print the vaccine information for the country user inputted
cur.execute("SELECT * FROM vaccine_info WHERE `ISO Code`=?", (country_code,))

tb = pt.PrettyTable()
tb.field_names = ['Country name', 'Total Doses', 'Accumulated vaccine per 100 people', 'Daily vaccine per 100 people',
                  'Share of population got one vaccine', 'ISO Code']
row = cur.fetchall()
conn.commit()
try:
    tb.add_row(list(row[0]))
    print("The table below shows the COVID-19 vaccine info you entered")
    print(tb)
except:
    print(
        "The table below shows the COVID-19 vaccine info you entered is not available because it does not report and "
        "publish enough vaccine information")

# Show the world map of the date which user input
user_date = str(user_date)
cur.execute("SELECT `ISO Code`, \"" + user_date + "\" FROM coronavirus_info WHERE status='Confirmed Cases'")
confirmed_cases = cur.fetchall()
conn.commit()

confirmed_dict = {}
for confirmed_case in confirmed_cases:
    try:
        confirmed_dict[confirmed_case[0].lower()] = confirmed_case[1]
    except:
        continue

wm_style = RS('#191970', base_style=LCS)
wm = pygal.maps.world.World(style=wm_style)
wm.title = "Confirmed Covid Cases World Map in %s " % user_date
wm.add("Confirmed Cases", confirmed_dict)
wm.render_to_file("Confirmed_cases.svg")

cur.execute("SELECT `ISO Code`, \"" + user_date + "\" FROM coronavirus_info WHERE status='Deaths'")
deaths_cases = cur.fetchall()
conn.commit()

deaths_dict = {}
for deaths_case in deaths_cases:
    try:
        deaths_dict[deaths_case[0].lower()] = deaths_case[1]
    except:
        continue

wm_style = RS('#006400', base_style=LCS)
wm = pygal.maps.world.World(style=wm_style)
wm.title = "Deaths Covid Cases World Map in %s " % user_date
wm.add("Deaths Cases", deaths_dict)
wm.render_to_file("deaths_cases.svg")

cur.execute("SELECT `ISO Code`, \"" + user_date + "\" FROM coronavirus_info WHERE status='New Cases'")
new_cases = cur.fetchall()
conn.commit()
conn.close()
new_dict = {}
for new_case in new_cases:
    try:
        new_dict[new_case[0].lower()] = new_case[1]
    except:
        continue

wm_style = RS('#800000', base_style=LCS)
wm = pygal.maps.world.World(style=wm_style)
wm.title = "Daily New Covid Cases World Map in %s " % user_date
wm.add("New Cases", new_dict)
wm.render_to_file("new_cases.svg")

