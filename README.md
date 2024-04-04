# StockBot
## database schema
### STOCK (追蹤的股票)
stockID name

股票 id, 股票名稱

### MYSTOCK (目前持有的股票紀錄)
id stockID amount price

獨一無二的 id, 股票 id, 購買的總金額數, 購買的單股價格

### MYDATA (使用者資料)
name, money

使用者名稱, 使用者目前擁有的金額

## 待做
1. 每日最多只購買 3 支股票 (買點股票中, RSI 前三低的)
2. Sell 邏輯
3. 連動 discord
4. 環境變數
5. docker