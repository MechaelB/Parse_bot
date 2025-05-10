from playwright.sync_api import sync_playwright
import pandas as pd
import sys
import os
from urllib.parse import urlparse

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def main(input_file):
    if not os.path.exists(input_file):
        print(f"Файл {input_file} не найден.")
        return
from playwright.sync_api import sync_playwright
import pandas as pd
import sys
import os
from urllib.parse import urlparse

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def main(input_file):
    # Проверяем, существует ли файл
    if not os.path.exists(input_file):
        print(f"Файл {input_file} не найден.")
        return

    # Чтение данных из Excel
    df = pd.read_excel(input_file)

    # Сохраняем результаты в список
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # headless=True для запуска без окна браузера
        page = browser.new_page()

        for idx, link in enumerate(df.iloc[:, 4]):  # 5-й столбец
            if not isinstance(link, str) or not is_valid_url(link):
                print(f"[{idx}] Пропуск: {link}")
                continue

            try:
                print(f"[{idx}] Переход по: {link}")
                page.goto(link, timeout=30000)

                # Ждем появления вкладки
                page.wait_for_selector('text=Заказчик и поставщик', timeout=10000)
                page.click('text=Заказчик и поставщик')

                # Ждем загрузку секций
                page.wait_for_selector('div.col-md-6', timeout=30000)

                # Извлекаем данные о заказчике
                заказчик_наименование_locator = page.locator('div.col-md-6:has-text("Наименование заказчика (на русском языке)")')
                заказчик_бин_locator = page.locator('div.col-md-6:has-text("БИН"):has-text("Заказчик")')

                заказчик_наименование = заказчик_наименование_locator.locator('tr:nth-child(2) td:nth-child(2)').text_content()
                заказчик_бин = заказчик_бин_locator.locator('tr:nth-child(3) td:nth-child(2)').text_content()

                # Извлекаем данные о поставщике
                поставщик_наименование_locator = page.locator('div.col-md-6:has-text("Наименование поставщика (на русском языке)")')
                поставщик_бин_locator = page.locator('div.col-md-6:has-text("БИН"):has-text("Поставщик")')

                поставщик_наименование = поставщик_наименование_locator.locator('tr:nth-child(2) td:nth-child(2)').text_content()
                поставщик_бин = поставщик_бин_locator.locator('tr:nth-child(3) td:nth-child(2)').text_content()

                # Добавляем в результаты
                results.append({
                    'URL': link,
                    'Заказчик Наименование': заказчик_наименование,
                    'Заказчик БИН': заказчик_бин,
                    'Поставщик Наименование': поставщик_наименование,
                    'Поставщик БИН': поставщик_бин
                })

            except Exception as e:
                print(f"[{idx}] Ошибка при обработке {link}: {e}")
                results.append({
                    'URL': link,
                    'Ошибка': str(e)
                })

        browser.close()

    # Сохраняем результаты один раз после всех переходов
    df_results = pd.DataFrame(results)
    result_path = os.path.join(os.path.dirname(input_file), os.path.basename(input_file).replace(".csv", "_result.csv").replace(".xlsx", "_result.csv").replace(".txt", "_result.csv"))
    df_results.to_csv(result_path, index=False)
    print("Сохранено в файл results.csv")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python parser.py <путь_к_файлу>")
    else:
        main(sys.argv[1])

    df = pd.read_excel(input_file)
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for idx, link in enumerate(df.iloc[:, 4]):  # 5-й столбец
            if not isinstance(link, str) or not is_valid_url(link):
                print(f"[{idx}] Пропуск: {link}")
                continue

            try:
                page.goto(link, timeout=30000)
                page.wait_for_selector('text=Заказчик и поставщик', timeout=10000)
                page.click('text=Заказчик и поставщик')
                page.wait_for_selector('div.col-md-6', timeout=30000)

                бин_элементы = page.query_selector_all('div.col-md-6:has-text("БИН")')
                бин_значения = [элемент.text_content() for элемент in бин_элементы]

                заказчик_наименование = page.locator('div.col-md-6:has-text("Наименование заказчика (на русском языке)")').text_content()
                #заказчик_бин = page.locator('div.col-md-6:has-text("БИН")').text_content()
                заказчик_бин = бин_значения[0]

                поставщик_наименование = page.locator('div.col-md-6:has-text("Наименование поставщика (на русском языке)")').text_content()
                #поставщик_бин = page.locator('div.col-md-6:has-text("БИН")').text_content()
                поставщик_бин = бин_значения[1]

                results.append({
                    'URL': link,
                    'Заказчик Наименование': заказчик_наименование,
                    'Заказчик БИН': заказчик_бин,
                    'Поставщик Наименование': поставщик_наименование,
                    'Поставщик БИН': поставщик_бин
                })
            except Exception as e:
                print(f"Ошибка при обработке ссылки {link}: {str(e)}")

        browser.close()

    # Сохраняем результаты
    result_path = os.path.join(os.path.dirname(input_file).replace("uploads","results"), os.path.basename(input_file).replace(".xlsx", "_result.csv"))
    pd.DataFrame(results).to_csv(result_path, index=False)
    print(f"Результаты сохранены в файл: {result_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Не указан файл для парсинга.")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file)
