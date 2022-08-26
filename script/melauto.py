import requests
from tqdm import tqdm
import multiprocessing as mp

max_retry = 5

def process_single_melauto(text: str, url_melauto: str, women: bool=False):
    retry = 1
    while retry <= max_retry:
        try:
            r =requests.get("{url}/{endpoint}".format(url=url_melauto,endpoint="professionf" if women else "profession"),params={"saisie":text})
            res = r.json()
            return [x["libelle"] for x in res["listeEcho"]]
        except:
            retry += 1
    print(text)
    return []

def process_data_melauto(data: list[str], url_melauto: str, nb_thread: int = 1,  progress: bool = True, women: bool=False):
    if nb_thread > 1:
        p = mp.Pool(processes=nb_thread)
        results = p.starmap(process_single_melauto, [(x,url_melauto,women) for x in data])
        p.close()
        p.join()
        return {tinput:res for tinput, res in zip(data,results)}
    else:
        return {x:process_single_melauto(text=x,url_melauto=url_melauto,women=women) for x in tqdm(data,disable=not(progress))}
