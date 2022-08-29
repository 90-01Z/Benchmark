import pandas as pd
import os
from datetime import datetime
import re
from pathlib import Path

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

type_sex = [
    {"id":"M", "key_EEC":"1","label":"Homme"},
    {"id":"F", "key_EEC":"2","label":"Femme"}
]


def get_rank(text: str, suggestions: list[str]):
    try:
        return suggestions.index(text)+1
    except:
        return 0



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

    print("{date} - Process Stromae - Men".format(date=datetime.now()))
    suggestions_stromae_men = process_data_stromae(men_occupations, url_stromae, nb_thread=25, progress=True, women = False)
    print(sum([len(x)> 0 for x in suggestions_stromae_men.values()]))

    print("{date} - Process Stromae - Women".format(date=datetime.now()))
    suggestions_stromae_women = process_data_stromae(women_occuations, url_stromae, nb_thread=25, progress=True, women = True)
    print(sum([len(x)> 0 for x in suggestions_stromae_women.values()]))  

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

    

    return {
            "M":{"melauto":suggestions_melauto_men,"stromae":suggestions_stromae_men,"cip":suggestions_cip_men},
            "F":{"melauto":suggestions_melauto_women,"stromae":suggestions_stromae_women,"cip":suggestions_cip_women},
    }


def compute_data(data: pd.DataFrame, suggestions: dict):
    data_prof = pd.DataFrame()

    for s in type_sex:
        for t in type_prof:
            total = None
            id_prof = t["id"]
            
            if t["sex"] is None:
                data_sel = data.loc[(~data[id_prof].isna()) & (data[id_prof]!="") & (data[id_prof]!="999") & (data["SEXE"]==s["key_EEC"]),]
            elif t["sex"]==s["id"]:
                data_sel = data.loc[(~data[id_prof].isna()) & (data[id_prof]!="") & (data[id_prof]!="999"),]
            else:
                data_sel =  pd.DataFrame(data={"text_input":[],"text_choice":[],"obs_id":[]})
            data_sel = data_sel.rename(columns={(id_prof+"LIBELLEMAX"):"text_input",id_prof:"text_choice"})
            data_sel = data_sel[["text_input","text_choice","obs_id"]]
            data_sel.insert(loc=0,column="sex_prof_label",value=[s["label"]]*data_sel.shape[0])
            data_sel.insert(loc=0,column="sex_prof_id",value=[s["id"]]*data_sel.shape[0])
            data_sel.insert(loc=0,column="type_prof_label",value=[t["label"]]*data_sel.shape[0])
            data_sel.insert(loc=0,column="type_prof_id",value=[t["id"]]*data_sel.shape[0])
            data_sel.insert(loc=0,column="rank_melauto",value=[get_rank(y,suggestions[s["id"]]["melauto"][x]) for x,y in zip(data_sel.text_input,data_sel.text_choice)])
            data_sel.insert(loc=0,column="rank_cip",value=[get_rank(y,suggestions[s["id"]]["cip"][x]) for x,y in zip(data_sel.text_input,data_sel.text_choice)])
            data_sel.insert(loc=0,column="rank_stromae",value=[get_rank(y,suggestions[s["id"]]["stromae"][x]) for x,y in zip(data_sel.text_input,data_sel.text_choice)])
            data_prof = pd.concat([data_prof,data_sel],ignore_index=True)

    data_prof.rank_melauto = [int(x) for x in data_prof.rank_melauto]
    data_prof.rank_cip = [int(x) for x in data_prof.rank_cip]
    data_prof.rank_stromae = [int(x) for x in data_prof.rank_stromae]
    data_prof.obs_id = [int(x) for x in data_prof.obs_id]
    data_prof = data_prof[["obs_id","type_prof_id","type_prof_label","sex_prof_id","text_input","text_choice","rank_melauto","rank_cip","rank_stromae"]]
    return data

if __name__ == '__main__':
    url_dataset = os.environ["URL_DATASET"] # "https://minio.lab.sspcloud.fr/shz42c/hackathon9001Z/EEC_hackathon.csv"
    url_stromae = os.environ["URL_STROMAE"] # "https://stromae-9001z.kub.sspcloud.fr/questionnaire/90-01Z/unite-enquetee/90-01Z_01"
    url_cip = os.environ["URL_CIP"]  # https://cip-9001z.kub.sspcloud.fr
    url_melauto = os.environ["URL_MELAUTO"]  # https://melauto-9001z.kub.sspcloud.fr
    data_location = os.environ["DATA_LOCATION"]  # "./data/benchmark_eec.csv"
    
    suggestions = compute_suggestions(url_dataset, url_stromae, url_cip, url_melauto)
    data = init_dataset(url_dataset)
    
    evaluation = eval_recouvrement(
        data=data, 
        suggestions=suggestions
    )
    
    print(evaluation["M"])
    print(evaluation["F"])

    data_profs = compute_data(data=data, suggestions=suggestions)
    os.makedirs(Path(data_location).parent)
    data_profs.to_csv(data_location, index=False, encoding="utf-8")
