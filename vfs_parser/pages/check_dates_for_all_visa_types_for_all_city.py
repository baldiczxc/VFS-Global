import os
import time
import sqlite3
import datetime

from utils import is_loader_hide


def log_error(error_message):
    now = datetime.datetime.now()
    with sqlite3.connect('database.db') as conn:
        conn.execute(
            'UPDATE metrics SET errors = errors + 1, last_updated = ? WHERE id = (SELECT id FROM metrics ORDER BY last_updated DESC LIMIT 1)',
            (now.isoformat(),)
        )
        conn.commit()
    print(f"Ошибка: {error_message}")


def check_dates_for_all_visa_types_for_all_city(page):
    try:
        city_dropdown = 'xpath://*[@id="mat-select-value-1"]/span'
        visa_type_dropdown = 'xpath:/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[2]/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span'
        visa_subcategory_dropdown = 'xpath:/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[3]/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span'
        options_container = 'xpath:/html/body/div[4]/div[2]/div/div'
        birth_date_input = 'css:body > app-root > div > main > div > app-eligibility-criteria > section > form > mat-card.mat-mdc-card.mdc-card.form-card.ng-star-inserted > form > div:nth-child(7) > div.datepicker-div.form-group > input'

        page.ele(city_dropdown).click()
        city_elements = page.ele(options_container).eles('xpath:./*')
        for l in range(len(city_elements)):
            if l > 0:
                page.ele(city_dropdown).click()
            page.ele(f'xpath:/html/body/div[4]/div[2]/div/div/mat-option[{l + 1}]/span').click()
            is_loader_hide(page)

            page.ele(visa_type_dropdown).click()
            visa_type_elements = page.ele(options_container).eles('xpath:./*')

            for i in range(len(visa_type_elements)):
                if i > 0:
                    page.ele(visa_type_dropdown).click()
                page.ele(f'xpath:/html/body/div[4]/div[2]/div/div/mat-option[{i + 1}]/span').click()
                is_loader_hide(page)

                page.scroll.down(600)
                page.ele(visa_subcategory_dropdown).click()
                subcategory_elements = page.ele(options_container).eles('xpath:./*')

                for j in range(len(subcategory_elements)):
                    if j > 0:
                        page.ele(visa_subcategory_dropdown).click()
                        page.ele(f'xpath:/html/body/div[4]/div[2]/div/div/mat-option[{j + 1}]/span').click()
                        is_loader_hide(page)
                    else:
                        page.ele(f'xpath:/html/body/div[4]/div[2]/div/div/mat-option[{j + 1}]/span').click()
                        is_loader_hide(page)
                        page.ele(birth_date_input).input(os.environ['birth_day'])
                page.scroll.up(600)
        time.sleep(120)
    except Exception as e:
        log_error(str(e))
        raise
