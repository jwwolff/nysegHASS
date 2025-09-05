import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import re
from selenium.webdriver.chrome.options import Options

class NysegScraper(object):
    def fetch(username, password):
        chrome_options = Options()
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")  # Recommended for Windows
        chrome_options.add_argument("--window-size=1920,1080")  # Optional: ensures full page rendering
        chrome_options.add_argument("--no-sandbox")  # Optional: useful in some Linux environments
        chrome_options.add_argument("--disable-dev-shm-usage")  # Optional: avoids shared memory issues

        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 20)
        actions = ActionChains(driver)

        loginPage = "https://www.nyseg.com/c/portal/login?redirect=https://portal.nyseg.com/auth"
        driver.get(loginPage)

        # Login
        emailInput = wait.until(EC.presence_of_element_located((By.ID, "_com_liferay_login_web_portlet_LoginPortlet_login")))
        emailInput.send_keys(username)

        passInput = driver.find_element(By.ID, "_com_liferay_login_web_portlet_LoginPortlet_password")
        passInput.send_keys(password)

        loginButton = driver.find_element(By.XPATH, "//button[contains(@id,'_com_liferay_login_web_portlet_LoginPortlet')]")
        loginButton.click()

        # Wait for "View More Energy Insights" button
        MoreDataButton = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'View More Energy Insights')]")))
        driver.execute_script("arguments[0].scrollIntoView();", MoreDataButton)
        time.sleep(1)
        MoreDataButton.click()

        # Switch to new window
        wait.until(lambda d: len(d.window_handles) > 1)
        original_window = driver.current_window_handle
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                break

        # Wait for usage panel
        compareUsagePanel = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='engage_insights_explore']")))
        driver.execute_script("arguments[0].scrollIntoView();", compareUsagePanel)

        # Click "Day" button
        dayButton = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='engage_insights_explore']//div[contains(text(),'Day')]")))
        driver.execute_script("arguments[0].scrollIntoView();", dayButton)
        dayButton.click()

        # Offset date
        offset_date = datetime.today() + timedelta(days=2)
        Date = offset_date.strftime('%Y-%m-%d')
        Data = []

        # Extract data from bars
        BarElements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='engage-chart-bar']")))
        for bar in BarElements:
            actions.move_to_element(bar).perform()
            tooltip = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='chart-tooltip__value' and contains(text(), 'kWh')]")))
            match = re.search(r'\d+\.\d+', tooltip.text)
            if match:
                Data.append(float(match.group()))

        return Date,Data
