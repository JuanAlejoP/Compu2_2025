from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import base64

def generate_screenshot(url: str) -> str:
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1200, 800)
    driver.get(url)
    screenshot = driver.get_screenshot_as_png()
    driver.quit()
    return base64.b64encode(screenshot).decode('utf-8')
