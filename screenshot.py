from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os

# Config
screenshotDir = "Screenshots"
screenWidth = 1200  # Adjusted width for better view
screenHeight = 2000  # Adjusted height for longer posts

def getPostScreenshot(filePrefix, script):
    print("Taking screenshot of the post...")
    driver, wait = __setupDriver(script.url)
    script.titleSCFile = __takeScreenshot(filePrefix, driver, wait, "Post")
    print(f"Title screenshot file saved at: {script.titleSCFile}")
    driver.quit()

def __takeScreenshot(filePrefix, driver, wait, handle="Post"):
    method = By.TAG_NAME if handle == "Post" else By.ID
    try:
        search = wait.until(EC.presence_of_element_located((method, "shreddit-post")))
        driver.execute_script("window.focus();")

        if not os.path.exists(screenshotDir):
            os.makedirs(screenshotDir)

        fileName = f"{screenshotDir}/{filePrefix}-{handle}.png"
        with open(fileName, "wb") as fp:
            fp.write(search.screenshot_as_png)
        print(f"Screenshot saved to {fileName}")
        return fileName
    except TimeoutException as e:
        print(f"TimeoutException while waiting for element with handle '{handle}': {e}")
        print(f"Current URL: {driver.current_url}")
        print(f"Page source: {driver.page_source[:2000]}")  # Print first 2000 characters of page source for debugging
        raise

def __setupDriver(url: str):
    options = webdriver.FirefoxOptions()
    options.headless = False
    options.enable_mobile = False
    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 20)  # Increased timeout to 20 seconds

    driver.set_window_size(width=screenWidth, height=screenHeight)
    driver.get(url)
    print(f"Opened URL: {url}")

    return driver, wait
