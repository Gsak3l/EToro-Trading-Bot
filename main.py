import multiprocessing
import time

from random import randint
from selenium import webdriver
from selenium.webdriver.support.ui import Select


class Auto_trading_bot:
    def __init__(self):
        # chrome 86 driver, you might have to install a different file here
        self.bot = webdriver.Chrome(executable_path='./chromedriver')

    def get_tables(self):
        bot = self.bot
        bot.get('https://finance.yahoo.com/most-active')  # reaching the site
        buttons = bot.find_elements_by_tag_name('button')  # getting all the buttons
        for button in buttons:
            if button.get_attribute('value') == 'agree':
                button.click()  # clicking the consent button
                break  # breaking the loop (or the if, I am not sure)


if __name__ == '__main__':
    bot1 = Auto_trading_bot()
    bot2 = Auto_trading_bot()
