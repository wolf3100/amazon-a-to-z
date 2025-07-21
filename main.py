from selenium import webdriver
import os
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep
import datetime
import re

def startAmazonAccount():
    chrome_service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get("https://atoz-login.amazon.work/")
    sleep(4)

    user = "0000"
    passw = "0000"
    username = driver.find_element(By.ID, 'associate-login-input')
    username.clear()
    username.send_keys(user)
    sleep(2)

    driver.find_element(By.ID, 'login-form-login-btn').click()
    sleep(2)

    password = driver.find_element(By.ID, 'password')
    password.clear()
    password.send_keys(passw)
    sleep(2)

    driver.find_element(By.ID, 'buttonLogin').click()
    print('\a')
    input("Press enter to continue")

    return driver

def keep_alive(driver, timeout=2):
    """
    Si aparece el modal 'Are you still there?', hace click en 'Stay logged in'.
    """
    try:
        modal = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test-component="StencilModal"]'))
        )
        stay_btn = modal.find_element(By.XPATH, './/button[.//div[text()="Stay logged in"]]')
        stay_btn.click()
        print(" Sesión renovada: clickeado 'Stay logged in'.")
    except TimeoutException:
        pass  # no apareció el modal

def hora_valida(rango_str):
    try:
        horario = rango_str.split()[0]  # e.g. "9:10am-11:50am"
        hora_inicio, hora_fin = horario.split("-")
        fmt = "%I:%M%p"
        inicio = datetime.datetime.strptime(hora_inicio.lower(), fmt).time()
        fin    = datetime.datetime.strptime(hora_fin.lower(), fmt).time()
        return datetime.time(7, 0) <= inicio and fin <= datetime.time(23, 0)
    except Exception as e:
        print(f"⚠️ Error al parsear hora «{rango_str}»: {e}")
        return False

def monitor_shifts(driver):
    dias_permitidos = [
        "Friday, Jul  11.","Saturday, Jul  12.","Sunday, Jul  13.","Monday, Jul  14.",
        "Tuesday, Jul  15.","Wednesday, Jul  16.","Thursday, Jul  17.","Friday, Jul  18.",
        "Saturday, Jul  19.","Sunday, Jul  20.","Monday, Jul  21.","Tuesday, Jul  29.",
        "Wednesday, Jul  23.","Thursday, Jul  24.","Friday, Jul  25.","Saturday, Jul  26.",
        "Sunday, Jul  27.","Monday, Jul  28.","Tuesday, Jul  29.","Wednesday, Jul  30.",
        "Thursday, Jul  31.", "Friday, Aug  1.", "Saturday, Aug  2.", "Sunday, Aug  3.", "Monday, Aug  4.", "Tuesday, Aug  5.", "Wednesday, Aug  6.", "Thursday, Aug  7.", "Friday, Aug  8.", "Saturday, Aug  9.", "Sunday, Aug  10.", "Monday, Aug  11."
    ]
    dias_pattern = re.compile("|".join(re.escape(d) for d in dias_permitidos))

    url = "https://atoz.amazon.work/shifts/schedule/find?ref=hm_fs_qklink&date=2025-06-29"
    wait = WebDriverWait(driver, 10)

    print("⏳ Iniciando monitoreo de turnos...")
    while True:
        # 1) renovamos sesión si es necesario
        keep_alive(driver)

        driver.get(url)
        sleep(2)

        cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-test-id="day-card"]')
        for card in cards:
            aria = card.get_attribute("aria-label").strip()
            m = re.search(r"(\d+)\s+shifts available", aria)
            num_shifts = int(m.group(1)) if m else 0

            if num_shifts > 0 and dias_pattern.search(aria):
                print(f"[📅] Día válido encontrado: {aria}")
                card.click()
                sleep(1)

                # 2) renovamos sesión tras desplegar turnos
                keep_alive(driver)

                shifts = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid^="OpportunityCard-"]')
                for turno in shifts:
                    horario = turno.find_element(By.CSS_SELECTOR, 'div[role="heading"] strong').text.strip()
                    print(f"    🕒 Evaluando {horario}…")
                    if hora_valida(horario):
                        print("    ✅ Turno dentro del rango. ¡Agregando!")
                        turno.find_element(By.CSS_SELECTOR, 'button[data-test-id="AddOpportunityModalButton"]').click()
                        print("    🎯 Turno agregado. Finalizando monitor.")
                        return
                    else:
                        print("    ⛔ Turno fuera de horario permitido.")

        print("🔁 No hay turnos válidos ahora. Esperando 2s…\n")
        sleep(2)

if __name__ == "__main__":
    driver = startAmazonAccount()
    monitor_shifts(driver)


