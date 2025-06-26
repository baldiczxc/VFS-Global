import time


def is_loader_hide(page, css_selector='.ngx-overlay', timeout=1):
    while True:
        loader = page.ele(f'css:{css_selector}', timeout=timeout)
        if loader is not None:
            class_attr = loader.attr('class')
            if class_attr and class_attr.strip() == 'ngx-overlay':
                break
        time.sleep(0.2)
