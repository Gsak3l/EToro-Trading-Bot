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
        # clicking twice the % change on the stocks table
        for i in range(2):
            time.sleep(5)  # waiting for the table content to load
            bot.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/section/div/'
                                      'div[2]/div[1]/table/thead/tr/th[4]').click()
        # getting the items of the body hopefully
        table = bot.find_element_by_tag_name('tbody')
        rows = table.find_elements_by_tag_name('tr')
        print(len(rows))


if __name__ == '__main__':
    bot1 = Auto_trading_bot()
    process1 = multiprocessing.Process(target=bot1.get_tables, )
    process1.start()
    process1.join()
