from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import base64
import logging
import time

logger = logging.getLogger(__name__)

def generate_screenshot(url: str, timeout: int = 30) -> str:
    """
    Genera un screenshot de la página web renderizada.
    
    Args:
        url: URL de la página
        timeout: Timeout en segundos
    
    Returns:
        Imagen en base64, o None si hay error
    """
    driver = None
    try:
        # Configurar opciones de Chrome
        options = Options()
        options.headless = True
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        
        # Crear driver
        driver = webdriver.Chrome(options=options)
        
        # Configurar timeouts
        driver.set_page_load_timeout(timeout)
        driver.implicitly_wait(10)
        
        # Acceder a la URL
        driver.set_window_size(1920, 1080)
        logger.info(f"Cargando URL: {url}")
        driver.get(url)
        
        # Esperar a que cargue el contenido (máximo 10 segundos)
        try:
            WebDriverWait(driver, 10).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
        except:
            logger.warning(f"Timeout esperando document.readyState para {url}")
        
        # Tomar screenshot
        screenshot_bytes = driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        logger.info(f"Screenshot generado exitosamente para {url}")
        return screenshot_b64
        
    except Exception as e:
        logger.error(f"Error generando screenshot para {url}: {e}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
