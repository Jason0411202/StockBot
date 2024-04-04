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

def Buy(conn, stock_id):

    myMoney=CheckMyMoney(conn) # 呼叫 CheckMyMoney 函式
    stockPrice=GetStockPrice(stock_id) # 呼叫 GetStockPrice 函式
    cursor = conn.cursor() # 建立 cursor 物件

    insertCommand = "INSERT INTO MYSTOCK (stockID, amount, price) VALUES (%s, %s, %s)"
    cursor.execute(insertCommand, (stock_id, myMoney/20, stockPrice)) # 執行 SQL 插入
    conn.commit() # 提交 SQL 插入
    print(insertCommand, (stock_id, myMoney/20, stockPrice)) # 輸出 SQL 插入指令

    AlterMyMoney(conn, myMoney-myMoney/20) # 呼叫 AlterMyMoney 函式


    # 關閉 cursor
    cursor.close()

def BuyProcess(conn):
    print("BuyProcess")

    #CheckMyMoney(conn) # 呼叫 CheckMyMoney 函式

    cursor = conn.cursor() # 建立 cursor 物件
    cursor.execute("SELECT * FROM STOCK") # 執行 SQL 查詢
    rows = cursor.fetchall() # 擷取所有的資料
    for row in rows:
        try:
            stock = twstock.Stock(str(row[0])) # 建立 Stock 物件
            bfp = twstock.BestFourPoint(stock) # 建立 BestFourPoint 物件
            result, reason = bfp.best_four_point() # 取得最佳四大買點
            if result:
                Buy(conn, row[0])
            print(row[0], result, reason, '\n') # 輸出股票代號、是否符合最佳四大買點、原因

        except Exception as e:
            print(e)

    # 關閉 cursor 和連線
    cursor.close()
    conn.close()

conn=ConnectToDatabase() # 呼叫 ConnectToDatabase 函式
BuyProcess(conn) # 呼叫 Buy 函式