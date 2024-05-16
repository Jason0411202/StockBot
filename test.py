import pandas as pd
import requests

# 定義網址
url = "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY?date=20240401&stockNo=0050&response=csv"

# 發送 GET 請求並取得回應
response = requests.get(url)

# 如果回應是成功的 (HTTP 狀態碼為 200)
if response.status_code == 200:
    # 使用 pandas 的 read_csv 函數讀取 CSV 檔案
    df = pd.read_csv(url, encoding="big5")
    
    print(df)
else:
    # 如果回應不是成功的，印出錯誤訊息
    print("無法取得資料。")
