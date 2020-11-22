import multiprocessing
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

manager = multiprocessing.Manager()
stock_info = manager.list()
stocks_to_buy = manager.list()
flags = manager.list()


def calculate_what_to_buy(local_stocks_to_buy):
    # waiting to retrieve the data from the get_stocks_info function
    while len(flags) == 0:
        continue
    stock_info_2 = sorted(stock_info, key=lambda x: x[3])  # sorting the array by the strength of the stock
    step = 0
    total = 0
    # calculating how many stocks have a positive strength
    for stock in stock_info_2:  # opposite for
        if stock[1] >= 1:  # counting how many stocks are positive
            step += 1  # not sure what I am doing here
            total += step  # it's my own idea, I swear
            local_stocks_to_buy.append([stock[0], step])
    flags.append(total)


# noinspection PyBroadException
class Auto_trading_bot:
    def __init__(self):
        # chrome 86 driver, you might have to install a different file here
        opts = Options()
        # changing user-agent because etoro detects the automated browser somehow
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.183 Safari/537.36")
        self.bot = webdriver.Chrome(executable_path='./chromedriver', options=opts)

    def close_open_stocks(self):
        bot = self.bot

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
        time.sleep(30)  # you are supposed to somehow change your ip now
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
        time.sleep(2)
        # THIS CLOSES ALL THE STOCKS WE HAVE SO FAR
        # clicking the portfolio button
        bot.find_element_by_xpath(
            '/html/body/ui-layout/div/div/div[1]/et-layout-menu/div/div[2]/div[1]/a[2]/span').click()
        time.sleep(2)
        # getting all the stocks we already have bought
        active_stocks = bot.find_elements_by_class_name('table-static-cell-info')
        active_stock_names = []
        for stock in active_stocks:
            active_stock_names.append(stock.find_element_by_tag_name('div').text)
        buttons = bot.find_elements_by_tag_name('ui-table-button-cell')  # locating all the buttons by class
        for button in buttons:  # clicking all the buttons to make the options appear
            button.click()
            dropdown = button.find_element_by_class_name('drop-select-box')  # getting the dropdown box
            dropdown_options = dropdown.find_elements_by_tag_name('div')  # getting all the options
            for opt in dropdown_options:  # looping through all options
                if opt.text == 'Close':  # clicking the right one
                    opt.click()
            # clicking the label that enables the button
            time.sleep(1)
            bot.find_element_by_xpath(
                '/html/body/div[6]/div[2]/close-all-positions/div/div[3]/div[3]/div[1]/div/label').click()
            # clicking the button to close the stock
            time.sleep(1)
            bot.find_element_by_class_name('close-all-positions-button-wrapper').find_element_by_tag_name(
                'button').click()
        for stock in reversed(stocks_to_buy):  # looping to buy each stock from the stocks_to_buy list
            bot.find_element_by_tag_name('input').clear()  # clearing the input
            bot.find_element_by_tag_name('input').send_keys(stock[0])  # searching for the stock
            time.sleep(1)  # waiting for the results to appear
            try:
                bot.find_element_by_class_name('trading-autocomplete-wrapper').find_element_by_class_name(
                    'search-result-name-full').click()  # clicking the right stock from the stocks section
                time.sleep(1)  # waiting for the data to load
                bot.find_element_by_tag_name('trade-button').click()  # clicking the trade button
                time.sleep(1)
                if stock[1] > 20:
                    for i in range(2):
                        bot.find_element_by_class_name('stepper-plus').click()  # clicking plus twice
                        time.sleep(1)
                elif stock[1] > 10:
                    bot.find_element_by_class_name('stepper-plus').click()  # clicking plus once
                elif stock[1] > 5:
                    bot.find_element_by_class_name('stepper-minus').click()  # clicking the minus once
                else:
                    for i in range(2):
                        bot.find_element_by_class_name('stepper-minus').click()  # clicking the minus twice
                        time.sleep(1)
                time.sleep(1)
                # clicking the final trade button
                bot.find_element_by_xpath('/html/body/div[6]/div[2]/div/div/div[2]/div/div[4]/div/button').click()
            except:
                pass
            time.sleep(2)
            # bot.close()  # shuts down the bot


if __name__ == '__main__':
    bot1 = Auto_trading_bot()
    bot2 = Auto_trading_bot()
    process1 = multiprocessing.Process(target=bot1.get_stock_info, args=(stock_info,))
    process2 = multiprocessing.Process(target=calculate_what_to_buy, args=(stocks_to_buy,))
    process3 = multiprocessing.Process(target=bot2.buy_stocks, args=("email address goes here", "password goes here"))
    process1.start()
    process2.start()
    process3.start()
    process1.join()
    process2.join()
    process3.join()
