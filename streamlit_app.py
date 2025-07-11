from xml.etree import ElementTree
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime


def get_nj_date_time():
    # using an API instead of datetime.now() since server might run on a different part of the world.
    # BUT will use datetime.now() if the api connection fails.
    
    return datetime.now().strftime("%A %x %I:%M:%S %p")


def freq_bus(coll):
    d = {}
    for each in coll:
        if each in d.keys():
            t = d[each] + 1
            d[each] = t
        else:
            d[each] = 1
    return d

       

        
     

def parse_data():

    res=requests.get("http://njtransit.com/rss/BusAdvisories_feed.xml")
    res.close()

    tree = ElementTree.fromstring(res.text)

    root=tree[0][7:]

    desc=[]
    bus=[]
    dates=[]

    for advisory in root:
        if advisory.tag=='item':
            bus.append(advisory.find("title").text.split("-")[0].replace("BUS ", ''))
            desc.append(advisory.find('description').text)
            dates.append(advisory.find("pubDate").text)
    
    df = pd.DataFrame({'DESCRIPTION':desc,"BUS":bus,'DATE_TIME':dates})
    df.BUS=df.BUS.astype(int)
    return df
    

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
        if t[0].rstrip() == "":
            continue
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
        d = d[a:index]
        d = d.replace('&amp;', "")
        descript.append(d.strip())
    return pd.DataFrame(data={'BUS': bus_lines, 'DATE_TIME': date_times, 'DESCRIPTION': descript})

@st.cache(hash_funcs={dict: id})
def get_most_frequent(freq_table):
    max_value = max(freq_table.values())
    max_keys = []

    for k in freq_table.keys():
        if freq_table[k] == max_value:
            max_keys.append(k)
    max_keys.sort()
    return "Bus Line(s) {} have {} appearances.".format(str(max_keys)[1:-1], max_value)


def get_histogram(_freq_table):
    values = _freq_table.values()
    v = {}
    for e in values:
        if e in v.keys():
            _t = v[e] + 1
            v[e] = _t
        else:
            v[e] = 1

    # There's a total of 267 routes in NJT
    # If the route DNE in the feed, then it should have 0 advisories.
    v[0] = 267 - len(values)  # Calculating the routes with no advisories
    _df = pd.DataFrame(data={"# Advisories": v.keys(), "# Bus Lines with this many Advisories": v.values()})
    return px.bar(_df, x="# Advisories", y="# Bus Lines with this many Advisories",
                  title='How many advisories are common?')


def create_good_bar_graph(data, current_dt):
    data['Bus Line'] = data['Bus Line'].astype(str)
    return px.bar(data, x='Bus Line', y='# Appearances',
                  title="Freq of Bus Lines on NJT Bus Advisory Feed @ {}".format(current_dt))


@st.cache()
def format_dataframe_into_string(df):
    string = ""
    for i in df.index:
        dt = df.loc[i, 'DATE_TIME']
        desc = df.loc[i, 'DESCRIPTION']
        string += dt + " " + desc + '\n\n'
    return string


if __name__ == '__main__':
    st.title("""New Jersey Transit Bus Advisory Feed""")
    current_dt = get_nj_date_time()
    raw_data = parse_data()

    t = "Last Updated {} Eastern Time".format(current_dt)
    st.header(t)
    option = st.selectbox(label="What To Do", index=0,
                          options=("Most Frequent Bus Lines With Advisories", "Does My Bus Line Have Advisories?"))

    if option == "Most Frequent Bus Lines With Advisories":
        st.subheader("""Finding The Most Common Bus Line That Has/Had Advisories""")
        freq_table = freq_bus(raw_data['BUS'].astype(int))
        freq_frame = pd.DataFrame(data={"Bus Line": freq_table.keys(), "# Appearances": freq_table.values()})

        top_buses = get_most_frequent(freq_table)
        st.write(top_buses)

        freq_frame.sort_values(by=['# Appearances', "Bus Line"], inplace=True, ascending=[False, True])
        freq_frame.reset_index(inplace=True, drop=True)
        fig = create_good_bar_graph(freq_frame, current_dt)
        st.plotly_chart(fig)
        st.plotly_chart(get_histogram(freq_table))
    elif option == "Does My Bus Line Have Advisories?":
        my_line = st.text_input(label='Please Enter Your Bus Line')

        if my_line in raw_data['BUS'].unique().tolist():
            st.write("""That Bus Line Has These Advisories:""")
            _slice = raw_data[raw_data['BUS'] == my_line]
            st.write(format_dataframe_into_string(_slice))
        else:
            st.write("There are no advisories for the {} bus line!".format(my_line))

    st.button(label='Update Graphs')
