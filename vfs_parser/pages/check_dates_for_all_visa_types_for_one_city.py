import logging
import os
import time

from vfs_parser.utils.check_elements.is_loader_hide import is_loader_hide


def check_dates_for_all_visa_types_for_one_city(page):
    city_dropdown = 'xpath://*[@id="mat-select-value-1"]/span'
    city_option = f'xpath://span[contains(text(),"Poland Visa Application Center-{os.environ["city"]}")]'
    visa_type_dropdown = 'xpath:/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[2]/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span'
    visa_subcategory_dropdown = 'xpath:/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[3]/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span'
    options_container = 'xpath:/html/body/div[4]/div[2]/div/div'
    birth_date_input = 'css:body > app-root > div > main > div > app-eligibility-criteria > section > form > mat-card.mat-mdc-card.mdc-card.form-card.ng-star-inserted > form > div:nth-child(7) > div.datepicker-div.form-group > input'
    button_selector = '/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[2]/button'
    page.ele(city_dropdown, timeout=30).click()
    page.ele(city_option, timeout=30).click()
    is_loader_hide(page)

    page.ele(visa_type_dropdown, timeout=30).click()
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
            page.ele(birth_date_input).clear()
            page.ele(birth_date_input).input(os.environ['birth_day'])
            dates_container = page.ele(
                'xpath:/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[5]/div').text
            logging.basicConfig(level=logging.INFO)
            logging.info(f"🌍 City:           {page.ele(city_option).text}\n"
                         f"🛂 Visa Type:      {visa_type_elements[i].text}\n"
                         f"📂 Subcategory:    {subcategory_elements[j].text}\n"
                         f"📅 Available Dates: {dates_container}\n"
                         "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                         )

    page.run_js(f'''
        const button = document.evaluate("{button_selector}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (button) {{
            button.disabled = false;
            button.removeAttribute('disabled');
        }}
    ''')
    time.sleep(1)
    page.ele(
        "xpath:/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[2]/button/span[2]").click()

# accept button after fill form /html/body/app-root/div/main/div/app-applicant-details/section/mat-card[2]/div[2]/div[2]/button/span[2]
