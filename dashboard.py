import streamlit as st
import pandas as pd
import re
from typing import Literal
import plotly.express as px
import math
import os



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

def eval_recouvrement(data: pd.DataFrame, sex: Literal['M','F','A'] = "A") -> pd.DataFrame:
    list_dict_obs = []
    
    for t in type_prof:
        total = None
        id_prof = t["id"]

        if sex=="A":
            data_sel = data.loc[data["type_prof_id"]==t["id"],]
            total = data_sel.shape[0]
        elif t["sex"] is None or t["sex"]==sex:
            data_sel = data.loc[(data["type_prof_id"]==t["id"]) & (data["sex_prof_id"]==sex)]
            total = data_sel.shape[0]
            
        if total is not None:
            obs = {"label":t["label"], "total": total}
            for name_tool in [x[5:] for x in list(data.columns) if re.match(string=x,pattern="rank_") is not None]:
                obs[name_tool] = data_sel.loc[data_sel["rank_"+name_tool]>0,].shape[0] /total
            list_dict_obs.append(obs)
    res = pd.DataFrame.from_records(list_dict_obs)
    res = res.set_index("label")
    res.rename(columns={"melauto":"Melauto","cip":"CIP","stromae":"Suggester-Lunatic","total":"Nombre d'observations"},inplace=True)
    res = res.style.format(formatter={
        'Melauto': lambda x: "{:.2%}".format(x).replace(".", ",").replace("%"," %"),
        'CIP': lambda x: "{:.2%}".format(x).replace(".", ",").replace("%"," %"),
        'Suggester-Lunatic': lambda x: "{:.2%}".format(x).replace(".", ",").replace("%"," %"),
        'Nombre d\'observations': lambda x: "{:6,d}".format(x).replace(",", " ")
    })
    return res


def eval_rank(data: pd.DataFrame, sex: Literal['M','F','A'] = "A", prof:  Literal['PCLCA','PCLCA2J','APCLCA','FPCLCA','MPCLCA','ALL'] = "ALL", method: Literal['melauto','stromae','cip'] = "melauto"):
    data_list = []
    for name_tool in [x[5:] for x in list(data.columns) if re.match(string=x,pattern="rank_") is not None]:
        x = data.rename(columns={"rank_"+name_tool:"rank"})
        x = x.loc[x["rank"]>0,]
        x.insert(loc=0,column="Outil",value=[name_tool]*x.shape[0])
        x = x[["sex_prof_id","type_prof_id","Outil","rank"]]
        data_list.append(x)

    data_sel = pd.concat(data_list,ignore_index=True)
    if sex != "A":
        data_sel = data_sel.loc[data_sel["sex_prof_id"]==sex,]
    if prof != "ALL":
        data_sel = data_sel.loc[data_sel["type_prof_id"]==prof,]
    data_sel = data_sel.loc[data_sel["Outil"]==method,]

    bin_width= 1
    nbins = math.ceil((data_sel["rank"].max() - data_sel["rank"].min()) / bin_width)
    
    fig = px.histogram(data_sel, x="rank",  marginal="box",range_x=[1,30],range_y=[0, 40],nbins=nbins, histnorm='percent')
    fig.update_layout(
    xaxis_title_text='Rang des suggestion', # xaxis label
    yaxis_title_text='Pourcdentage des observations', # yaxis label
    )

    return fig



data_prof = pd.read_csv(os.environ["DATA_LOCATION"],encoding="utf-8")

st.title('Benchmark d\'outils pour la collecte sur liste des professions')
st.markdown("*Source Enquête emploi en continu 2021*")


st.header("Présentation des trois outils")

st.markdown("""
- [Suggester Lunatic](https://stromae-9001z.kub.sspcloud.fr/questionnaire/90-01Z/unite-enquetee/90-01Z_01) : Outil de codage sur liste dans la nouvelle filière (technologie : Javascript)
- [Melauto](https://melauto-9001z.kub.sspcloud.fr/profession?saisie=Stat) : Outil de collecte des professions dans l'EEC en autoadministré web (technologie : Java)
- [CIP](https://cip-9001z.kub.sspcloud.fr) : Outil de consultation de l'index des professions (technologie : elasticsearch)
""")

st.header("Taux de recouvrement")
st.markdown("""
Il s'agit de la part des observations où les suggestions proposées au travers de l'outil, 
pour le dernier texte qu'avait saisi l'enquêté dans la barre de recherche avant qu'il ne sélectionne un écho dans la liste,
comprenant celle retenue par l'enquêté lors de la collecte.
""")

genre_recouvrement = st.selectbox("Genre des libellés de profession", ["M","F", "A"], index=2 ,format_func=lambda x: {
    "M": "Libellés masculins",
    "F": "Libellés féminins",
    "A": "Libellés féminins et masculins",
}[x])

st.table(eval_recouvrement(data_prof,genre_recouvrement))

st.markdown("""
Le taux de recouvrement de l'outil Melauto devrait être de 100 %. L'outil déployé pour le test est identique à celui utilisé lors de la collecte de l'EEC en 2021. De plus, les listes des professions et des mots vides de sens sont celles qui ont été intégrées en 2021.

*Une piste possible pourrait être une erreur dans les paradonnées de l'EEC. Le libellé collecté en cours de saisi ne serait pas exactement le dernier saisi qui a donné lieu à la sélection d'un écho.*
""")

st.header("Comparaison des rangs des suggestions")

method_rank = st.selectbox("Outil d'autocomplétion", ["melauto", 'cip', 'stromae'], index=0 ,format_func=lambda x: {
    "melauto": "Melauto",
    "cip": "Outil de consultation de l'index des professions",
    "stromae": "Suggester Lunatic",
}[x])

prof_rank = st.selectbox("Type de profession", [x["id"] for x in type_prof] + ["ALL"] , index=len(type_prof) ,format_func=lambda x: "Tous types de profession" if x=="ALL" else [y["label"] for y in type_prof if y["id"]==x][0])

genre_rank = st.selectbox("Genre des libellés", ["M","F", "A"], index=2 ,format_func=lambda x: {
    "M": "Libellés masculins",
    "F": "Libellés féminins",
    "A": "Libellés féminins et masculins",
}[x])


st.plotly_chart(eval_rank(data_prof,genre_rank,prof_rank,method_rank), use_container_width=True)

st.header("Données")


st.dataframe(data_prof[["type_prof_label","text_input","text_choice","rank_melauto","rank_cip","rank_stromae"]].rename(columns={
    "type_prof_label":"Type de profession",
    "text_input":"Texte saisi par l'enquêté",
    "text_choice":"Suggestion choisie par l'enquêté",
    "rank_melauto":"Rang de la proposition Melauto",
    "rank_cip":"Rang de la proposition dans CIP",
    "rank_stromae":"Rang de la proposition dans Lunatic"
    }),width=None)

st.markdown("""
Un rang ayant pour valeur "0" signifie que la proposition choisie par l'enquêté ne se retrouve pas dans les suggestions de l'outil considéré pour le même input (i.e. même texte saisi).
""")


@st.cache
def convert_df(df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
     return data_prof.to_csv(index=False).encode('utf-8')

csv = convert_df(data_prof)

st.download_button(
     label="Télécharger les données au format csv",
     data=csv,
     file_name='benchmark_eec.csv',
     mime='text/csv',
 )
