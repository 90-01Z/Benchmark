from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from tqdm import tqdm
import time
import os


def initialization_driver(url_stromae: str) -> Firefox:
    driver = Firefox()
    time.sleep(3)
    driver.get(url_stromae)
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR, ".undefined:nth-child(2) > .MuiButton-label").click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, ".MuiButton-label").click()
    time.sleep(1)
    element = driver.find_element(By.CSS_SELECTOR, "#next-button > .MuiButton-label")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    driver.find_element(By.CSS_SELECTOR, "#next-button > .MuiButton-label").click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, "#next-button > .MuiButton-label").click()
    time.sleep(1)
    return driver

def request_suggester_stromae(driver: Firefox, text_input : str) -> list[str]:
    driver.find_element(By.ID, "l5smshnt-input").clear()
    driver.find_element(By.ID, "l5smshnt-input").send_keys(text_input)
    time.sleep(1)
    elements = driver.find_element(By.ID, "l5smshnt-list")
    return [x.text for x in elements.find_elements(By.CLASS_NAME, 'label') ]

def test_presence_suggester_stromae(suggestions_output: list[str], expected_label: str) -> bool:
    return expected_label in suggestions_output

def init_dataset(url_dataset: str) -> pd.DataFrame:
    data = pd.read_csv(url_dataset,dtype=str)
    data = data[["PCLCA","PCLCALIBELLEMAX","SEXE","PCLCANBECHO"]]
    data = data.loc[~data["PCLCA"].isna(),]
    data = data.loc[data["PCLCA"]!="999",]
    data = data.loc[data["SEXE"]=="1"]
    data = data.head(100)
    return data

def process_benchmark_stromae(data : pd.DataFrame, driver: Firefox) -> None:
    presence_stromae_list = []
    for i in tqdm(data.index):
        prof_sel = data.at[i,"PCLCA"]
        prof_input = data.at[i,"PCLCALIBELLEMAX"]
        propositions = request_suggester_stromae(driver=driver,text_input=prof_input)
        presence_stromae_list.append(test_presence_suggester_stromae(expected_label=prof_sel,suggestions_output=propositions))
    data.insert(loc=0,column="I_PRESENCE_STROMAE",value=presence_stromae_list)    

if __name__ == '__main__':
    url_dataset = os.environ["URL_DATASET"] # "https://minio.lab.sspcloud.fr/shz42c/hackathon9001Z/EEC_hackathon.csv"
    url_stromae = os.environ["URL_STROMAE"] # "https://stromae-90-01z.dev.insee.io/questionnaire/90-01z/unite-enquetee/11"
    driver = initialization_driver(url_stromae)
    data = init_dataset(url_dataset)
    process_benchmark_stromae(data, driver)
    print(sum(data.I_PRESENCE_STROMAE))
