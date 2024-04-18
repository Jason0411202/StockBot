CREATE Database STOCKDATABASE;
USE STOCKDATABASE;

CREATE TABLE STOCK (
    stockID VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
INSERT INTO STOCK (stockID, name)
VALUES
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

CREATE TABLE MYSTOCK (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stockID VARCHAR(255),
    amount INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    buytime VARCHAR(255),
    reason VARCHAR(255)
);
INSERT INTO MYSTOCK (stockID, amount, price, buytime, reason)
VALUES
('2330', '5000', '750', '0', '測試'),
('2308', '4750', '100', '0', '測試');

CREATE TABLE MYDATA (
    name VARCHAR(255) PRIMARY KEY,
    money INT NOT NULL
);
INSERT INTO MYDATA (name, money)
VALUES
('Jason', '100000');

DROP Database STOCKDATABASE;


