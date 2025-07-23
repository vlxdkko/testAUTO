import pandas as pd
import requests
import subprocess
import os

# === 1. Скачиваем XLS ===
url = "https://optparf.ru/upload/goods/Актуальный прайс.xls"
xls_filename = "Актуальный прайс.xls"

response = requests.get(url)
with open(xls_filename, 'wb') as f:
    f.write(response.content)
print("✔️ XLS скачан")

# === 2. Обработка файла ===
df = pd.read_excel(xls_filename, engine="xlrd", header=None)
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

# === 4. Клонируем целевой репозиторий ===
TARGET_REPO = "github.com/vlxdkko/fullparf.git"
BRANCH = "main"
TOKEN = os.environ.get("TARGET_REPO_PAT")
if not TOKEN:
    print("❌ Переменная окружения TARGET_REPO_PAT не найдена")
    exit(1)

url_with_token = f"https://x-access-token:{TOKEN}@{TARGET_REPO}"

subprocess.run(["git", "clone", "--depth", "1", "--branch", BRANCH, url_with_token, "target-repo"], check=True)
os.chdir("target-repo")

# === 5. Копируем файл и пушим ===
subprocess.run(["mv", f"../{xlsx_output}", xlsx_output])
subprocess.run(["git", "config", "user.name", "GitHub Actions"])
subprocess.run(["git", "config", "user.email", "actions@github.com"])
subprocess.run(["git", "add", xlsx_output])
subprocess.run(["git", "commit", "-m", "Обновление XLSX с актуальными ценами"])
subprocess.run(["git", "push"])

print("✅ XLSX залит в vlxdkko/fullparf")
