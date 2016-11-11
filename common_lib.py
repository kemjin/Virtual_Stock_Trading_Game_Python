# Project Jiminel (Virtual Stock market game)
# core engine: getting a stock price from google finance

import urllib2, sys, time, os, re
import sqlite3
from db_function import *


def total_profit(db_name):
    total_amount = 0.0000
    db = sqlite3.connect(db_name)
    profile_table = db.execute("SELECT * from PROFILE")
    for row in profile_table:
        total_amount = (float(row[3]) / 2)
    print "Total profit you have made so far is $" + str(total_amount) 

##
def portfolio_status(db_name):
    price_list = []
    db = sqlite3.connect(db_name)

    print ("Current Portfolio Status")
    cursor = db.execute("SELECT * from TRADING")
    for row in cursor:
        price = get_stock_price_only(row[3])
        if row[2] == 'BUYLONG':
            if float(price) > float(row[1]):
                print str(row[3]) + " BUYLONG and making profit: Get-in: " + str(row[1]) + " vs current: " + str(price)
                profit1 = str((float(price)-float(row[1]))*int(row[4]))
                print "Company: " + str(row[3]) + " PROFIT TOTAL: " + profit1
                price_list.append(profit1)
            else:
                print str(row[3]) + " BUYLONG and losing: Get-in: " + str(row[1]) + " vs current: " + str(price)
                profit1 = str((float(price)-float(row[1]))*int(row[4]))
                print "Company: " + str(row[3]) + " LOSING TOTAL: " + profit1
                price_list.append(profit1)
        elif row[2] == 'SELLSHORT':
            if float(price) < float(row[1]):
                print str(row[3]) + " SELLSHORT and making profit: Get-in: " + str(row[1]) + " vs current: " + str(price)
                profit1 = str(((float(row[1]))-float(price))*int(row[4]))
                print "Company: " + str(row[3]) + " PROFIT TOTAL: " + profit1
                price_list.append(profit1)
            else:
                print str(row[3]) + " SELLSHORT and losing: Get-in: " + str(row[1]) + " vs current: " + str(price)
                profit1 = str(((float(row[1])-float(price)))*int(row[4]))
                print "Company: " + str(row[3]) + " LOSING TOTAL: " + profit1
                price_list.append(profit1)
    total_sum = 0.00
    for price1 in price_list:
        total_sum = total_sum + float(price1)
    print "Total result is " + str(total_sum)
    return



##
def search_own_stock(holding_info, company_name, trading_type):

    # already_owned[0] : Holding stock amount
    # already_owned[1] : Get in price

    holding_amount = 0
    purchased_price = 0
    already_owned = []
    for xx in range (0, len(holding_info)):
                if holding_info[xx][2] == trading_type and holding_info[xx][3] == company_name:
                    holding_amount = int(holding_info[xx][4])
                    purchased_price = float(holding_info[xx][1])
    already_owned.append(holding_amount)
    already_owned.append(purchased_price)
    return already_owned

##
def calculate_profit(getin_price, amount_stock, current_price, accout_type, trading_type):
    original_margin_fund = float(getin_price) * int(amount_stock)
    final_sold_fund = float(current_price) * int(amount_stock)

    if trading_type == 'BUYLONG':
        profit = final_sold_fund - original_margin_fund
        if profit > 0:
            profit = profit * 0.7 # After commision fee and tax
    elif trading_type == 'SELLSHORT':
        profit =  original_margin_fund - final_sold_fund
        if profit > 0:
            profit = profit * 0.7 # After commision fee and tax        

    print "PROFIT: " + str(profit)

    original_own_fund = original_margin_fund / 2
    return original_own_fund + profit


########################################
# RENEW TRADING FUNCTION
########################################
##
def buy_stock(db_name):
    user_profile = get_profile_table(db_name)
    new_trading = []

    # Get holding information first
    holding_info = []
    holding_info = get_holding_table(db_name)

    print "Which company do you want to buy?"
    # Get company name from a user & get the current price
    company_name = raw_input()
    current_price = get_stock_info(company_name)
    max_purchase = float(user_profile[3]) / float(current_price)
    print "Your company is %s and its price is %s" % (company_name, str(current_price))
    print "You can purchase " + str(int(max_purchase)) + " amount stocks"
    print "How many do you want to buy?"
    # Get amount from a user
    trading_amount_request = raw_input()

    if int(trading_amount_request) > int(max_purchase):
        print "You entered greater than you can afford. Try again"
        return

    current_holding = []
    current_holding = search_own_stock(holding_info, company_name, "BUYLONG")

    if int(current_holding[0]) == 0:
        # Update TRADING table
        new_trading.append(user_profile[0])
        new_trading.append(current_price)
        new_trading.append('BUYLONG')
        new_trading.append(company_name)
        new_trading.append(trading_amount_request)
    else:
        avg_price = (int(current_holding[0]) * float(current_holding[1])) + (float(current_price) * int(trading_amount_request))
        total_stock_amount = (int(current_holding[0]) + int(trading_amount_request))
        avg_price = avg_price / total_stock_amount

        # Delete previous purchase because we will insert New purchase record
        delete_whole_company(db_name, company_name, 'BUYLONG')

        new_trading.append(user_profile[0])
        new_trading.append(avg_price)
        new_trading.append('BUYLONG')
        new_trading.append(company_name)
        new_trading.append(total_stock_amount)

    # Update TRADING table
    update_trading_table(new_trading, db_name)
    # Update HISTORY table
    update_history_table(new_trading, db_name)
    # Update remain fund in PROFILE table
    update_remain_fund(db_name, float(user_profile[3]) - (float(current_price) * float(trading_amount_request)), new_trading[0])

    # Delete zero stock (garbage data) just for in case
    delete_zero_stock_row(db_name)
    return


def sell_stock(db_name):
    # Need to be careful because if a user own same company twice, 
    # Sell should show the total amount of stock
    user_profile = get_profile_table(db_name)
    new_trading = []

    # Get holding information first
    holding_info = []
    holding_info = get_holding_table(db_name)

    print "Which company do you want to sell?"
    # Get company name from a user & get the current price
    company_name = raw_input()
    current_price = get_stock_info(company_name)
    max_purchase = float(user_profile[3]) / float(current_price)
    
    current_holding = []
    current_holding = search_own_stock(holding_info, company_name, "BUYLONG")
    print "You own " + str(current_holding[0]) + " stock"
    print "How many stocks you want to sell?"

    # Get amount from a user
    trading_amount_request = raw_input()

    if int(trading_amount_request) > int(current_holding[0]):
        print "You entered greater than you owned. Try again"
        return

    if int(trading_amount_request) == int(current_holding[0]): # If sell all
        delete_whole_company(db_name, company_name, 'BUYLONG')
        # CALCULATE PROFIT
        # AND UPDATE REMAIN FUND

        new_trading.append(user_profile[0])
        new_trading.append(current_price)
        new_trading.append('SOLD')
        new_trading.append(company_name)
        new_trading.append(trading_amount_request) 

        # Update HISTORY table
        update_history_table(new_trading, db_name)
        #calculate_profit(getin_price, amount_stock, current_price, accout_type, trading_type)
        fund_after_sold = calculate_profit(current_holding[1], trading_amount_request, current_price, user_profile[2], 'BUYLONG')
        fund_after_sold = 2*(fund_after_sold) + float(user_profile[3])
        update_remain_fund(db_name, fund_after_sold, user_profile[0])
    else: # If a user sells only part
        remain_stock_amount = (int(current_holding[0]) - int(trading_amount_request))

        # Delete previous purchase because we will insert New purchase record
        delete_whole_company(db_name, company_name, 'BUYLONG')

        new_trading.append(user_profile[0])
        new_trading.append(current_holding[1])
        new_trading.append('BUYLONG')
        new_trading.append(company_name)
        new_trading.append(remain_stock_amount) 

        # Update TRADING table
        update_trading_table(new_trading, db_name)

        new_trading[1] = current_price
        new_trading[2] = 'SOLD'
        new_trading[4] = trading_amount_request

        # Update HISTORY table
        update_history_table(new_trading, db_name)

        # CALCULATE PROFIT
        # AND UPDATE REMAIN FUND
        fund_after_sold = calculate_profit(current_holding[1], trading_amount_request, current_price, user_profile[2], 'BUYLONG')
        fund_after_sold = 2*(fund_after_sold) + float(user_profile[3])
        update_remain_fund(db_name, fund_after_sold, user_profile[0])
    # Delete zero stock (garbage data) just for in case
    delete_zero_stock_row(db_name)
    return

def sell_short_stock(db_name):
    user_profile = get_profile_table(db_name)
    new_trading = []

    # Get holding information first
    holding_info = []
    holding_info = get_holding_table(db_name)

    print "Which company do you want to SELLSHORT?"
    # Get company name from a user & get the current price
    company_name = raw_input()
    current_price = get_stock_info(company_name)
    max_purchase = float(user_profile[3]) / float(current_price)
    print "Your company is %s and its price is %s" % (company_name, str(current_price))
    print "You can purchase " + str(int(max_purchase)) + " amount stocks"
    print "How many do you want to buy?"
    # Get amount from a user
    trading_amount_request = raw_input()

    if int(trading_amount_request) > int(max_purchase):
        print "You entered greater than you can afford. Try again"
        return

    current_holding = []
    current_holding = search_own_stock(holding_info, company_name, "SELLSHORT")

    if int(current_holding[0]) == 0:
        # Update TRADING table
        new_trading.append(user_profile[0])
        new_trading.append(current_price)
        new_trading.append('SELLSHORT')
        new_trading.append(company_name)
        new_trading.append(trading_amount_request)
    else:
        avg_price = (int(current_holding[0]) * float(current_holding[1])) + (float(current_price) * int(trading_amount_request))
        total_stock_amount = (int(current_holding[0]) + int(trading_amount_request))
        avg_price = avg_price / total_stock_amount

        # Delete previous purchase because we will insert New purchase record
        delete_whole_company(db_name, company_name, 'SELLSHORT')

        new_trading.append(user_profile[0])
        new_trading.append(avg_price)
        new_trading.append('SELLSHORT')
        new_trading.append(company_name)
        new_trading.append(total_stock_amount)

    # Update TRADING table
    update_trading_table(new_trading, db_name)
    # Update HISTORY table
    update_history_table(new_trading, db_name)
    # Update remain fund in PROFILE table
    update_remain_fund(db_name, float(user_profile[3]) - (float(current_price) * float(trading_amount_request)), new_trading[0])

    # Delete zero stock (garbage data) just for in case
    delete_zero_stock_row(db_name)
    return


def buy_to_cover_stock(db_name):
    # Need to be careful because if a user own same company twice, 
    # Sell should show the total amount of stock
    user_profile = get_profile_table(db_name)
    new_trading = []

    # Get holding information first
    holding_info = []
    holding_info = get_holding_table(db_name)

    print "Which company do you want to Buy to cover?"
    # Get company name from a user & get the current price
    company_name = raw_input()
    current_price = get_stock_info(company_name)
    max_purchase = float(user_profile[3]) / float(current_price)
    
    current_holding = []
    current_holding = search_own_stock(holding_info, company_name, "SELLSHORT")
    print "You own " + str(current_holding[0]) + " stock"
    print "How many stocks you want to sell?"

    # Get amount from a user
    trading_amount_request = raw_input()

    if int(trading_amount_request) > int(current_holding[0]):
        print "You entered greater than you owned. Try again"
        return

    if int(trading_amount_request) == int(current_holding[0]): # If sell all
        delete_whole_company(db_name, company_name, 'SELLSHORT')
        # CALCULATE PROFIT
        # AND UPDATE REMAIN FUND

        new_trading.append(user_profile[0])
        new_trading.append(current_price)
        new_trading.append('BUY-TO-COVER')
        new_trading.append(company_name)
        new_trading.append(trading_amount_request) 

        # Update HISTORY table
        update_history_table(new_trading, db_name)
        #calculate_profit(getin_price, amount_stock, current_price, accout_type, trading_type)
        fund_after_sold = calculate_profit(current_holding[1], trading_amount_request, current_price, user_profile[2], 'SELLSHORT')
        fund_after_sold = 2*(fund_after_sold) + float(user_profile[3])
        update_remain_fund(db_name, fund_after_sold, user_profile[0])
    else: # If a user sells only part
        remain_stock_amount = (int(current_holding[0]) - int(trading_amount_request))

        # Delete previous purchase because we will insert New purchase record
        delete_whole_company(db_name, company_name, 'SELLSHORT')

        new_trading.append(user_profile[0])
        new_trading.append(current_holding[1])
        new_trading.append('SELLSHORT')
        new_trading.append(company_name)
        new_trading.append(remain_stock_amount) 

        # Update TRADING table
        update_trading_table(new_trading, db_name)

        new_trading[1] = current_price
        new_trading[2] = 'BUY-TO-COVER'
        new_trading[4] = trading_amount_request

        # Update HISTORY table
        update_history_table(new_trading, db_name)

        # CALCULATE PROFIT
        # AND UPDATE REMAIN FUND
        fund_after_sold = calculate_profit(current_holding[1], trading_amount_request, current_price, user_profile[2], 'SELLSHORT')
        fund_after_sold = 2*(fund_after_sold) + float(user_profile[3])
        update_remain_fund(db_name, fund_after_sold, user_profile[0])
    # Delete zero stock (garbage data) just for in case
    delete_zero_stock_row(db_name)
    return


##################################################
# Get stock information (price, etc)
##################################################
##
def get_stock_price_only(company_name):

    # Grab HTML
    url = "http://finance.google.com/finance/info?client=ig&q="
    url = url + company_name
    match = urllib2.urlopen(url).read()
    price = grab_price_only(match)
    #print "Original price: $" + str(price)
    return float(price)

##
def grab_price_only(match):
    price = ''
    price_element = match.split(',')
    for xx in range (0, len(price_element)):
        if '"l" :' in price_element[xx]: # Include price info
            price = price_element[xx].split(':')[1]
            price = price.replace('"', '')
            price = price.replace(' ', '')

    return price

##
def get_stock_info(company_name):

    # Grab HTML
    url = "http://finance.google.com/finance/info?client=ig&q="
    url = url + company_name
    match = urllib2.urlopen(url).read()
    price = grab_price_only(match)
    print company_name + " stock price is: " + str(price)
    print "Original price: $" + str(price)
    print "How much do you think?"
    user_price = raw_input()
    return float(user_price)


def main():
    get_stock_info('aapl')
    return


if __name__ == '__main__':
    main()

