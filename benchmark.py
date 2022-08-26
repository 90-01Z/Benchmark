import pandas as pd
import os
from datetime import datetime

from script.preprocess_data import init_dataset, get_unique_occupation_text_input_by_sex
from script.stromae import process_data_stromae
from script.cip import process_data_cip
from script.melauto import process_data_melauto

type_prof = [
    {"id":"PCLCA","label":"Profession principale","sex":None},
    {"id":"PCLCA2J","label":"Profession secondaire","sex":None},
    {"id":"APCLCA","label":"Profession antérieure","sex":None},
    {"id":"FPCLCA","label":"Profession du père","sex":"M"},
    {"id":"MPCLCA","label":"Profession de la mère","sex":"F"}
]

def eval_old(input_dataframe: pd.DataFrame, suggestions: dict[str, list[str]]) -> int:
    data = input_dataframe[["PCLCA","PCLCALIBELLEMAX","SEXE","PCLCANBECHO"]]
    data = data.loc[(~data["PCLCA"].isna()) & (data["PCLCA"]!="") & (data["PCLCA"]!="999") & (data["SEXE"]=="1"),]
    presence_stromae_list = []
    for i in data.index:
        prof_sel = data.at[i,"PCLCA"]
        prof_input = data.at[i,"PCLCALIBELLEMAX"]
        presence_stromae_list.append(prof_sel in suggestions[prof_input])
    data.insert(loc=0, column="I_PRESENCE_STROMAE", value=presence_stromae_list)
    return sum(data.I_PRESENCE_STROMAE)

def eval_recouvrement(data: pd.DataFrame, suggestions: dict[str, dict[str, dict[str, list[str]]]]) -> dict[str, pd.DataFrame]:
    output = {}
    for key_sex, suggestions_sex in suggestions.items():
        integer_sex = "2" if key_sex == "F" else "1"
        list_dict_obs = []
        for t in type_prof:
            total = None
            id_prof = t["id"]
            
            if t["sex"] is None:
                data_sel = data.loc[(~data[id_prof].isna()) & (data[id_prof]!="") & (data[id_prof]!="999") & (data["SEXE"]==integer_sex),]
                total = data_sel.shape[0]
            elif t["sex"]==key_sex:
                data_sel = data.loc[(~data[id_prof].isna()) & (data[id_prof]!="") & (data[id_prof]!="999"),]
                total = data_sel.shape[0]

            if total is not None:
                obs = {"label":t["label"], "total": total}
                for name_tool, suggestions_sex_tool in suggestions_sex.items():
                    obs[name_tool] = sum([data_sel.at[i,id_prof] in suggestions_sex_tool[data_sel.at[i,id_prof+"LIBELLEMAX"]] for i in data_sel.index])
                list_dict_obs.append(obs)
        output[key_sex] = pd.DataFrame.from_records(list_dict_obs)
    return output

def compute_suggestions(url_dataset: str, url_stromae: str, url_cip: str, url_melauto: str):
    data = init_dataset(url_dataset)
    men_occupations, women_occuations = get_unique_occupation_text_input_by_sex(data)
    print("Number of unique occupations (men) : {count}".format(count=len(men_occupations)))
    print("Number of unique occupations (women) : {count}".format(count=len(women_occuations)))

    print("{date} - Process Melauto - Men".format(date=datetime.now()))
    suggestions_melauto_men = process_data_melauto(men_occupations, url_melauto, nb_thread=25, progress=True, women = False)
    print(sum([len(x)> 0 for x in suggestions_melauto_men.values()]))

    print("{date} - Process Melauto - Women".format(date=datetime.now()))
    suggestions_melauto_women = process_data_melauto(women_occuations, url_melauto, nb_thread=25, progress=True, women = True)
    print(sum([len(x)> 0 for x in suggestions_melauto_women.values()]))

    print("{date} - Process CIP - Men".format(date=datetime.now()))
    suggestions_cip_men = process_data_cip(men_occupations, url_cip, nb_thread=25 , progress=True, women = False)
    print(sum([len(x)> 0 for x in suggestions_cip_men.values()]))

    print("{date} - Process CIP - Women".format(date=datetime.now()))
    suggestions_cip_women = process_data_cip(women_occuations, url_cip, nb_thread=25 , progress=True, women = True)
    print(sum([len(x)> 0 for x in suggestions_cip_women.values()]))

    print("{date} - Process Stromae - Men".format(date=datetime.now()))
    suggestions_stromae_men = process_data_stromae(men_occupations, url_stromae, nb_thread=25, progress=True, women = False)
    print(sum([len(x)> 0 for x in suggestions_stromae_men.values()]))

    print("{date} - Process Stromae - Women".format(date=datetime.now()))
    suggestions_stromae_women = process_data_stromae(women_occuations, url_stromae, nb_thread=25, progress=True, women = True)
    print(sum([len(x)> 0 for x in suggestions_stromae_women.values()]))  

    return {
            "M":{"melauto":suggestions_melauto_men,"stromae":suggestions_stromae_men,"cip":suggestions_cip_men},
            "F":{"melauto":suggestions_melauto_women,"stromae":suggestions_stromae_women,"cip":suggestions_cip_women},
    }

if __name__ == '__main__':
    url_dataset = os.environ["URL_DATASET"] # "https://minio.lab.sspcloud.fr/shz42c/hackathon9001Z/EEC_hackathon.csv"
    url_stromae = os.environ["URL_STROMAE"] # "https://stromae-9001z.kub.sspcloud.fr/questionnaire/90-01Z/unite-enquetee/90-01Z_01"
    url_cip = os.environ["URL_CIP"]  # https://cip-9001z.kub.sspcloud.fr
    url_melauto = os.environ["URL_MELAUTO"]  # https://melauto-9001z.kub.sspcloud.fr
    
    suggestions = compute_suggestions(url_dataset, url_stromae, url_cip, url_melauto)
    data = init_dataset(url_dataset)
    
    evaluation = eval_recouvrement(
        data=data, 
        suggestions=suggestions
    )
    print(evaluation["M"])
    print(evaluation["F"])
