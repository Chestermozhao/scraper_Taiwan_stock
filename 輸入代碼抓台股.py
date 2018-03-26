import requests
from bs4 import BeautifulSoup as bs
import re
import xlwt
import xlrd
import time
import random
from xlutils.copy import copy

def scrapy_price(stock_token):
    N = str(stock_token)
    head = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"}
    url = "https://goodinfo.tw/StockInfo/StockDividendPolicy.asp?STOCK_ID="+N
    html = requests.get(url,headers=head)
    html = html.text
    tds = []
    bs_stock = bs(html, "html.parser")
    table_price = bs_stock.findAll("table",{"class":"std_tbl"})
    for table in table_price:
        rows = table.findAll('tr')
        for row in rows:
            tds.append(row.findAll("td"))
    price_stock = str(tds[2][0].get_text())   
    global price_lis
    price_lis.append(price_stock)
    print(price_stock)

def get_token():
    global token
    token =[]
    stock_list = xlrd.open_workbook('真正的股票照表操作.xlsx')
    table = stock_list.sheets()[0]  
    nrows = table.nrows
    ncols = table.ncols
    for i in range(ncols):
        if table.col_values(i)[0] == "代號":
            for j in range(1,nrows):
                token.append(table.col_values(i)[j])
    for i in range(len(token)):
        token[i] = int(token[i])
    print(token)

def append_excel(path_name):
    book = xlrd.open_workbook(path_name)
    w_file = copy(book)  #複製內存檔案
    w_sheet = w_file.get_sheet('股票') #指定sheet
    w_sheet.write(0,6, time.ctime())
    for i in range(len(price_lis)):
        w_sheet.write(i+1, 6, price_lis[i])  # 在第10行第2列添加新数据'每日股價'
    w_file.save(path_name)


get_token()
price_lis = []
for j in range(len(token)):
##    try:
    scrapy_price(token[j])
    time.sleep(random.randint(10,25))
append_excel("抓股價.xls")
##    except:
##        print("沒抓到")

