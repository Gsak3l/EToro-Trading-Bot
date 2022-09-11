import time

import pandas as pd
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class EToroBot:
    def __init__(self, account_name, account_email, account_password, page_load_timeout, trading_timeout):
        self.name = account_name
        self.email = account_email
        self.password = account_password
        self.page_load_timeout = page_load_timeout
        self.trading_timeout = trading_timeout

    # function that allows you to log in to the account
    def login(self, driver):
        driver.get("https://www.etoro.com/login")

        # bypassing e-Toros login system by changing user agent. Credits github.com/winterdrive
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'"
        })

        # writing email and password on the form
        driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(self.email)
        driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(self.password)

        # I don't like the xpath selector on this one, I will do it by text
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        for button in buttons:
            if button.text == 'Sign in':
                button.click()
                break

        time.sleep(self.page_load_timeout)
        return driver

    # function that allows you to switch to virtual portfolio
    def switch_to_virtual(self, driver):
        driver.find_element(By.LINK_TEXT, 'Switch to Virtual').click()
        time.sleep(self.trading_timeout)
        driver.find_element(By.LINK_TEXT, 'Switch to Virtual Portfolio').click()
        time.sleep(self.page_load_timeout)
        return driver

    # function that allows you to switch to real portfolio
    def switch_to_real(self, driver):
        driver.find_element(By.LINK_TEXT, 'Switch to Real').click()
        time.sleep(self.trading_timeout)
        driver.find_element(By.LINK_TEXT, 'Go to Real Portfolio').click()
        time.sleep(self.page_load_timeout)
        return driver

    # just searches for the stock in the input and then calls buy_stock() to buy the stock
    def search_stock(self, driver, stocks):
        # looping through the stocks, key is the stock and value is the amount
        for key, value in stocks.items():

            # searching for the input field to search for the stock
            all_inputs = driver.find_elements(By.TAG_NAME, 'input')
            for inp in all_inputs:
                if inp.get_attribute('placeholder') == 'Search':
                    inp.send_keys(key)
                    break
            time.sleep(self.trading_timeout)

            # clicking the Trade button
            driver.find_element(By.TAG_NAME, 'trade-button').click()
            time.sleep(self.trading_timeout)

            driver = self.buy_stock(driver, value)  # stock already selected
            time.sleep(self.trading_timeout)

        return driver

    def buy_stock(self, driver, value):
        popup = driver.find_element(By.XPATH, '//*[@id="open-position-view"]')

        # clicking input field and writing amount
        amount = popup.find_element(By.TAG_NAME, 'input')
        amount.click()
        # simulating ctrl+a and backslash, clear() doesn't seem to work
        amount.send_keys(Keys.CONTROL + "a")
        amount.send_keys(Keys.BACKSPACE)
        amount.send_keys(value)

        # clicking set order button
        buttons = popup.find_elements(By.TAG_NAME, 'button')
        for button in buttons:
            if button.text == 'Set Order':
                button.click()  # focusing outside the input box
                time.sleep(self.trading_timeout)
                button.click()  # buying the stock
                break

        return driver


class YahooFinance:
    def __init__(self):
        pass

    @staticmethod
    def bypass_authentication(driver):
        driver.get("https://finance.yahoo.com/most-active?offset=0&count=100")  # 100 most active
        # multi-language, otherwise by text works just fine
        driver.find_element(By.CLASS_NAME, 'btn.primary').click()
        return driver

    @staticmethod
    def get_most_active(driver):
        stocks = driver.find_elements(By.TAG_NAME, 'tr')  # all the stocks in the table
        df_stocks = pd.DataFrame(columns=[
            'Symbol', 'Name', 'Price', 'Change', '%Change', 'Volume', 'Avg Vol (3m)', 'Market Cap', 'PE Ratio (TTM)']
        )

        for stock in stocks[1:]:  # skipping the first one, it's the header
            tds = stock.find_elements(By.TAG_NAME, 'td')
            df_stocks.loc[len(df_stocks.index)] = [
                tds[0].text, tds[1].text, tds[2].text, tds[3].text, tds[4].text,
                tds[5].text, tds[6].text, tds[7].text, tds[8].text
            ]

        return df_stocks, driver


def initialize_driver_options():
    options = ChromeOptions()

    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--log-level=3')
    options.add_argument('--silent')
    options.add_argument('--useAutomationExtension=false')

    return options


def calculate_stocks(df_stocks):
    # calculating the amount of stocks to buy
    stocks = {}
    for index, row in df_stocks.iterrows():
        if row['%Change'] == '-':  # if the stock is down, skip it
            continue

        # calculating the amount of stocks to buy
        amount = int(float(row['Volume'].replace(',', '')) / float(row['Avg Vol (3m)'].replace(',', '')))
        stocks[row['Symbol']] = amount

    return stocks


if __name__ == '__main__':
    webdriver = Chrome(options=initialize_driver_options())

    yahoo_bot = YahooFinance()
    webdriver = yahoo_bot.bypass_authentication(webdriver)
    df, webdriver = yahoo_bot.get_most_active(webdriver)
    stocks_to_buy = calculate_stocks(df)

    # adjust page load timeout and trading timeout according to your internet connection, vpn, ping
    e_toro_bot = EToroBot(
        account_name='',
        account_email='',
        account_password='',
        page_load_timeout=5,
        trading_timeout=2
    )

    webdriver = e_toro_bot.login(webdriver)
    webdriver = e_toro_bot.switch_to_virtual(webdriver)
    # webdriver = e_toro_bot.switch_to_real(webdriver)


    webdriver = e_toro_bot.search_stock(webdriver, stocks_to_buy)
