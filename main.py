# Project Jiminel (Virtual Stock market game)
# core engine: getting a stock price from google finance
# Author: Jin Wook Kim (2/20/2016)
# License: MIT license

# Need to see conclusion so far (Current status / How much profit / Total this Month)
# Modify DB menu

import urllib2, sys, time, os, re
import sqlite3
from common_lib import *

db_name = 'jiminel_data.db'


def call_menu():

    # Print Menu
    print """

*************************************
PROJECT Jiminel: Virtual Stock game
*************************************
* 1. View your info
* 2. Check stock price
*
* 3. Trading: Buy
* 4. Trading: Sell
* 5. Trainng: Sell Short
* 6. Trading: Buy to Cover
*
* 7. Your Performance
* 8. Performance Summary (Total)
* 9. DB menu
* 10. Get your full History
*
* 0. Menu
* If you want to quit, press 'q'
*********************************
"""
    return


def db_menu():
    # Print Menu
    print """
*********************************
* DB Menu
*
* 1. Reset DB
* 2. Modify Current FUND
*
* If you want to quit, press 'q'
*********************************

Select the number:

"""
    get_db_menu_choice()
    return

def get_db_menu_choice():
    user_input = raw_input()
    if user_input == '1': #
        initial_db_setup(db_name)

    elif user_input == '2':
        print "Which company do you want to check?"
        company_name = raw_input()
        price = get_stock_price_only(company_name)
        print price

    elif user_input == '3':
        trading(db_name, "BUY")

    elif user_input == '4':
        trading(db_name, "SELL")

    elif user_input == 'q':
        pass
    else:
        print "I am sorry. I didn't get your input"
        print "Try again, please"
    return


def get_user_choice():
    user_input = raw_input()
    if user_input == '1': # DONE
        print_tables(db_name)

    elif user_input == '2': # DONE
        print "Which company do you want to check?"
        company_name = raw_input()
        price = get_stock_price_only(company_name)
        print price

    elif user_input == '3': # DONE
        buy_stock(db_name)

    elif user_input == '4': # DONE
        sell_stock(db_name)

    elif user_input == '5': # DONE
        sell_short_stock(db_name)

    elif user_input == '6': # DONE
        buy_to_cover_stock(db_name)

    elif user_input == '7':
        portfolio_status(db_name)

    elif user_input == '8':
        total_profit(db_name)

    elif user_input == '9': # WORKING ON IT (NEED TO ADD MORE)
        db_menu()

    elif user_input == '10': # DONE
        print_history_tables(db_name)

    elif user_input == '0': # DONE
        call_menu()

    elif user_input == 'q':
        exit()
    else:
        print "I am sorry. I didn't get your input"
        print "Try again, please"
    return


def main():
    global db_name
    db_name = 'jiminel_data.db'


    call_menu()
    while True:
        print "\nSelect your menu number:"
        get_user_choice()        

    return


if __name__ == '__main__':
    main()


####################################################
# DB Design
####################################################

# USER_INFO
# USERNAME - TEXT
# ORIG_FUND - REAL (How much do you have)
# TRADING_TYPE - TEXT (CASH or MARGIN account)
# TOTAL_FUND - REAL (Current available fund amount that can purchase stocks)

# TRADING 
# USERNAME - TEXT (For Unique key)
# GETIN_PRICE - (How much did you get in)
# TRADING_TYPE - (BUYLONG OR SELLSHORT)
# COMPANY_NAME - (Which Company)
# AMOUNT_STOCK - (How many stocks do you have)

# HISTORY
# USERNAME - Unique key
# GETIN_PRICE
# TRADING_TYPE
# COMPNAY_NAME
# AMOUNT_STOCK
# DATE_TIME

