import os
import sqlite3
import datetime

from DrissionPage._functions.keys import Keys
from dotenv import load_dotenv

from vfs_parser.utils.check_elements.is_cloudflare_bypass import is_cloudflare_bypass
from vfs_parser.utils.check_elements.is_loader_hide import is_loader_hide

load_dotenv()


def log_error(error_message):
    now = datetime.datetime.now()
    with sqlite3.connect('database.db') as conn:
        conn.execute(
            'UPDATE metrics SET errors = errors + 1, last_updated = ? WHERE id = (SELECT id FROM metrics ORDER BY last_updated DESC LIMIT 1)',
            (now.isoformat(),)
        )
        conn.commit()
    print(f"Ошибка: {error_message}")


def login_to_vfs(page):
    try:
        email = os.getenv('email_login')
        password = os.getenv('password_login')

        tabs = page.tab_ids
        new_window = page.get_tab(tabs[-1])

        new_window.get(page.base_url)

        new_window.ele('xpath:/html/body/div[2]/div[2]/div/div/div[2]/div/div/button[1]', timeout=60).click()
        new_window.ele('xpath://*[@id="email"]', timeout=60).input(email)
        new_window.ele('xpath://*[@id="password"]', timeout=60).input(password)
        is_cloudflare_bypass(new_window)
        new_window.ele(
            'xpath:/html/body/app-root/div/main/div/app-login/section/div/div/mat-card/form/button', timeout=60).click()
        new_window.get_screenshot('tmp', 'login_page.png')
        new_window.ele(
            'xpath:/html/body/app-root/div/main/div/app-dashboard/section[1]/div/div[1]/div[2]/button',
            timeout=60).input(
            Keys.ENTER)
        is_loader_hide(new_window)
    except Exception as e:
        log_error(str(e))
        raise