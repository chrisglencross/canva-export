#!/usr/bin/env python3

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, NoSuchElementException

URL = "http://www.epsomandewellharriers.org"
HEADLESS = True


def login_to_captive_portal(url, headless=True):
    options = Options()
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.binary_location = '/usr/bin/chromium'

    service = Service(executable_path='/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
        print(f"Navigated to: {url}") 
    except WebDriverException as e:
        print(f"Error: Failed to navigate to URL: {url} - {e}")
        driver.quit()
        return False

    if "Epsom & Ewell Harriers" in driver.title:
        print(f"No captive portal detected: {driver.title}")
        driver.quit()
        return True

    try:
        submit_button = driver.find_element(By.CLASS_NAME, "button")
    except NoSuchElementException:
        print("Error: Could not find login form elements. Check the HTML of the captive portal page.")
        driver.quit()
        return False

    submit_button.click()
    print("Submitted the form.")

    time.sleep(5)

    try:
        if "Epsom & Ewell Harriers" in driver.title:
            print(f"Login successful (title changed): {driver.title}")
            driver.quit()
            return True

        print("Warning: Could not reliably determine login status.")
        driver.quit()
        return False

    except Exception as e:
        print(f"Error checking login status: {e}")
        driver.quit()
        return False


def main():
    retries = 3
    delay = 5

    for attempt in range(retries):
        print(f"Attempt {attempt + 1} to login to captive portal for {URL}")
        success = login_to_captive_portal(URL, HEADLESS)
        if success:
            print("Successfully connected to the internet.")
            return
        else:
            print(f"Login failed.  Retrying in {delay} seconds...")
            time.sleep(delay)
    print("Failed to login to the captive portal after multiple attempts.")


if __name__ == "__main__":
    main()
