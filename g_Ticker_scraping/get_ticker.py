from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from tqdm import tqdm


def get_ticker() -> None:
    
    """
    Get the ticker from marketstack.com

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    url = "https://marketstack.com/search"

    #driver is firefox
    driver = webdriver.Firefox(executable_path="/home/flotchet/Code/geckodriver")
    driver.get(url)

    for i in tqdm(range(2_048)):

        #wait 2seconds
        sleep(2)
        #wait for the table to load
        WebDriverWait(driver, 10_000_000).until(lambda d: d.find_element(By.XPATH, "/html/body/div/section[2]/div/div[2]/table/tbody"))

        #Get the table element
        table = driver.find_element(By.XPATH, "/html/body/div/section[2]/div/div[2]/table/tbody")

        #save the table into a single csv
        with open(f"data/ticker.csv", "a") as f:
            for row in table.find_elements(By.TAG_NAME, "tr"):
                for cell in row.find_elements(By.TAG_NAME, "td"):
                    f.write(cell.text + ",")
                f.write("\n")

        #scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        #wait for the next button to load
        WebDriverWait(driver, 10_000_000).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/section[2]/div/div[2]/a[2]'))).click()

    #close the driver
    driver.close()
        


if __name__ == "__main__":
    get_ticker()