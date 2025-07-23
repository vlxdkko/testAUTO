import pandas as pd
import requests
import os
import subprocess

# === 1. Скачиваем XLS ===
url = "https://optparf.ru/upload/goods/Актуальный прайс.xls"
xls_filename = "Актуальный прайс.xls"

print("⏬ Загружаем файл...")
response = requests.get(url)
if response.status_code != 200:
    print(f"❌ Ошибка при скачивании: статус {response.status_code}")
    exit(1)

with open(xls_filename, 'wb') as f:
    f.write(response.content)
print("✔️ XLS скачан")

# Проверим наличие и размер файла
if not os.path.exists(xls_filename):
    print("❌ Файл не найден после скачивания.")
    exit(1)

print(f"📄 Файл существует, размер: {os.path.getsize(xls_filename)} байт")

# === 2. Обработка файла ===
print("📊 Читаем файл...")
try:
    df = pd.read_excel(xls_filename, engine="xlrd", header=None)
except Exception as e:
    print("❌ Ошибка чтения Excel:", e)
    exit(1)

df = df.iloc[:, 1:]
df.columns = ['Название', 'Цена']
df = df[pd.to_numeric(df['Цена'], errors='coerce').notnull()]
df['Цена'] = df['Цена'].astype(float)

def adjust_price(price):
    if price < 5000:
        return round(price + 700, 0)
    elif price < 10000:
        return round(price / 95 * 100, 0)
    else:
        return round(price / 98 * 100, 0)

df['Цена'] = df['Цена'].apply(adjust_price)

# === 3. Сохраняем как .xlsx ===
xlsx_output = "Актуальный прайс.xlsx"
df.to_excel(xlsx_output, index=False)
print("✔️ Преобразование завершено")

# === 4. Заливаем в GitHub ===
print("⬆️ Пушим в репозиторий...")

# Устанавливаем конфиг для GitHub Actions
subprocess.run(["git", "config", "user.name", "github-actions"])
subprocess.run(["git", "config", "user.email", "github-actions@github.com"])

# Добавляем, коммитим и пушим
subprocess.run(["git", "add", xlsx_output])
subprocess.run(["git", "commit", "-m", "Обновление XLSX с актуальными ценами"])
subprocess.run(["git", "push"])

print("✅ Успешно запушено.")
