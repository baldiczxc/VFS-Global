import time


def is_cloudflare_bypass(page,
                         xpath='/html/body/app-root/div/main/div/app-login/section/div/div/mat-card/form/app-cloudflare-captcha-container/div/div/input'):
    while True:
        value = page.ele(
            f'xpath:{xpath}').value
        if value is not None and value != '':
            break
        time.sleep(1)
