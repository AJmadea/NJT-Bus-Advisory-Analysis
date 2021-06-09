import pandas as pd
import plotly.express as px
import main as m
import os
import streamlit_app as sap


def rows_over_time():
    base = "C:/Users/Andrew/Desktop/njt_bus_adv_data/info.csv"
    data = pd.read_csv(base)
    latest = sorted(data['DATE_TIME'].unique().tolist())[-1]
    fig = px.line(data, x='DATE_TIME', y='ROWS', title='Unique Rows Of Accumulated Data as of {}'.format(latest))
    fig.show()


def find_most_frequent():
    _dir = "C:/Users/Andrew/Desktop/njt_bus_adv_data/combined/"
    file = os.listdir(_dir)[0]
    print(_dir+file)
    data = pd.read_csv(_dir+file, index_col=0)
    freq_table = m.freq_bus(data['BUS'])
    top = m.get_most_frequent(freq_table)
    print(top)
    freq_frame = pd.DataFrame(data={"Bus Line": freq_table.keys(), "# Appearances": freq_table.values()})
    freq_frame.sort_values(by=['# Appearances', "Bus Line"], inplace=True, ascending=[False, True])
    freq_frame.reset_index(inplace=True, drop=True)
    print(freq_frame.head(20))
    print(freq_frame.shape)
    fig = sap.create_good_bar_graph(freq_frame)
    fig.show()


if __name__ == "__main__":
    rows_over_time()
    find_most_frequent()