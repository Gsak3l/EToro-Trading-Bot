import multiprocessing
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

manager = multiprocessing.Manager()
stock_info = manager.list()
stocks_to_buy = manager.list()
flags = manager.list()


def calculate_what_to_buy(local_stocks_to_buy, amount_of_money):
    # waiting to retrieve the data from the get_stocks_info function
    while len(flags) == 0:
        continue
    stock_info_2 = sorted(stock_info, key=lambda x: x[3])  # sorting the array by the strength of the stock
    # calculating how many stocks have a decent strength
    positive_stocks = 0
    for stock in stock_info_2:
        if stock[3] > 0:
            positive_stocks = + positive_stocks
    money_step = 4
    separator = amount_of_money / 10
    # opposite for
    for stock in reversed(stock_info_2):
        # checking if the stock strength is enough, and if there are enough money
        if stock[3] > 0 and amount_of_money > 0 and money_step >= 1:
            # appending the array with the stock names and the amount of money to spent on them
            local_stocks_to_buy.append([stock[0], money_step * separator])
            amount_of_money = amount_of_money - money_step * separator
            # removing the money from the amount_of_money
            money_step = money_step - 1  # decreasing the value of the step
    for i in local_stocks_to_buy:
        print(i)
    flags.append(True)


# noinspection PyBroadException
class Auto_trading_bot:
    def __init__(self):
        # chrome 86 driver, you might have to install a different file here
        opts = Options()
        # changing user-agent because etoro detects the automated browser somehow
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.183 Safari/537.36")
        self.bot = webdriver.Chrome(executable_path='./chromedriver', options=opts)

    def get_stock_info(self, local_stock_info):
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
            stock_names = row.find_elements_by_tag_name('td')[0].text  # stock names
            stock_per_change = row.find_elements_by_tag_name('td')[4].text  # stock percentage change
            stock_volume = row.find_elements_by_tag_name('td')[5].text  # stock total volume
            try:
                stock_per_change = stock_per_change.split('+', 1)[1]  # getting the numbers and not the +
            except:
                stock_per_change = "-10.1"  # we don't need negative values
            stock_per_change = stock_per_change.split('.', 1)[0]  # not getting decimal
            stock_volume = stock_volume.split('.', 1)[0]  # getting only the millions and not the thousands
            stock_per_change = int(stock_per_change)  # converting to integer
            stock_volume = int(stock_volume)  # converting to int
            # calculating the buying value
            buying_value = 3 * stock_per_change + 2 * stock_volume
            # appending the array's row
            local_stock_info.append([stock_names, stock_per_change, stock_volume, buying_value])
        flags.append(True)
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
        time.sleep(5)
        # clicking the sign in button
        bot.find_element_by_xpath('//button[@automation-id="login-sts-btn-sign-in"]').click()
        # waiting 30 seconds after we get all the data
        while len(flags) != 1:
            continue
        time.sleep(20)  # you are supposed to somehow change your ip now
        # clicking the sign in button again
        bot.find_element_by_xpath('//button[@automation-id="login-sts-btn-sign-in"]').click()
        # waiting to get the calculated values from calculate_what_to_buy
        while len(flags) != 2:
            continue
        # waiting for the page to load
        time.sleep(5)
        # locating the virtual portfolio button, change this if you want to invest in your actual portfolio
        # !!! not recommended, I don't know anything about stocks !!!
        bot.find_element_by_tag_name('et-select').click()  # clicking the "REAL" portfolio button to switch to virtual
        # wait half a second
        time.sleep(0.5)
        # finding all the options from the menu
        options = bot.find_elements_by_tag_name('et-select-body-option')
        for option in options:
            # clicking the virtual portfolio option
            if option.find_element_by_tag_name('span').text == 'Virtual Portfolio':
                option.click()
        time.sleep(2)
        # clicking the final warning button
        bot.find_element_by_xpath(
            '/html/body/div[5]/div[2]/div/et-dialog-container/et-portfolio-toggle-account/div/div[3]/a').click()
        for stock in stocks_to_buy:  # looping to buy each stock from the stocks_to_buy list
            bot.find_element_by_tag_name('input').send_keys(stock[0])  # searching for the stock
            time.sleep(1)  # waiting for the results to appear
            bot.find_element_by_class_name('trading-autocomplete-wrapper').find_element_by_class_name(
                'search-result-name-full').click()  # clicking the right stock from the stocks section
            time.sleep(2)
            # finding the trade button
            try:
                bot.find_element_by_tag_name('trade-button').click()  # clicking the trade button
                bot.find_element_by_tag_name('input').send_keys(stock[1])  # typing the amount of money
                buttons = bot.find_elements_by_tag_name('button')  # finding all the buttons
                for button in buttons:
                    if button.text == 'Set Order                        ':
                        button.click()  # clicking the right button
            except:
                pass
            time.sleep(2)
        # bot.close()  # shuts down the bot


if __name__ == '__main__':
    bot1 = Auto_trading_bot()
    bot2 = Auto_trading_bot()
    process1 = multiprocessing.Process(target=bot1.get_stock_info, args=(stock_info,))
    process2 = multiprocessing.Process(target=calculate_what_to_buy, args=(stocks_to_buy, 1500))
    process3 = multiprocessing.Process(target=bot2.buy_stocks, args=("email address goes here", "password goes here"))
    process1.start()
    process2.start()
    process3.start()
    process1.join()
    process2.join()
    process3.join()
