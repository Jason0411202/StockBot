import twstock

# ('3231', '緯創'),
# ('2330', '台積電'),
# ('2317', '鴻海'),
# ('2382', '廣達'),
# ('2376', '技嘉'),
# ('2454', '聯發科'),
# ('3661', '世芯-KY'),
# ('2603', '長榮'),
# ('3443', '創意'),
# ('2356', '英業達'),
# ('2303', '聯電'),
# ('2308', '台達電'),
# ('00632R', '元大台灣50反1'),
# ('1603', '華電');

temp = twstock.realtime.get(['3231', '2330', '2317', '2382', '2376', '2454', '3661', '2603', '3443', '2356', '2303', '2308', '00632R', '1603'])
print(temp)