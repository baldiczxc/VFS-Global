import logging
import subprocess
import time

from vfs_parser.config.page.page import VisaOpenPage
from vfs_parser.pages.check_dates_for_all_visa_types_for_one_city import check_dates_for_all_visa_types_for_one_city
from vfs_parser.pages.login import login_to_vfs
from pyvirtualdisplay import Display

def monitoring():
    ####
    # UNCOMMENT FOR SERVER
    ####

    display = Display(size=(1920, 1080))
    display.start()

    page = VisaOpenPage.create()
    login_to_vfs(page)
    check_dates_for_all_visa_types_for_one_city(page)

    display.stop()
