from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return open("index.html").read()

@app.route("/process", methods=["POST"])
def process():
    data = request.json.get("ip")
    if not data:
        return jsonify({"error": "IP-адрес не предоставлен"}), 400

    try:
        # Формируем URL
        url = f"https://mxtoolbox.com/SuperTool.aspx?action=blacklist%3a{data}&run=toolpage"

        # Настройка Selenium
        driver = webdriver.Chrome()  # Убедитесь, что установлен ChromeDriver
        driver.get(url)

        # Ожидаем загрузки таблицы
        time.sleep(5)  # Задержка для полной загрузки страницы

        # Находим таблицу результатов
        table_element = driver.find_element(By.CLASS_NAME, "tool-result-table")
        table_html = table_element.get_attribute("outerHTML")
        driver.quit()

        # Парсим HTML через BeautifulSoup
        soup = BeautifulSoup(table_html, "html.parser")
        rows = soup.find_all("tr")

        # Извлечение данных из таблицы
        result_data = []
        for row in rows:
            cols = row.find_all(["td", "th"])  # Находим все ячейки
            cols_text = [col.get_text(strip=True) for col in cols]  # Извлекаем текст
            result_data.append(cols_text)

        # Преобразуем в форматированный текст или JSON
        return jsonify({"data": result_data})

    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "Не удалось получить данные с сайта-донора"}), 500

if __name__ == "__main__":
    app.run(debug=True)
