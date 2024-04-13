import time
import mysql.connector
import twstock

def ConnectToDatabase():
    print("ConnectToDatabase")

    # 連接到 MySQL 資料庫
    conn = mysql.connector.connect(
        host="localhost",  # 主機名稱，本地資料庫通常是 localhost
        user="root",  # 使用者名稱，根據你的資料庫設定
        password="Jason910904",  # 密碼，根據你的資料庫設定
        database="STOCKDATABASE"  # 資料庫名稱，根據你的資料庫設定
    )

    if(conn.is_connected()):
        print("Connect to STOCKDATABASE success")
        return conn
    else:
        print("Connect to STOCKDATABASE failed")
        exit()

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

def GetStockPrice(stock_id): # 回傳今日股價
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
        

def Buy(conn, stock_id, reason):

    if CheckStockBuyTime(conn, stock_id) == 1: # 過去一個禮拜內買過了
        return # 暫時不買

    myMoney=CheckMyMoney(conn) # 呼叫 CheckMyMoney 函式
    stockPrice=GetStockPrice(stock_id) # 呼叫 GetStockPrice 函式
    cursor = conn.cursor() # 建立 cursor 物件

    insertCommand = "INSERT INTO MYSTOCK (stockID, amount, price, buytime, reason) VALUES (%s, %s, %s, %s, %s)"

    nowTime=time.time()
    cursor.execute(insertCommand, (stock_id, myMoney/20, stockPrice, nowTime, reason)) # 執行 SQL 插入，每次都花 1/20 的本金購買股票
    conn.commit() # 提交 SQL 插入
    print("買入股票: ", stock_id, ", 購入股價: ", stockPrice, ", 購入總金額: ", myMoney/20, ", 購入原因: ", reason)

    AlterMyMoney(conn, myMoney-myMoney/20) # 呼叫 AlterMyMoney 函式


    # 關閉 cursor
    cursor.close()

def Sell(conn, stock_id, reason):
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
        sellPrice=GetStockPrice(stock_id)
        profit=(float(sellPrice)/float(buyPrice))*float(amount) - float(amount) # 計算損益
        profitRate=(float(sellPrice)/float(buyPrice))-1 # 計算損益率
        print("股號:", stock_id, ", 買入價格:", buyPrice, ", 賣出價格:", sellPrice, ", 已實現損益:", profit, ", 已實現損益率:", profitRate*100, "%", ", 賣出原因:", reason)

        final_profit+=profit

    cursor = conn.cursor() # 建立 cursor 物件
    cursor.execute("DELETE FROM MYSTOCK WHERE stockID = %s", (stock_id,))
    conn.commit() # 提交 SQL 刪除
    cursor.close()

    AlterMyMoney(conn, myMoney+final_profit) # 呼叫 AlterMyMoney 函式

def Check(conn):
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
            sellPrice=GetStockPrice(stock_id)
            profit=(float(sellPrice)/float(buyPrice))*float(amount) - float(amount) # 計算損益
            profitRate=(float(sellPrice)/float(buyPrice))-1 # 計算損益率
            print("股號:", stock_id, ", 買入價格:", buyPrice, ", 當前價格:", sellPrice, ", 購買的總金額數:", amount, ", 未實現損益:", profit, ", 未實現損益率:", profitRate*100, "%", ", 購入原因:", reason)
        except Exception as e:
            print(e)

def MainProcess(conn):
    cursor = conn.cursor() # 建立 cursor 物件
    cursor.execute("SELECT * FROM STOCK") # 執行 SQL 查詢
    rows = cursor.fetchall() # 擷取所有的資料
    for row in rows: # 賣出股票
        try:
            stock = twstock.Stock(str(row[0])) # 建立 Stock 物件
            bfp = twstock.BestFourPoint(stock) # 建立 BestFourPoint 物件
            result, reason = bfp.best_four_point() # 取得最佳四大買點
            if not result: # 如果符合最佳四大買點
                #print(row[0], result, reason) # 輸出股票代號、是否符合最佳四大買點、原因
                Sell(conn, row[0], reason) # 呼叫 Sell 函式
                print("\n")

        except Exception as e:
            print(e)

    for row in rows: # 買進股票
        try:
            stock = twstock.Stock(str(row[0])) # 建立 Stock 物件
            bfp = twstock.BestFourPoint(stock) # 建立 BestFourPoint 物件
            result, reason = bfp.best_four_point() # 取得最佳四大買點
            if result: # 如果符合最佳四大買點
                #print(row[0], result, reason) # 輸出股票代號、是否符合最佳四大買點、原因
                Buy(conn, row[0], reason) # 呼叫 Buy 函式
                print("\n")

        except Exception as e:
            print(e)

    # 確認當前持股資料
    Check(conn)

    # 關閉 cursor 和連線
    cursor.close()
    conn.close()

conn=ConnectToDatabase() # 呼叫 ConnectToDatabase 函式
MainProcess(conn) # 呼叫主程式