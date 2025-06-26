import DrissionPage
from dotenv import load_dotenv


class VisaOpenPage:
    @staticmethod
    def create(base_url='https://visa.vfsglobal.com/blr/ru/pol/dashboard'):
        options = DrissionPage.ChromiumOptions()
        options.incognito(True)
        options.set_argument("--no-sandbox")
        options.set_argument("--lang=en-US,en")
        page = DrissionPage.ChromiumPage(addr_or_opts=options)
        load_dotenv('config/.env')
        page.base_url = base_url
        return page
