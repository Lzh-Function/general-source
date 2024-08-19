import requests
import json
import pandas as pd

# term: using "" for phrase (not "()")
term = ""
sort = "RELEVANT_DESC"
limit = ""
searchDateFrom = "2015-01-01T00:00:00.000Z"
skip = 0
# categoryIds: get from URL of the category dashboard
categoryIds = "605c72ef153207001f6470ce"

allhits = pd.DataFrame([], columns=["title", "abstract", "published date", "doi"])

while True:
    url = "https://chemrxiv.org/engage/chemrxiv/public-api/v1/items?term=" + term + "&sort=" + sort + "&limit=" + limit + "&searchDateFrom=" + searchDateFrom +"&skip=" + f"{skip}" + "&categoryIds=" + categoryIds
    
    response = requests.get(url)
    
    if response.status_code != 200:
        print("ERROR!")
        break
    else:
        data = response.json()
        if len(data["itemHits"]) == 0:
            print("FINISHED!")
            break
        else:
            for i, hit in enumerate(data["itemHits"]):
                title = hit["item"]["title"]
                abstract = hit["item"]["abstract"]
                date = hit["item"]["publishedDate"]
                doi = hit["item"]["doi"]
                allhits = pd.concat([allhits, pd.DataFrame(data=[[title, abstract, date, doi]], columns=["title", "abstract", "published date", "doi"])], axis=0)
            skip += 50
            print(f"No.{skip} finished")

allhits.reset_index(inplace=True, drop=True)
allhits.to_csv("")
