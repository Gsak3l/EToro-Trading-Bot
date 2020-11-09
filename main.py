import multiprocessing
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

manager = multiprocessing.Manager()
stock_names = manager.list()
stock_per_change = manager.list()
stock_volume = manager.list()


class Auto_trading_bot:
    def __init__(self):
        # chrome 86 driver, you might have to install a different file here
        opts = Options()
        # changing user-agent because etoro detects the automated browser somehow
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.183 Safari/537.36")
        self.bot = webdriver.Chrome(executable_path='./chromedriver', options=opts)

    def get_tables(self, local_stock_names, local_stock_per_change, local_stock_volume):
        bot = self.bot
        bot.get('https://finance.yahoo.com/most-active')  # reaching the site
        buttons = bot.find_elements_by_tag_name('button')  # getting all the buttons
        for button in buttons:
            if button.get_attribute('value') == 'agree':
                button.click()  # clicking the consent button
                break  # breaking the loop (or the if, I am not sure)
        # clicking twice the % change on the stocks table
        for i in range(2):
            time.sleep(3)  # waiting for the table content to load
            bot.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/section/div/'
                                      'div[2]/div[1]/table/thead/tr/th[5]').click()
        time.sleep(5)
        # getting the entire table
        table = bot.find_element_by_tag_name('tbody')
        # getting all the rows
        rows = table.find_elements_by_tag_name('tr')
        for row in rows:
            # getting the first column for each row, the name of the stock
            # and appending the global list with these names
            local_stock_names.append(row.find_elements_by_tag_name('td')[0].text)
            # doing the same for the % change
            local_stock_per_change.append(row.find_elements_by_tag_name('td')[4].text)
            # once again for the total volume
            local_stock_volume.append(row.find_elements_by_tag_name('td')[5].text)
        bot.close()  # shuts down the bot

    def buy_stocks(self, email, password):
        bot = self.bot
        bot.get('https://www.etoro.com/login')  # accessing the etoro website
        form = bot.find_element_by_tag_name('form')  # finding the form
        inputs = form.find_elements_by_tag_name('input')  # getting all the inputs available in the form
        # filling the form with the email and password
        inputs[0].send_keys(email)
        inputs[1].send_keys(password)
        # sleeping for a while before clicking the sign in button
        time.sleep(30)
        bot.find_element_by_xpath('//button[@automation-id="login-sts-btn-sign-in"]').click()


if __name__ == '__main__':
    bot1 = Auto_trading_bot()
    bot2 = Auto_trading_bot()
    process1 = multiprocessing.Process(target=bot1.get_tables, args=(stock_names, stock_per_change, stock_volume))
    process2 = multiprocessing.Process(target=bot2.buy_stocks, args=("email address goes here", "password goes here"))
    process1.start()
    process2.start()
    process1.join()
    process2.join()
