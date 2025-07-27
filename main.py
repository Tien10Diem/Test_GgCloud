# collect_data.py
import pandas as pd
import requests
import time
from datetime import datetime
import upload_DR  # 👈 Gọi trực tiếp sau khi collect xong

OUTPUT_FILE = "crypto_full_data.csv"
df_ids = pd.read_csv("500_coins.csv")
coin_ids = df_ids["id"].tolist()

now = datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M:%S")
all_data = []

for i in range(0, len(coin_ids), 100):
    batch = coin_ids[i:i+100]
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ",".join(batch),
        "sparkline": False,
        "price_change_percentage": "24h"
    }
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Lỗi ở batch {i//100+1}: {e}")
        continue

    data = r.json()
    for coin in data:
        all_data.append({
            "id": coin.get("id"),
            "name": coin.get("name"),
            "symbol": coin.get("symbol"),
            "current_price_usd": coin.get("current_price"),
            "market_cap": coin.get("market_cap"),
            "market_cap_rank": coin.get("market_cap_rank"),
            "price_change_24h": coin.get("price_change_percentage_24h"),
            "total_volume": coin.get("total_volume"),
            "circulating_supply": coin.get("circulating_supply"),
            "total_supply": coin.get("total_supply"),
            "image": coin.get("image"),
            "time_collected": now_str
        })

    time.sleep(1.2)

df = pd.DataFrame(all_data)
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
print(f"✅ Đã lưu file: {OUTPUT_FILE}")

# === UPLOAD FILE LÊN GOOGLE DRIVE ===
upload_DR.upload_to_drive()

print("✅ Đã upload lên Google Drive")
