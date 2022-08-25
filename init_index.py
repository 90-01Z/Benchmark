import json
import pandas as pd
import os

path_index_input = os.environ["INDEX_NUMERIC_COMPACT"] # "C:\Users\SHZ42C\Documents\RTI\Refonte de la PCS\data\index_alphabetique_numerique_compact_2022.csv"
data = pd.read_csv(path_index_input,dtype=str, encoding="utf-8")
data = data.loc[data["liste"]== "1",]

os.makedirs("./index_gen/cip", exist_ok=True)
os.makedirs("./index_gen/stromae", exist_ok=True)
os.makedirs("./index_gen/melauto", exist_ok=True)


# OUTPUT CIP
data.to_csv("./index_gen/cip/index_cip.csv",index=False, encoding="utf-8")

# OUTPUT STROMAE
stromae_h = data[["id","libm"]].rename(columns={"libm":"label"})
stromae_h = stromae_h.loc[~stromae_h["label"].isna(),]
stromae_h_dict = stromae_h.to_dict("records")
for el in stromae_h_dict:
    el["id"] = int(el["id"])
stromae_f = data[["id","libf"]].rename(columns={"libf":"label"})
stromae_f = stromae_f.loc[~stromae_f["label"].isna(),]
stromae_f_dict = stromae_f.to_dict("records")
for el in stromae_f_dict:
    el["id"] = int(el["id"])

with open("./index_gen/stromae/PROF2022H.json",mode="w",encoding="utf-8") as f:
    json.dump(stromae_h_dict,f, ensure_ascii=False)

with open("./index_gen/stromae/PROF2022F.json",mode="w",encoding="utf-8") as f:
    json.dump(stromae_f_dict,f, ensure_ascii=False)

# OUTPUT MELAUTO
stromae_h.to_csv("./index_gen/melauto/profession_h.csv",index=False, encoding="utf-8", header=False, sep=";")
stromae_f.to_csv("./index_gen/melauto/profession_f.csv",index=False, encoding="utf-8", header=False, sep=";")
