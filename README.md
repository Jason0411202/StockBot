# StockBot
## 部署
### 準備好 .env 檔案
```shell
CHANNEL_ID=discord 機器人傳送訊息的 discord 頻道 id
BOT_API_KEY= discord 機器人的 api key
DATABASE_HOST= 資料庫的 host 名稱
DATABASE_PASSWORD= 資料庫的密碼
```

### 準備好 docker-compose.yml 檔案
linux 版
```yaml
# 使用 3.3 版本的 docker-compose
version: '3.3'

# 定義服務，共有兩個服務，分別是 mysql_database 和 stockbot_short
services:
  mysql_database: # mysql_database 服務
    image: mariadb:10.5  # 指定這個服務要使用的 image，為 mariadb:10.5 映像檔
    container_name: ${DATABASE_HOST}  # 指定這個服務的 container name (很重要，會關係到前端如何連接後端)
    environment: # 指定這個服務要使用的環境變數，這裡設定了 MYSQL_ROOT 的密碼
      MYSQL_ROOT_PASSWORD: ${DATABASE_PASSWORD}
    networks: # 指定這個服務要使用的 network
      - "my_network"
    restart: always  # 當服務停止時，自動重啟服務
  stockbot_short: # stockbot_short 服務
    image: jason0411202/stockbot-short-linux  # 指定這個服務要使用的 image
    depends_on: # 指定這個服務依賴於哪些服務，mysql_database 服務啟動後才啟動 stockbot_short 服務
      - mysql_database        # 指定 stockbot_short 服務依賴於 backend 服務，這樣能保證 stockbot_short 在 backend 服務啟動後才啟動
    networks: # 指定這個服務要使用的 network
      - "my_network"
    env_file: # 將這個服務要使用的環境變數檔案傳給該容器
      - .env
    restart: always  # 當服務停止時，自動重啟服務

networks:  # 定義 networks，目的是為了使容器之間可以互相連接
  my_network:  # 定義一個名為 my_network 的 network
    driver: bridge  # 使用 bridge network，功能是讓不同服務可以互相連接
```

## 執行指令
```shell
docker-compose up -d
```

## database schema
### STOCK (追蹤的股票)
stockID name

股票 id, 股票名稱

### MYSTOCK (目前持有的股票紀錄)
id stockID amount price, buytime, reason

獨一無二的 id, 股票 id, 購買的總金額數, 購買的單股價格, 購買的時間, 購買的原因

### MYDATA (使用者資料)
name, money

使用者名稱, 使用者目前擁有的金額

### SELLHISTORY (已實現損益)
stockID, amount, buyPrice, sellPrice, profit, reason

股票 id, 賣出的數量, 購買的單股價格, 賣出的單股價格, 損益, 賣出的原因

## 交易邏輯
### 短線
* 主攻個股交易
* 每次購入金額為當前銀行帳戶餘額之 1/20
* 決定買入的股票，一個禮拜之內不再買 (賣出後刷新時間)
* 可能會分批買，但會一次全賣
* 根據 twstock 的四大買賣點進行選股篩選

### 長線 (移至另一個專案)
* 主攻 ETF 交易
* 市值型 (006208) 與配息型(0056, 00878, 00919, 00929) ETF 計數器分開計算
* 基本買賣邏輯:
  * 當股價來到一個月內最低點時固定買入 5000，操作後一個月內不再進行任何關於該型的買賣操作
  * 當股價來到三個月內最高點時固定賣出 5000，操作後一個月內不再進行任何關於該型的買賣操作
* 加減碼邏輯:
  * 當買入時，價格位於 180 日平均股價之上，少買 2000
  * 當買入時，價格位於 180 日平均股價之下，多買 3000
  * 當買入時，價格位於 360 日平均股價之下，再多買 2000
  * 當賣出時，價格位於 180 日平均股價之下，少賣 2000

## 待做
1. Sell 邏輯 (complete)
2. 已實現損益資料庫 (complete)
3. 長線交易邏輯 (移至另一個專案)
4. 連動 discord (complete)
5. 環境變數 (complete)
6. docker (complete)