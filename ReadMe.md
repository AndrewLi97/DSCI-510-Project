## How To Run the Code
### Important to read before you run the whole scraper file:
The main.py file uses Selenium library for web scrapping because the ourworldindata.org uses dynamic and lazing loading techniques to display its tables after I carefully check the source code of the website.

The selenium library needs to download a WebDriver in order to run. Please check the https://www.google.com/chrome/ to download the Google Chrome in your computer first and then https://sites.google.com/a/chromium.org/chromedriver/downloads to download the WebDriver into your computer.
***This is not included in requirements.txt because WebDriver is not a python package but rather an individual file.***

**The WebDriver must match with the version of your Google Chrome.**
*I have included the web driver I used in the zip file I submit. It is for MacBook Google Chrome version 90.*

**You MUST include your WebDriver into your Path environment variable before you run the code.**
For how to include the WebDriver into your Path environment variable. Please check:

- For Windows: refer to https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/
- For Mac: Simply copy & paste the WebDriver file into **/usr/local/bin** folder and it will work out.

### MUST KNOW:

#### Expected Time Last when run the code
The code needs to uses API for thousands of times to scrape the data so **Internet Connection Quality is important** and it also has nested for loops so it may take **30 minutes or even longer** based on your computer configuration to run the program and scrape the data and perform the analysis.

#### Exceptions when run the code
When I test my program, the rows it returns for coronavirus information is not always the same because the connection to api is not stable, which means it may have lacking rows if you rerun the program. However, if everything is good, you should have 190 countries coronavirus information which means 570 rows in coronavirus_info table in the final_project.db.

### Zip File Structure
- You_Li_DSCI510_main.py which is the main program file
- requirements.txt
- ChromeDriver for Selenium WebDriver
- database folder contains a sqlite database file final_project.db
- A ReadMe.md about how to run the code and the expected results
- sample_output folder that has sample Data visualization files that has three .png files show the trend of coronavirus cases (total, deaths and new), one scatter and linear regression png file and three .svg file shows the coronavirus cases information worldwide for specific date.


#### Detailed information
- You_Li_DSCI510_main.py file have --static /path/final_project.db arguments. If you input --static in the command line with dataset file path behind, it will connect the database file and ask for user input.
- You_Li_DSCI510_main.py takes about 30 minutes to run if you choose to run the whole program without giving specific arguments in the command line.
- You_Li_DSCI510_main.py needs to include the ChromeDriver into Path environment variable in order to run. Please Check the information above.
- The path to datasets folder is Path/You_Li_DSCI510_FinalProject/dataset_file/final_project.db

### Sample input and expected output
After scrapping the data from three data sources, the program will write them into three csv files first and convert them into a SQLite database file called "final_project.db".

The program will then ask the user to input a country name and a date between 2021-01-01 and 2021-04-30 in the format of YYYY-MM-DD to generate outputs.

**Sample**:

The user inputs *USA* as country name and then input *2021-03-25* as date.
The program will open 3 windows that show the coronavirus cases trend for USA first.
When you close the first 3 figure windows the program will pop out another scatter and regression line plot.
When you close the scatter figure, the program will print out following information then in the terminal:

***
There are 166 total data
There are 132 total train data
There are 34 total test data
The linear regression formula between GDP and Accumulated vaccine per 100 people is  y=[10.16775189] + [0.00062786]x
The statistical exam data for regression formula is:
R^2： [0.29216391]；
TSS： [94098.22732424]；
RSS： [27492.10632158]；
ESS： [66606.12100266]；

The table below shows the COVID-19 vaccine info you entered
+---------------+-------------+------------------------------------+------------------------------+-------------------------------------+----------+
|  Country name | Total Doses | Accumulated vaccine per 100 people | Daily vaccine per 100 people | Share of population got one vaccine | ISO Code |
+---------------+-------------+------------------------------------+------------------------------+-------------------------------------+----------+
| United States | 249570000.0 |               74.62                |             0.64             |                44.4%                |    US    |
+---------------+-------------+------------------------------------+------------------------------+-------------------------------------+----------+
***

Besides it will also save 4 png files that have 3 plots showing the trend of coronavirus cases in America and one scatter plot showing the relationship between GDP per capita and accumulated vaccine per 100 people.

It will also generate 3 svg files showing the world map in different color to represent the number of coronavirus cases information at the date of 2021-03-25.

**Notes:**

- The sample data and output above are not fixed. The linear regression formula and statistical exam data will change slightly because it will random select the train data and test data each time the program runs. And the table of vaccine information is updated daily. Each day you scrape from the website, the number will be probably different from the last day you run it.

- The program supports fuzzy input for country, which means for USA, you could either input 'USA','US','United States of America','United States' or even 'America'.
