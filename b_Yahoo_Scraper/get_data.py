#-I-QOF-----------------------------------------------------------------------------------------
import warnings
#i-MATH-----------------------------------------------------------------------------------------
from random import randint
#-I-OS------------------------------------------------------------------------------------------
from time import sleep
from time import time
#-I-PERF----------------------------------------------------------------------------------------
from multiprocessing import Pool
#-I-DS------------------------------------------------------------------------------------------
import pandas as pd
#-I-WEB-----------------------------------------------------------------------------------------
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib3
from bs4 import BeautifulSoup
#-I-DB------------------------------------------------------------------------------------------
import sqlite3
#-----------------------------------------------------------------------------------------------

#connect to the db
def connect(db : str =  "DB/data.db") -> sqlite3.Connection:
    """
    Connect to the database

    Parameters
    ----------
    db: str
        name of the database

    Returns
    -------
    conn: sqlite3.Connection
        connection to the database
    """
    conn = sqlite3.connect(db)
    return conn

#close the connection
def close(conn : sqlite3.Connection) -> None:
    """
    Close the connection to the database

    Parameters
    ----------
    conn: sqlite3.Connection
        connection to the database

    Returns
    -------
    None
    """
    conn.close()
    return None

#get the tickers
def get_tickers(conn : sqlite3.Connection) -> pd.DataFrame:
    """
    Get the tickers from the database

    Parameters
    ----------
    conn: sqlite3.Connection
        connection to the database

    Returns
    -------
    df: pd.DataFrame
        dataframe of the tickers
    """
    df = pd.read_sql_query("SELECT * FROM tickers", conn)
    return df

#add a table to the database
def add_table(conn : sqlite3.Connection, table : str, df : pd.DataFrame) -> None:
    """
    Add a table to the database

    Parameters
    ----------
    conn: sqlite3.Connection
        connection to the database
    table: str
        name of the table
    df: pd.DataFrame
        dataframe to add to the database

    Returns
    -------
    None
    """
    df.to_sql(table, conn, if_exists="replace", index=False)
    return None


def get_data(symbol : str, url : str) -> None:
    
    """
    Get the data from yahoo finance

    Parameters
    ----------
    symbol: str
        ticker symbol
    url: str
        url to scrape

    Returns
    -------
    None
    """

    #get the current minutes of the current hour

    #get the current minutes
    minutes = int(time() / 60) % 60

    #if the minutes are between 0 and 20, then the market is closed

    if ((minutes >= 0 and minutes <= 5) or
        (minutes >= 20 and minutes <= 25) or 
        (minutes >= 40 and minutes <= 45)):
        #sleep for 5 minutes
        sleep(5 * 60) 

    

    #connect to the database
    conn = connect()

    #check if the ticker was already got
    #get the value of got in the table tickers
    got = pd.read_sql_query(f"SELECT got FROM tickers WHERE symbol = '{symbol}'", conn).iloc[0, 0]
    #if got is 1, then the ticker was already got
    if got == 1:
        #close the connection
        close(conn)

        return None

    #change the got from tickers table to true 
    with conn:
        cur = conn.cursor()
        cur.execute("UPDATE tickers SET got = 1 WHERE symbol = ?", (symbol,))

    
    #driver is firefox
    driver = webdriver.Firefox(executable_path="/home/flotchet/Code/geckodriver")

    driver.get(url)

        
    
    try:
        #click accept
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div/div/form/div[2]/div[2]/button[1]'))).click()
    except Exception as e:
        print(e) 
        print("No accept button")
        driver.close()
        close(conn)
        sleep(randint(5, 20))
        return None


    try:
        #click cross
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div[4]/div/div/div[1]/div/div/div/div/div/section/button[1]'))).click()
    except:
        print("No cross button")
        driver.close()
        close(conn)
        sleep(randint(5, 20))
        return None
    

    try:
        #click the dropdown menu
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/section/div[1]/div[1]/div[1]/div/div/div[1]'))).click()
    except:
        print("No dropdown menu")
        driver.close()
        close(conn)
        sleep(randint(5, 20))
        return None

    try:
        #click max
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/section/div[1]/div[1]/div[1]/div/div/div[2]/div/ul[2]/li[4]/button'))).click()
    except:
        print("No max button")
        driver.close()
        close(conn)
        sleep(randint(5, 20))
        return None

    try:
        #click apply
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/section/div[1]/div[1]/button'))).click()
    except:
        print("No apply button")
        driver.close()
        close(conn)
        sleep(randint(5, 20))
        return None

    sleep(1)

    try:
        #scroll to this element of the page: /html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/section/div[2]/table/tfoot/tr/td/span[2]/span
        element = WebDriverWait(driver, 25).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".Mstart\(20px\) > span:nth-child(1)")))
        for _ in range(200):
            driver.execute_script("return arguments[0].scrollIntoView(true);", element)
            sleep(0.05)
    except:
        driver.close()
        close(conn)
        sleep(randint(5, 20))
        print("No scroll")

    try:
        #get the tables
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        driver.close()

    except:
        print("No table")
        close(conn)
        driver.close()
        sleep(randint(5, 20))
        return None
    
    
    #get the data from the table

    #get the headers
    headers = [th.text for th in table.find("thead").find_all("th")]
    #get the rows
    rows = table.find("tbody").find_all("tr")
    #get the data
    data = [[td.text for td in rows[i].find_all("td")] for i in range(len(rows))]
    #create the dataframe
    df = pd.DataFrame(data, columns=headers)

    #add the data to the database
    add_table(conn, symbol, df)

    #close the connection
    close(conn)

    return None

#https://www.nasdaq.com/market-activity/stocks/msft/historical

#main
if __name__ == "__main__":
    #connect to the database
    conn = connect()
    #get the tickers
    tickers = get_tickers(conn)
    #close the connection
    close(conn)
    #print the head
    print(tickers.head())



    n_process = 8
    try:
        #Create the pool of workers
        with Pool(n_process) as pool:
            #map the function to the tickers
            #autokill a process after 2mins
            pool.starmap(get_data, zip(tickers["symbol"], tickers["url"]))

    except urllib3.exceptions.MaxRetryError:
        warnings.warn("MaxRetryError occured")

    except WebDriverException:
        warnings.warn("WebDriverException occured")

    except Exception:
        warnings.warn("An exception occured")


    print("Done")