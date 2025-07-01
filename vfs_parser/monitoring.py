import logging
import subprocess
import time
import sqlite3
import datetime

from vfs_parser.config.page.page import VisaOpenPage
from vfs_parser.pages.check_dates_for_all_visa_types_for_one_city import check_dates_for_all_visa_types_for_one_city
from vfs_parser.pages.login import login_to_vfs
from pyvirtualdisplay import Display

def log_error(error_message):
    now = datetime.datetime.now()
    with sqlite3.connect('database.db') as conn:
        conn.execute(
            'UPDATE metrics SET errors = errors + 1, last_updated = ? WHERE id = (SELECT id FROM metrics ORDER BY last_updated DESC LIMIT 1)',
            (now.isoformat(),)
        )
        conn.commit()
    logging.error(f"Ошибка: {error_message}")


def monitoring():
    try:
        ####
        # UNCOMMENT FOR SERVER
        ####

        display = Display(size=(1920, 1080))
        display.start()

        page = VisaOpenPage.create()
        login_to_vfs(page)
        check_dates_for_all_visa_types_for_one_city(page)

        display.stop()
    except Exception as e:
        log_error(str(e))
        raise
