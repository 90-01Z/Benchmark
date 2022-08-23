import pandas as pd
import os

from script.preprocess_data import init_dataset, get_unique_occupation_text_input_by_sex
from script.stromae import process_data_stromae


def eval_old(input_dataframe: pd.DataFrame(), suggestions: dict[str, list[str]]) -> int:
    data = input_dataframe[["PCLCA","PCLCALIBELLEMAX","SEXE","PCLCANBECHO"]]
    data = data.loc[(~data["PCLCA"].isna()) & (data["PCLCA"]!="") & (data["PCLCA"]!="999") & (data["SEXE"]=="1"),]
    data = data.head(100)
    presence_stromae_list = []
    for i in data.index:
        prof_sel = data.at[i,"PCLCA"]
        prof_input = data.at[i,"PCLCALIBELLEMAX"]
        presence_stromae_list.append(prof_sel in suggestions[prof_input])
    data.insert(loc=0, column="I_PRESENCE_STROMAE", value=presence_stromae_list)
    return sum(data.I_PRESENCE_STROMAE)

if __name__ == '__main__':
    url_dataset = os.environ["URL_DATASET"] # "https://minio.lab.sspcloud.fr/shz42c/hackathon9001Z/EEC_hackathon.csv"
    url_stromae = os.environ["URL_STROMAE"] # "https://stromae-90-01z.dev.insee.io/questionnaire/90-01z/unite-enquetee/11"
    data = init_dataset(url_dataset)
    men_occupations, women_occuations = get_unique_occupation_text_input_by_sex(data)
    print(len(men_occupations))
    print(len(women_occuations))
    suggestions = process_data_stromae(men_occupations, url_stromae, nb_thread=25, progress=True)
    print(eval_old(data, suggestions))
