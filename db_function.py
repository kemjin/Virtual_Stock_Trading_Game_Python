# Project Jiminel (Virtual Stock market game)
# core engine: getting a stock price from google finance

# DB Degisn
#
# USER_INFO Table
# TRADING table
# HISTORY Table

import urllib2, sys, time, os, re
import sqlite3, os.path
from datetime import datetime

##
def initial_db_setup(db_name):
    user_id = 'jiminel'
    #db_name = user_id + '_data.db'

    # Check db is exist or not
    if (os.path.exists(db_name)):
        print "DB already exist"
        os.remove(db_name)
    else:
        print "No database found"
    db = sqlite3.connect(db_name)

    # This is creating a table
    db.execute('''CREATE TABLE PROFILE
             (USERNAME          TEXT NOT NULL,
             ORIG_FUND          REAL NOT NULL,
             TRADING_TYPE       TEXT NOT NULL,
             CASH               REAL NOT NULL
             );''')

    # This is creating a table
    db.execute('''CREATE TABLE TRADING
             (USERNAME          TEXT NOT NULL,
             GETIN_PRICE        REAL NOT NULL,
             TRADING_TYPE       TEXT NOT NULL,
             COMPANY_NAME       TEXT NOT NULL,
             AMOUNT_STOCK        INT NOT NULL);''')

    # This is creating a table
    db.execute('''CREATE TABLE HISTORY
             (USERNAME          TEXT NOT NULL,
             GETIN_PRICE        REAL NOT NULL,
             TRADING_TYPE       TEXT NOT NULL,
             COMPANY_NAME       TEXT NOT NULL,
             AMOUNT_STOCK        INT NOT NULL,
             DATE_TIME          TEXT NOT NULL);''')

    db.close()
    # Insert INITIAL values
    insert_value(db_name, user_id)

    print ("Reset Database is done")
    return

##
def insert_value(db_name, user_id):

    db = sqlite3.connect(db_name)
    # This is inserting data into a table
    # We assume that the account is for MARGIN account
    db.execute("INSERT INTO PROFILE (USERNAME, ORIG_FUND, TRADING_TYPE, CASH) VALUES (?, 100000.00, 'MARGIN', 200000.00 )", [user_id])

    #db.execute("INSERT INTO TRADING (USERNAME, GETIN_PRICE, TRADING_TYPE, COMPANY_NAME, AMOUNT_STOCK) \
    #VALUES (?, 'Allen', 25, 'Texas', 15000.00 )", user_id)

    db.commit()
    return

##
def print_tables(db_name):

    db = sqlite3.connect(db_name)

    print ("User Profile Information")
    profile_table = db.execute("SELECT * from PROFILE")
    for row in profile_table:
        #print "USERNAME: = ", row[0]
        #print "Original Fund = ", row[1]
        print "Trading Type = ", row[2]
        print "Available Purchase = ", row[3], "\n"

    print ("Trading / Holding Information")
    
    trading_table = db.execute("SELECT * from TRADING")
    for row in trading_table:
        #print "USERNAME: = ", row[0]
        print "Get in Price = ", row[1]
        print "Trading Type = ", row[2]
        print "Company name = ", row[3]
        print "Amount of stock = ", row[4], "\n"
    return

##
def print_history_tables(db_name):

    db = sqlite3.connect(db_name)

    print ("Trading / Holding History")
    
    trading_table = db.execute("SELECT * from HISTORY")
    for row in trading_table:
        #print "USERNAME: = ", row[0]
        print "Get in Price = ", row[1]
        print "Trading Type = ", row[2]
        print "Company name = ", row[3]
        print "Amount of stock = ", row[4]
        print "Date : ", row[5], "\n"
    return    

##
# Add BUY / SELLSHORT Record
def update_trading_table(new_trading, db_name):

    db = sqlite3.connect(db_name)
    db.execute("INSERT INTO TRADING (USERNAME, GETIN_PRICE, TRADING_TYPE, COMPANY_NAME, AMOUNT_STOCK) VALUES (?, ?, ?, ?, ?)", new_trading)
    db.commit()
    db.close()
    #print "Update is done"
    return

##
# Add trading history to HISTORY table
def update_history_table(new_trading, db_name):

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    new_trading.append(str(current_time))

    db = sqlite3.connect(db_name)
    db.execute("INSERT INTO HISTORY (USERNAME, GETIN_PRICE, TRADING_TYPE, COMPANY_NAME, AMOUNT_STOCK, DATE_TIME) VALUES (?, ?, ?, ?, ?, ?)", new_trading)
    db.commit()
    db.close()
    #print "Update is done"
    return

##
# Update Remain Fund Record
def update_remain_fund(db_name, remain_fund, user_id):

    db = sqlite3.connect(db_name)
    db.execute("UPDATE PROFILE SET CASH=? WHERE USERNAME=?", (float(remain_fund), user_id))
    db.commit()
    #db.execute("UPDATE PROFILE SET CASH=? WHERE USERNAME=?", (float(available_purchase), user_id))
    #db.commit()
    db.close()
    return

##
def delete_zero_stock_row(db_name):

    db = sqlite3.connect(db_name)
    db.execute("DELETE from TRADING WHERE AMOUNT_STOCK=0")
    db.commit()
    db.close()

    return

## Getting profile table info
def get_profile_table(db_name):

    db = sqlite3.connect(db_name)
    user_profile = []

    cursor = db.execute("SELECT * from PROFILE")
    for row in cursor:
        user_profile.append(row[0])
        user_profile.append(row[1])
        user_profile.append(row[2])
        user_profile.append(row[3])

    return user_profile

## Getting TRADING table ifo
def get_holding_table(db_name):

    db = sqlite3.connect(db_name)
    holding_information = []

    cursor = db.execute("SELECT * from TRADING")
    for row in cursor:
        holding_information.append(row)

    return holding_information


## Reset HISTORY Table
def reset_history_table(db_name):

    db = sqlite3.connect(db_name)

    db.execute("DELETE FROM HISTORY")
    db.commit()

    # This is creating a table
    db.execute('''CREATE TABLE HISTORY
             (USERNAME          TEXT NOT NULL,
             DATE               TEXT NOT NULL,
             COMPANY_NAME       TEXT NOT NULL,
             AMOUNT_STOCK        INT NOT NULL,
             GETIN_PRICE        REAL NOT NULL,
             TRADING_TYPE       TEXT NOT NULL);''')

    db.commit()
    db.close()
    print "Reset HISTORY table is done"
    return



def update_profile_table(new_trading, db_name):

    db = sqlite3.connect(db_name)

    db.execute("DELETE FROM PROFILE")
    db.commit()

    db.execute("INSERT INTO PROFILE (USERNAME, ORIG_FUND, TRADING_TYPE, CASH) VALUES (?, ?, ?, ?)", new_trading)
    db.commit()
    db.close()
    print "Update is done"
    return




### DELETE IF update_amount_stock function works fine w/ buy and sell
def update_remain_stock(db_name, company_name, amount_of_stock, holding_info):
    db = sqlite3.connect(db_name)
    remain_amount = int(holding_info[4]) - int(amount_of_stock)
    if remain_amount == 0:
        db.execute("DELETE FROM TRADING WHERE COMPANY_NAME=? AND TRADING_TYPE=? AND AMOUNT_STOCK=?", (company_name, holding_info[2], int(holding_info[4])))
    else:
        db.execute("UPDATE TRADING SET AMOUNT_STOCK=? WHERE COMPANY_NAME=? AND TRADING_TYPE=? AND AMOUNT_STOCK=?", (remain_amount, company_name, holding_info[2], int(holding_info[4])))
    db.commit()
    db.close()

    return

## Delete after sell or buy-to-cover all
def delete_whole_company(db_name, company_name, trading_type):

    db = sqlite3.connect(db_name)
    db.execute("DELETE from TRADING WHERE COMPANY_NAME=? AND TRADING_TYPE=?", (company_name, trading_type))
    db.commit()
    db.close()
    return



def delete_trading_row(db_name, company_name, amount_of_stock, holding_info):

    db = sqlite3.connect(db_name)
    db.execute("DELETE from TRADING WHERE COMPANY_NAME=? AND TRADING_TYPE=? AND AMOUNT_STOCK=?", (company_name, holding_info[2], int(holding_info[4])))
    db.commit()
    db.close()
    return


def update_amount_stock(db_name, company_name, new_amount, trading_type, original_amount):

    db = sqlite3.connect(db_name)
    #remain_amount = int(holding_info[4]) - int(amount_of_stock)
    db.execute("UPDATE TRADING SET AMOUNT_STOCK=? WHERE COMPANY_NAME=? AND TRADING_TYPE=? AND AMOUNT_STOCK=?", (new_amount, company_name, trading_type, original_amount))
    db.commit()
    db.close()
    return



def main():
    insert_value('newboxster_data.db', 'newboxster')
    return


if __name__ == '__main__':
    main()

