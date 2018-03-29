import requests
from bs4 import BeautifulSoup as bs
import re
import time
import random
from pymongo import MongoClient
from pprint import pprint
from pymongo import ReturnDocument
from bson.objectid import ObjectId
from pymongo import ASCENDING, DESCENDING

class MongoDBManage:
    def __init__(self):
        self.client = MongoClient("localhost",27017)
        self.db = self.client["mongodatabase_stock"]
        self.Taiwan_stock = self.db["stock_info"]

    def insert_one_info(self,data):
        self.Taiwan_stock.insert_one(data)
    
    def insert_many_info(self,data):
        self.Taiwan_stock.insert_many(data)
    
    def remove_document(self,data):
        self.Taiwan_stock.delete_many(data)
    
    def update_stock_info(self,org_data,updatedata):
        self.Taiwan_stock.update_one(org_data,{"$set":updatedata},upsert = False)
    
    def find_Tstock(self,data):
        find_stock = self.Taiwan_stock.find(data)
        for eachstock in find_stock:
            pprint(eachstock)
    
    def delete_stock(self,data):
        #刪除document
        self.Taiwan_stock.delete_one(data)
    
    def drop_collection(self,collection):
        #刪除整個資料庫
        self.Taiwan_stock.drop()
    
    def create_stock_index(self):
        #建立索引標籤
        self.Taiwan_stock.create_index([("stock_order", ASCENDING)], unique = True)
        db_sorted= sorted(list(self.Taiwan_stock.index_information()))
        print(db_sorted)

def scrapy_price(stock_token):
    head = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"}
    url = "https://goodinfo.tw/StockInfo/StockDividendPolicy.asp?STOCK_ID="+ stock_token
    html = requests.get(url,headers=head)
    html = html.text
    tds = []
    bs_stock = bs(html, "html.parser")
    table_price = bs_stock.findAll("table",{"class":"std_tbl"})
    for table in table_price:
        rows = table.findAll('tr')
        name = table.findAll("",{"class":"link_blue"})
        ID = name[0].get_text().encode("utf-8")
        id = ID[0:4].decode("utf-8")
        name_stock = name[0].get_text()[5:].encode('latin1').decode('utf-8')
        for row in rows:
            tds.append(row.findAll("td"))
    stock_infomation = []
    stock_infomation.append(name_stock)
    stock_infomation.append(str(id))
    stock_infomation.append(str(tds[2][0].get_text().encode('latin1').decode('utf-8')))
    return stock_infomation


def data_dict():
    stock_insert = {}
    stock_insert["stockID"] = todayinfo[1]
    stock_insert["enterprise"] = todayinfo[0]
    stock_insert["price"] = todayinfo[2]
    stock_insert["time"] = time.strftime("%Y-%m-%d", time.localtime())
    return stock_insert


stockID = str(input("輸入台股代碼"))
todayinfo = scrapy_price(stockID)

#加入mongo資料庫
if __name__ == "__main__":
    mongodb = MongoDBManage()
    if str(type(mongodb.Taiwan_stock.find_one({"stockID":todayinfo[1]}))) == "<class 'dict'>":
        print(todayinfo[0],"已經有了,update股價",todayinfo[2],sep="")
        mongodb.update_stock_info({"stockID":str(todayinfo[1])},data_dict())
    else:
        print("幫你加上",todayinfo[0], todayinfo[2],sep="")
        mongodb.insert_one_info(data_dict())
    print("您已經關注",mongodb.Taiwan_stock.count(),"檔股票囉!") #計算幾筆資料


# 
