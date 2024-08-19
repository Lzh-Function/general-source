import arxiv
from datetime import datetime, timedelta
import pytz
import numpy as np
import pandas as pd

client = arxiv.Client()
end = 
start = 
end = 

res_list = []

# query: "(" → "%28", ")" → "%29"
res = client.results(arxiv.Search(query=))
cnt = 0
for r in res:
    info = []
    info.append(r.title)
    info.append(r.summary)
    info.append(str(r))
    res_list.append(info)
    cnt += 1

res_df = pd.DataFrame(columns=["Title", "Abstract", "Link"], index=np.arange(len(res_list)))

if cnt == 0 and len(res_list) == 0:
    print("やり直せｋｓ")
else:
    for i in range(cnt):
        res_df.loc[i] = [res_list[i][0], res_list[i][1], res_list[i][2]]
    print(res_df.shape)
    res_df.to_csv("")
