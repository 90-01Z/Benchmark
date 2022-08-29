from selenium.webdriver import Firefox
from selenium.webdriver.remote.webdriver import BaseWebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import selenium.common.exceptions
from tqdm import tqdm
from typing import Union, Optional
import multiprocessing as mp
from multiprocessing.util import Finalize

class StromaeSession(object):
    def __init__(self, url_stromae: str, is_global: bool):
        self.url_stromae = url_stromae
        self.is_global = is_global
        self.driver = None

    def __enter__(self):
        self.driver = initialization_driver(self.url_stromae, self.is_global)
        print("in __enter__ of %s" % mp.current_process())
        return self

    def __exit__(self):
        self.driver.quit()
        print("in __exit__ of %s" % mp.current_process())


def initialization_driver(url_stromae: str, is_global: bool = True, women: bool = False) -> Firefox:
    if is_global:
        global driver
    options = Options()
    options.headless = True
    driver = Firefox(options=options)

    driver.get(url_stromae)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".undefined:nth-child(2) > .MuiButton-label"))
    )
    driver.find_element(By.CSS_SELECTOR, ".undefined:nth-child(2) > .MuiButton-label").click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".MuiButton-label"))
    )
    driver.find_element(By.CSS_SELECTOR, ".MuiButton-label").click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#next-button > .MuiButton-label"))
    )
    element = driver.find_element(By.CSS_SELECTOR, "#next-button > .MuiButton-label")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#next-button > .MuiButton-label"))
    )
    driver.find_element(By.CSS_SELECTOR, "#next-button > .MuiButton-label").click()
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#next-button > .MuiButton-label"))
    )
    if women:
        driver.find_element(By.CSS_SELECTOR, "#input-label-l5smdkey-1 > p").click()
    else:
        driver.find_element(By.CSS_SELECTOR, "#input-label-l5smdkey-2 > p").click()
    driver.find_element(By.CSS_SELECTOR, "#next-button > .MuiButton-label").click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".lunatic-suggester-input"))
    )
    return driver


def request_suggester_stromae(text_input: str, driver_web: Optional[BaseWebDriver]= None) -> list[str]:
    if driver_web is None:
        driver_web = driver
    driver_web.find_element(By.CSS_SELECTOR, ".lunatic-suggester-input").clear()
    WebDriverWait(driver_web, 10, 0.1).until_not(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#l5smshnt-list > li"))
    )
    driver_web.find_element(By.CSS_SELECTOR, ".lunatic-suggester-input").send_keys(text_input)
    try:
        elements = WebDriverWait(driver_web, 5, 0.1).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".lunatic-suggester-panel > li > div > .label"))
        )
    except selenium.common.exceptions.TimeoutException:
        elements = []
    suggestions = [x.text for x in elements]
    return suggestions


def finalizer():
    driver.quit()

def _worker_init(url_stromae: str, is_global: bool = True, women: bool = False):
    global resource
    initialization_driver(url_stromae, is_global, women)
    Finalize(None, finalizer, exitpriority=10)


def process_data_stromae(data: list[str], url_stromae: str, nb_thread: int = 1, progress: bool = True, women: bool=False) -> dict[str, list[str]]:
    if nb_thread > 1:
        p = mp.Pool(processes=nb_thread, initializer=_worker_init, initargs=(url_stromae, True, women))
        results = p.map(request_suggester_stromae, data)
        p.close()
        p.join()
    else: 
        driver = initialization_driver(url_stromae, False, women)
        results = [request_suggester_stromae(x, driver) for x in tqdm(data, disable=not(progress))]
        driver.quit()
    return {tinput:res for tinput, res in zip(data,results)}
