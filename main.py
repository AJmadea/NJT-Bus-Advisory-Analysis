import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime


def freq_bus(coll):
    d = {}
    for each in coll:
        if each in d.keys():
            t = d[each] + 1
            d[each] = t
        else:
            d[each] = 1
    return d


def get_data():
    url = "https://www.njtransit.com/rss/BusAdvisories_feed.xml"
    data = requests.get(url)
    data = data.text.replace("\t", "")
    item_list = data.split('<item>')
    item_list = item_list[1:]

    bus_lines = []
    date_times = []
    descriptions = []
    for each_line in item_list:
        fromTitle = each_line.find("<title>BUS ")
        endTitle = each_line.find("</title>")
        t = each_line[(fromTitle + len("<title>BUS ")):endTitle].split(' - ')
        bus_lines.append(t[0])
        date_times.append(t[1])
        fromDesc = each_line.find('<description>')
        toDesc = each_line.find("</description>")
        descriptions.append(each_line[(fromDesc + 13):toDesc])

    descript = []
    for d in descriptions:
        a = d.find(': ')
        a = 0 if a == -1 else a
        index = d.find(' - ')
        descript.append(d[a:index])

    df = pd.DataFrame(data={'BUS': bus_lines, 'DATE_TIME': date_times, 'DESCRIPTION': descript})

    freq = freq_bus(df['BUS'].astype(int))

    freq_df = pd.DataFrame(data={"Bus Line": freq.keys(), "# Appearances": freq.values()})
    return freq_df, freq, df


@st.cache(hash_funcs={dict: id})
def get_most_frequent(freq_table):
    max_value = max(freq_table.values())
    max_keys = []

    for k in freq_table.keys():
        if freq_table[k] == max_value:
            max_keys.append(k)

    keys = str(max_value)
    if len(max_keys):
        keys = keys[1:len(keys)]

    return "Bus Line(s) {} have {} appearances.".format(max_keys, max_value)


if __name__ == '__main__':
    st.header("""NJT Bus Advisory""")
    st.subheader("""Finding The Most Common Bus Line That Has/Had Advisories""")
    freq_frame, freq_table, raw_data = get_data()
    now = datetime.now()
    #raw_data.to_csv("C:/Users/Andrew/Desktop/njt_bus_adv_data/NJT_BUS_ADV_Data_" + now.strftime("%y%m%d_%H%M%S")+".csv")
    t = "Last Updated \n{}".format(now.strftime("%c"))
    st.write(t)

    top_buses = get_most_frequent(freq_table)
    st.write(top_buses)

    fig = px.bar(freq_frame, x='Bus Line', y='# Appearances',
                 title="Freq of Bus Lines on NJT Bus Advisory Feed")
    st.plotly_chart(fig)
    st.button(label='Fetch Info')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
