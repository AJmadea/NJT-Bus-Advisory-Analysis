# %%
import pandas as pd
import requests
from xml.etree import ElementTree

# %%
res=requests.get("http://njtransit.com/rss/BusAdvisories_feed.xml")
res.close()

print(res)

tree = ElementTree.fromstring(res.text)

root=tree[0][7:]

titles=[]
desc=[]
nodes=[]
dates=[]

for advisory in root:
    if advisory.tag=='item':
        titles.append(advisory.find('title').text)
        desc.append(advisory.find('description').text)
        nodes.append(advisory.find("link").text.split("/")[-1])
        dates.append(advisory.find("pubDate").text)
    
df = pd.DataFrame({"Title":titles,'Description':desc,'Node':nodes,'DateTime':dates})

# %%
df.Node = df.Node.astype(int)
existingData = pd.read_csv('Advisories.csv')
existingData.Node = existingData.Node.astype(int)
df=df.merge(existingData, indicator=True)
df=df[df._merge=='left_only'].copy()


print(df.shape,'More Rows!')
df.to_csv("Advisories.csv", index=False, mode='a', header=False)


