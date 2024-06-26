from datetime import datetime, timedelta
import time
import pymysql
import twstock
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import os

intents = discord.Intents.default() #intents 是要求的權限
intents.message_content = True
client = discord.Client(intents=intents) #client是與discord連結的橋樑
load_dotenv()

CHANNEL_ID = os.getenv("CHANNEL_ID")
BOT_API_KEY = os.getenv("BOT_API_KEY")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

def InitDatabase():
    try:
        print("InitDatabase")

        conn = pymysql.connect(
            host=DATABASE_HOST,
            user="root",
            password=DATABASE_PASSWORD,  # 密碼設置為空字符串
        )

        cursor = conn.cursor()
        cursor.execute("DROP DATABASE IF EXISTS STOCKDATABASE") # 如果資料庫存在，就刪除
        cursor.execute("CREATE Database STOCKDATABASE;") # 執行 SQL 腳本

        # 關閉游標和連接
        cursor.close()
        conn.close()

        # 嘗試重新連接
        # 連接到 pymysql 資料庫
        conn = pymysql.connect(
            host=DATABASE_HOST,  # 主機名稱，本地資料庫通常是 localhost
            user="root",  # 使用者名稱，根據你的資料庫設定
            password=DATABASE_PASSWORD,  # 密碼設置為空字符串
            database="STOCKDATABASE"  # 資料庫名稱，根據你的資料庫設定
        )

        sql_commands = [
            "CREATE DATABASE IF NOT EXISTS STOCKDATABASE;",
            "USE STOCKDATABASE;",
            """
            CREATE TABLE IF NOT EXISTS STOCK (
                stockID VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            );
            """,
            """
            INSERT INTO STOCK (stockID, name) VALUES
            ('3231', '緯創'),
            ('2330', '台積電'),
            ('2317', '鴻海'),
            ('2382', '廣達'),
            ('2376', '技嘉'),
            ('2454', '聯發科'),
            ('3661', '世芯-KY'),
            ('2603', '長榮'),
            ('3443', '創意'),
            ('2356', '英業達'),
            ('2303', '聯電'),
            ('2308', '台達電'),
            ('00632R', '元大台灣50反1'),
            ('1603', '華電');
            """,
            """
            CREATE TABLE IF NOT EXISTS MYSTOCK (
                id INT AUTO_INCREMENT PRIMARY KEY,
                stockID VARCHAR(255),
                amount INT NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                buytime VARCHAR(255),
                reason VARCHAR(255)
            );
            """,
            """
            INSERT INTO MYSTOCK (stockID, amount, price, buytime, reason) VALUES
            ('2330', 5000, 750, '0', '測試'),
            ('2308', 4750, 100, '0', '測試');
            """,
            """
            CREATE TABLE IF NOT EXISTS SELLHISTORY (
                id INT AUTO_INCREMENT PRIMARY KEY,
                stockID VARCHAR(255),
                amount INT NOT NULL,
                buyPrice DECIMAL(10, 2) NOT NULL,
                sellPrice DECIMAL(10, 2) NOT NULL,
                profit DECIMAL(10, 2) NOT NULL,
                reason VARCHAR(255)
            );
            """,
            """
            INSERT INTO SELLHISTORY (stockID, amount, buyPrice, sellPrice, profit, reason) VALUES
            ('2330', 5000, 750, 800, 2500, '測試'),
            ('2308', 4750, 100, 110, -1000, '測試');
            """,
            """
            CREATE TABLE IF NOT EXISTS MYDATA (
                name VARCHAR(255) PRIMARY KEY,
                money INT NOT NULL
            );
            """,
            """
            INSERT INTO MYDATA (name, money) VALUES
            ('Jason', 100000);
            """
        ]
        cursor = conn.cursor() # 建立 cursor 物件
        for command in sql_commands:
            cursor.execute(command)
            conn.commit()
        cursor.close() # 關閉 cursor

        return conn
    except Exception as e:
        print(e)
        return None

def CheckMyMoney(conn):
    cursor = conn.cursor() # 建立 cursor 物件
    cursor.execute("SELECT money FROM MYDATA WHERE name = 'Jason'") # 執行 SQL 查詢
    rows = cursor.fetchone() # 擷取第一筆資料
    cursor.close() # 關閉 cursor

    return rows[0] # 回傳第一筆資料的第一個欄位

def AlterMyMoney(conn, newMoney):
    cursor = conn.cursor() # 建立 cursor 物件
    cursor.execute("UPDATE MYDATA SET money = %s WHERE name = 'Jason'", (newMoney,)) # 執行 SQL 更新
    conn.commit() # 提交 SQL 更新
    cursor.close() # 關閉 cursor

def GetStockPrice(stock_id, allInfo): # 回傳今日股價
    return allInfo[stock_id]['realtime']['latest_trade_price']

def GetStockPrice_backup(stock_id): # 回傳今日股價
    stock = twstock.Stock(stock_id) # 建立 Stock 物件
    stockPrice = stock.price # 取得股價

    # 回傳最後一個欄位
    return stockPrice[-1]

def CheckStockBuyTime(conn, stock_id): # 檢查是否在過去一個禮拜內買過
    nowTime=time.time()
    cursor = conn.cursor() # 建立 cursor 物件

    cursor.execute("SELECT buytime FROM MYSTOCK WHERE stockID = %s", (stock_id,)) # 執行 SQL 查詢
    rows = cursor.fetchall() # 擷取所有的資料
    for row in rows:
        if nowTime-float(row[0]) < 604800: # 604800 秒 = 1 週
            print("過去一週買過這支股票了, 股號:", stock_id)
            return 1
    
    return 0
        

async def Buy(conn, allInfo, stock_id, reason):

    if CheckStockBuyTime(conn, stock_id) == 1: # 過去一個禮拜內買過了
        return # 暫時不買

    myMoney=CheckMyMoney(conn) # 呼叫 CheckMyMoney 函式
    stockPrice=GetStockPrice(stock_id, allInfo) # 呼叫 GetStockPrice 函式
    cursor = conn.cursor() # 建立 cursor 物件

    insertCommand = "INSERT INTO MYSTOCK (stockID, amount, price, buytime, reason) VALUES (%s, %s, %s, %s, %s)"

    nowTime=time.time()
    cursor.execute(insertCommand, (stock_id, myMoney/20, stockPrice, nowTime, reason)) # 執行 SQL 插入，每次都花 1/20 的本金購買股票
    conn.commit() # 提交 SQL 插入
    print("買入股票: ", stock_id, ", 購入股價: ", stockPrice, ", 購入總金額: ", myMoney/20, ", 購入原因: ", reason)
    channel = discord.utils.get(client.get_all_channels(), id=int(CHANNEL_ID))
    await channel.send("買入股票: "+str(stock_id)+"\n購入股價: "+str(stockPrice)+"\n購入總金額: "+str(myMoney/20)+"\n購入原因: "+str(reason)+"\n---")

    AlterMyMoney(conn, myMoney-myMoney/20) # 呼叫 AlterMyMoney 函式


    # 關閉 cursor
    cursor.close()

def REMEMBER_SELL_HISTORY(conn, stock_id, amount, buyPrice, sellPrice, profit, reason):
    cursor = conn.cursor() # 建立 cursor 物件

    insertCommand = "INSERT INTO SELLHISTORY (stockID, amount, buyPrice, sellPrice, profit, reason) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(insertCommand, (stock_id, amount, buyPrice, sellPrice, profit, reason)) # 執行 SQL 插入
    conn.commit() # 提交 SQL 插入

    cursor.close() # 關閉 cursor
    conn.close() # 關閉連線


async def Sell(conn, allInfo, stock_id, reason):
    myMoney=CheckMyMoney(conn) # 呼叫 CheckMyMoney 函式
    cursor = conn.cursor() # 建立 cursor 物件

    cursor.execute("SELECT amount, price FROM MYSTOCK WHERE stockID = %s", (stock_id,)) # 執行 SQL 查詢
    rows = cursor.fetchall() # 擷取所有的資料
    cursor.close() # 關閉 cursor

    if len(rows) == 0: # 如果查詢結果為空
        print("目前未持有此股票, 股號:", stock_id)

        return # 沒得賣

    final_profit=0
    for row in rows:
        amount=row[0]
        buyPrice=row[1]
        sellPrice=GetStockPrice(stock_id, allInfo)
        profit=(float(sellPrice)/float(buyPrice))*float(amount) - float(amount) # 計算損益
        profitRate=(float(sellPrice)/float(buyPrice))-1 # 計算損益率
        print("股號:", stock_id, ", 買入價格:", buyPrice, ", 賣出價格:", sellPrice, ", 已實現損益:", profit, ", 已實現損益率:", profitRate*100, "%", ", 賣出原因:", reason)
        channel = discord.utils.get(client.get_all_channels(), id=int(CHANNEL_ID))
        await channel.send("股號: "+str(stock_id)+"\n買入價格: "+str(buyPrice)+"\n賣出價格: "+str(sellPrice)+"\n已實現損益: "+str(profit)+"\n已實現損益率: "+str(profitRate*100)+"%\n賣出原因: "+str(reason)+"\n---")

        REMEMBER_SELL_HISTORY(conn, stock_id, amount, buyPrice, sellPrice, profit, reason)

        final_profit+=profit

    cursor = conn.cursor() # 建立 cursor 物件
    cursor.execute("DELETE FROM MYSTOCK WHERE stockID = %s", (stock_id,))
    conn.commit() # 提交 SQL 刪除
    cursor.close()

    AlterMyMoney(conn, myMoney+final_profit) # 呼叫 AlterMyMoney 函式

async def Check(conn, allInfo):
    cursor = conn.cursor() # 建立 cursor 物件
    cursor.execute("SELECT * FROM MYSTOCK") # 執行 SQL 查詢
    rows = cursor.fetchall() # 擷取所有的資料
    cursor.close() # 關閉 cursor

    for row in rows:
        try:
            stock_id=row[1]
            amount=row[2]
            buyPrice=row[3]
            reason=row[5]
            sellPrice=GetStockPrice(stock_id, allInfo)
            profit=(float(sellPrice)/float(buyPrice))*float(amount) - float(amount) # 計算損益
            profitRate=(float(sellPrice)/float(buyPrice))-1 # 計算損益率
            print("股號:", stock_id, ", 買入價格:", buyPrice, ", 當前價格:", sellPrice, ", 購買的總金額數:", amount, ", 未實現損益:", profit, ", 未實現損益率:", profitRate*100, "%", ", 購入原因:", reason)
            channel = discord.utils.get(client.get_all_channels(), id=int(CHANNEL_ID))
            await channel.send("股號: "+str(stock_id)+"\n買入價格: "+str(buyPrice)+"\n當前價格: "+str(sellPrice)+"\n購買的總金額數: "+str(amount)+"\n未實現損益: "+str(profit)+"\n未實現損益率: "+str(profitRate*100)+"%\n購入原因: "+str(reason)+"\n---")

        except Exception as e:
            print(e)

    # 從 SELLHISTORY 取得歷史總損益
    cursor = conn.cursor() # 建立 cursor 物件
    cursor.execute("SELECT profit FROM SELLHISTORY") # 執行 SQL 查詢
    rows = cursor.fetchall() # 擷取所有的資料
    
    # 計算總損益
    total_profit=0
    for row in rows:
        total_profit+=row[0]
    
    print("歷史總損益:", total_profit)
    channel = discord.utils.get(client.get_all_channels(), id=int(CHANNEL_ID))
    await channel.send("---\n歷史總損益: "+str(total_profit)+"\n---")


def RealTime_GET(conn):
    cursor = conn.cursor() # 建立 cursor 物件
    cursor.execute("SELECT stockID FROM STOCK") # 執行 SQL 查詢
    rows = cursor.fetchall() # 擷取所有的資料

    stockID_list = []
    for row in rows:
        stockID_list.append(row[0])
    
    return twstock.realtime.get(stockID_list)

@tasks.loop(seconds=1.0) #每60秒執行一次
async def Time_Check(conn):
    # 如果現在時間不是 14:00 整，就不執行
    # 獲取當前UTC時間
    utc_now = datetime.utcnow()
    # 計算台灣時區時間（UTC+8）
    taiwan_time = utc_now + timedelta(hours=8)
    if taiwan_time.time().hour != 14 or taiwan_time.time().minute != 0:
        return

    while True:
        flag=0
        try:
            ############################################################ 短線交易邏輯 ############################################################
            allInfo=RealTime_GET(conn)
            print(allInfo)

            cursor = conn.cursor() # 建立 cursor 物件
            cursor.execute("SELECT * FROM STOCK") # 執行 SQL 查詢
            rows = cursor.fetchall() # 擷取所有的資料
            for row in rows: # 賣出股票
                try:
                    stock = twstock.Stock(str(row[0])) # 建立 Stock 物件
                    bfp = twstock.BestFourPoint(stock) # 建立 BestFourPoint 物件
                    result, reason = bfp.best_four_point() # 取得最佳四大買賣點 (以上次收盤時的資料為準)
                    if not result and reason.count(',')>=1: # 如果符合最佳四大買賣點，且有兩個以上的理由
                        await Sell(conn, allInfo, row[0], reason) # 呼叫 Sell 函式
                        print("\n")

                except Exception as e:
                    print(e)

            for row in rows: # 買進股票
                try:
                    stock = twstock.Stock(str(row[0])) # 建立 Stock 物件
                    bfp = twstock.BestFourPoint(stock) # 建立 BestFourPoint 物件
                    result, reason = bfp.best_four_point() # 取得最佳四大買賣點 (以上次收盤時的資料為準)
                    if result and reason.count(',')>=1: # 如果符合最佳四大買賣點
                        await Buy(conn, allInfo, row[0], reason) # 呼叫 Buy 函式
                        print("\n")

                except Exception as e:
                    print(e)

            # 確認當前持股資料
            await Check(conn, allInfo)

            # 關閉 cursor 和連線
            cursor.close()
            ############################################################ 短線交易邏輯 ############################################################
        except:
            flag+=1

        if flag==0:
            break

@client.event
async def on_ready(): #啟動成功時會呼叫
    channel = discord.utils.get(client.get_all_channels(), id=int(CHANNEL_ID))
    await channel.send("啟動")
    time.sleep(10) # 等待 database 準備好
    while True:
        conn=InitDatabase()
        if conn != None:
            break

    Time_Check.start(conn) #每60秒在背景執行Time_Check函式

client.run(BOT_API_KEY) #啟動bot