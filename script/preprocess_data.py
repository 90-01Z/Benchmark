import pandas as pd

def init_dataset(url_dataset: str) -> pd.DataFrame:
    data = pd.read_csv(url_dataset,dtype=str, keep_default_na= False)
    return data

def get_unique_occupation_text_input_by_sex(data: pd.DataFrame) -> tuple[set[str], set[str]]:

    men_current_occupation = set(list(data.loc[(~data["PCLCALIBELLEMAX"].isna()) & (data["SEXE"]=="1"),"PCLCALIBELLEMAX"]))
    men_secondary_occupation = set(list(data.loc[(~data["PCLCA2JLIBELLEMAX"].isna()) & (data["SEXE"]=="1"),"PCLCA2JLIBELLEMAX"]))
    men_previous_occupation = set(list(data.loc[(~data["APCLCALIBELLEMAX"].isna()) & (data["SEXE"]=="1"),"APCLCALIBELLEMAX"]))
    men_occupation = men_current_occupation | men_secondary_occupation | men_previous_occupation

    women_current_occupation = set(list(data.loc[(~data["PCLCALIBELLEMAX"].isna()) & (data["SEXE"]=="2"),"PCLCALIBELLEMAX"]))
    women_secondary_occupation = set(list(data.loc[(~data["PCLCA2JLIBELLEMAX"].isna()) & (data["SEXE"]=="2"),"PCLCA2JLIBELLEMAX"]))
    women_previous_occupation = set(list(data.loc[(~data["APCLCALIBELLEMAX"].isna()) & (data["SEXE"]=="2"),"APCLCALIBELLEMAX"]))
    women_occupation = women_current_occupation | women_secondary_occupation | women_previous_occupation

    return men_occupation, women_occupation

