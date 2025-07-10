from selenium import webdriver
import os
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime
import datetime
from selenium.webdriver.support.ui import WebDriverWait
import re
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait

def startAmazonAccount():
    chrome_service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--disable-gpu") # Esto puede ayudar en ciertos casos para evitar problemas con el modo headless
    #chrome_options.add_argument("--window-size=1920,1080")
    #chrome_options.add_argument("--enable-logging")
    #chrome_options.add_argument("--log-level=0")  # Habilita todos los logs
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
    login_bottom = driver.find_element(By.ID, 'login-form-login-btn')
    login_bottom.click()
    sleep(2)
    password = driver.find_element(By.ID, 'password')
    password.clear()
    password.send_keys(passw)
    sleep(2)
    login_bottom = driver.find_element(By.ID, 'buttonLogin')
    login_bottom.click()
    print('\a')
    input("Press enter to continue")

    return driver


import datetime

def hora_valida(rango_str):
    try:
        # quitamos “EDT” u otra zona
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
    "Monday, Jun  30.",
    "Tuesday, Jul  1.",
    "Wednesday, Jul  2.",
    "Thursday, Jul  3.",
    "Friday, Jul  4.",
    "Saturday, Jul  5.",
    "Sunday, Jul  6.",
    "Monday, Jul  7.",
    "Tuesday, Jul  8.",
    "Wednesday, Jul  9.",
    "Thursday, Jul  10.",
    "Friday, Jul  11.",
    "Saturday, Jul  12.",
    "Sunday, Jul  13.",
    "Monday, Jul  14.",
    "Tuesday, Jul  15.",
    "Wednesday, Jul  16.",
    "Thursday, Jul  17.",
    "Friday, Jul  18.",
    "Saturday, Jul  19.",
    "Sunday, Jul  20.",
    "Monday, Jul  21.",
    "Tuesday, Jul 22.",
    "Wednesday, Jul  23.",
    "Thursday, Jul  24.",
    "Friday, Jul  25.",
    "Saturday, Jul  26.",
    "Sunday, Jul  27.",
    "Monday, Jul  28.",
    "Tuesday, Jul  29.",
    "Wednesday, Jul  30.",
    "Thursday, Jul  31."
    ]
    # Creamos un patrón rápido para buscar cualquiera de esos strings
    dias_pattern = re.compile("|".join(re.escape(d) for d in dias_permitidos))

    url = "https://atoz.amazon.work/shifts/schedule/find?ref=hm_fs_qklink&date=2025-06-29"
    wait = WebDriverWait(driver, 10)

    print("⏳ Iniciando monitoreo de turnos...")
    while True:
        driver.get(url)
        sleep(2)

        cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-test-id="day-card"]')
        for card in cards:
            aria = card.get_attribute("aria-label").strip()

            # Extraemos cuántos shifts hay
            m = re.search(r"(\d+)\s+shifts available", aria)
            num_shifts = int(m.group(1)) if m else 0

            # Sólo días permitidos y con al menos 1 turno
            if num_shifts > 0 and dias_pattern.search(aria):
                print(f"[📅] Día válido encontrado: {aria}")
                card.click()
                sleep(1)

                # Ahora revisamos los turnos
                shifts = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid^="OpportunityCard-"]')
                for turno in shifts:
                    horario = turno.find_element(By.CSS_SELECTOR, 'div[role="heading"] strong').text.strip()
                    print(f"    🕒 Evaluando {horario}…")
                    if hora_valida(horario):
                        print("    ✅ Turno dentro del rango. ¡Agregando!")
                        btn = turno.find_element(By.CSS_SELECTOR, 'button[data-test-id="AddOpportunityModalButton"]')
                        btn.click()
                        print("    🎯 Turno agregado. Finalizando monitor.")
                    
                    else:
                        print("    ⛔ Turno fuera de horario permitido.")

        print("🔁 No hay turnos válidos ahora. Esperando 2s…\n")
        sleep(2)
driver = startAmazonAccount()
monitor_shifts(driver)