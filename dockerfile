# 使用 Python 3.8 作為基礎映像
FROM python:3.11.3-slim

# 設置工作目錄
WORKDIR /app

# 從本地目錄複製應用程式程式碼到容器中的 /app 目錄
COPY . /app

# 安裝所需的 Python 庫
RUN pip install --no-cache-dir -r requirements.txt

# 安裝 MySQL 客戶端
RUN apt-get update && apt-get install -y default-mysql-client

# 定義容器啟動時運行的命令
CMD ["sh", "-c", "python main.py"]
