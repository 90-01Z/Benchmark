import requests
from tqdm import tqdm
import multiprocessing as mp

max_retry = 5

def process_single_cip(text: str, url_cip: str, women: bool=False):
    retry = 1
    while retry <= max_retry:
        try:
            r =requests.post("{url}{endpoint}".format(url=url_cip,endpoint="/api/profession_auto/"),json={"libelle": text, "genre": "feminin" if women else "masculin"})
            res = r.json()
            return [x["libelle_feminise" if women else "libelle_masculinise"] for x in res["echos"]]
        except:
            retry +=1
    print(text)
    return []

def process_data_cip(data: list[str], url_cip: str, nb_thread:int = 1, progress: bool = True, women: bool=False):
    if nb_thread > 1:
        p = mp.Pool(processes=nb_thread)
        results = p.starmap(process_single_cip, [(x,url_cip,women) for x in data])
        p.close()
        p.join()
        return {tinput:res for tinput, res in zip(data,results)}
    else:
        return {x:process_single_cip(text=x,url_cip=url_cip,women=women) for x in tqdm(data,disable=not(progress))}

