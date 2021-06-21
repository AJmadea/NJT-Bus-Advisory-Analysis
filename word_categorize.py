import pandas as pd
import os
import plotly.express as px
from datetime import datetime
from Logger import Logger
import main as m


def create_top_bus_line_account_for_ties():
    n = 11
    # Importing data
    os.chdir("C:/Users/Andrew/Desktop/njt_bus_adv_data/")
    _data = pd.read_csv("freq_df.csv")
    # Choosing The Columns
    columns = _data.columns[2:]
    # Creating rankings [1,n)
    ranks = [i for i in range(1, n)]

    # Creating resultant dataframe
    ranking_df = pd.DataFrame(data={"Common Descriptor": columns})
    ranking_df[ranks] = "temp"
    ranking_df.set_index("Common Descriptor", inplace=True)

    # Each slice is sorted by a specific column c
    for c in columns:
        _slice = _data.sort_values(by=c, ascending=False)

        # The values in column c are converted into a list and sorted desc
        list_values = _slice[c].tolist()
        list_values.sort(reverse=True)

        # All busses that have that value are added into a dictionary
        # key : value is freq (int) : bus lines (list of ints)
        v = {}
        for value in list_values:
            v[value] = _slice[_slice[c] == value]['Bus'].tolist()

        # (Error prevention) The length of the ranks and the len of the values should be equal size for the zip()
        if n != len(v.values()):
            diff = -abs(len(v.values()) - n)
            for i in range(-1, diff, -1):
                v[i] = [i]

        # Zipping ranks and values for assignment to the dataframe
        for rank, value in zip(ranks, v.values()):
            ranking_df.loc[c, rank] = str(value)

    for r in ranks:
        ranking_df.rename({r: "Rank {}".format(r)}, axis=1, inplace=True)
    ranking_df.to_csv("ranking_df.csv")


def create_top_bus_line_df():
    n = 21
    os.chdir("C:/Users/Andrew/Desktop/njt_bus_adv_data/")
    _data = pd.read_csv("freq_df.csv")
    columns = _data.columns[2:]
    ranks = [i for i in range(1, n)]

    ranking_df = pd.DataFrame(data={"Common Descriptor": columns})
    ranking_df[ranks] = -1
    ranking_df.set_index("Common Descriptor", inplace=True)

    for c in columns:
        _slice = _data.sort_values(by=c, ascending=False)
        list_buses = _slice["Bus"].tolist()
        list_values = _slice['Freq'].tolist()

        for rank in ranks:
            if list_values[rank-1] == 0:
                break
            ranking_df.loc[c, rank] = list_buses[rank-1]

    for r in ranks:
        ranking_df.rename({r: "Rank {}".format(r)}, axis=1, inplace=True)
    ranking_df.to_csv("ranking_df.csv")


def common_bus_line_for_each_word():
    _data = get_data()
    _common = get_common_attr()
    freq_table = m.freq_bus(_data['BUS'])
    freq_df = pd.DataFrame(data={"Bus": freq_table.keys(), "Freq": freq_table.values()})
    freq_df.sort_values(by="Freq", inplace=True, ascending=False)
    freq_df.set_index("Bus", inplace=True)

    # a new column is created for each common attr in common
    for c in _common:
        freq_df[c] = 0

    for bus_line in freq_df.index:
        _slice = _data[_data['BUS'] == bus_line]
        d = {}
        for _i in _slice.index:
            for c in _common:
                if c in str(_slice.loc[_i, 'DESCRIPTION'].lower()):
                    if c in d.keys():
                        d[c] = d[c] + 1
                    else:
                        d[c] = 1
        for k in d.keys():
            freq_df.loc[bus_line, k] = d[k]

    freq_df.to_csv("freq_df.csv")


def get_data():
    base = "C:/Users/Andrew/Desktop/njt_bus_adv_data/combined/"
    file = os.listdir(base)[0]
    print(base + file)
    data = pd.read_csv(base + file, index_col=0)
    data.reset_index(inplace=True, drop=True)

    for i in data.index:
        # Get rid of &amp;
        temp_string = str(data.loc[i, 'DESCRIPTION']).lower()
        temp_string = temp_string.strip()
        temp_string = temp_string.replace('&amp; ', "")
        data.loc[i, 'DESCRIPTION'] = temp_string
    return data


def get_common_attr():
    with open("C:/Users/Andrew/Desktop/NJT_Bus_Advisory/common.txt") as f:
        _common = f.readlines()

    __common = []
    for c in _common:
        __common.append(c[:-1])
    return __common


def get_freq_table(common_attr, _data):
    _d = {}
    print(common_attr)
    print(_data)
    for c in common_attr:
        _d[c] = 0
    for _i in _data.index:
        _temp = _data.loc[_i, 'DESCRIPTION'].lower()
        for k in _d.keys():
            if k in _temp:
                t = _d[k] + 1
                _d[k] = t
    return _d


def create_text_files_foreach_common():
    data = get_data()
    common = get_common_attr()

    for c in common:
        _d = {c: []}
        file_name = c.replace(" ", "_")
        file_name = file_name.replace('.', '')
        for _i in data.index:
            desc = data.loc[_i, 'DESCRIPTION'].lower()
            if c in desc:
                _temp = _d[c]
                _temp.append(desc)

        with open("word_lists/word_lists_{}.txt".format(file_name), 'w') as f:
            f.write("Descriptions that contain\n \'{}\'\n".format(c))
            for w in _d[c]:
                f.write("{}\n".format(w))


if __name__ == "__main__":
    os.chdir("C:/Users/Andrew/Desktop/njt_bus_adv_data/")
    l = Logger(path="C:/Users/Andrew/Desktop/njt_bus_adv_data/word_logs/", max_files=25)
    try:
        l.log("Reading in data from combined/")
        data = get_data()

        l.log("Reading in the common attributes...")
        common = get_common_attr()

        l.log("Creating a frequency table (dictionary) of the common attr")
        d = get_freq_table(common, data)

        percent_categorized = sum(d.values())/data.shape[0] * 100
        l.log("% Categorized: {}".format(percent_categorized))

        misc = []
        dups = []
        norm = []

        l.log("Finding amount duplicates/uncategorized/1 association")
        for i in data.index:
            temp = data.loc[i, 'DESCRIPTION'].lower()

            bools = [int(c in temp) for c in common]
            _sum = sum(bools)
            if _sum == 0:
                misc.append(temp)
            elif _sum > 1:
                dups.append(temp)
            elif _sum == 1:
                norm.append(temp)

        l.log("Uncategorized\t{}".format(len(misc)))
        l.log(">1 Assoc\t{}".format(len(dups)))
        l.log("1 Association:\t{}".format(len(norm)))
        l.log("The sum of these should be equal to the number of rows in the data: {}".format(
            len(misc) + len(dups) + len(norm) == data.shape[0]
        ))

        l.log("Reading from words.csv")
        # Index, Date_Time, One Category, More Than One Category, Uncategorized, % Categorized, Rows
        words = pd.read_csv("C:/Users/Andrew/Desktop/njt_bus_adv_data/words.csv", index_col=0)
        words = words.append(other={"DATE_TIME": datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
                                    "One Category": len(norm),
                                    "More Than One Category": len(dups),
                                    "Uncategorized": len(misc),
                                    "% Categorized": percent_categorized,
                                    "Rows": data.shape[0],
                                    "# Categories": len(common)},
                             ignore_index=True)
        l.log("Exporting progress to csv")
        words.to_csv("C:/Users/Andrew/Desktop/njt_bus_adv_data/words.csv")

        l.log("Writing uncategorized descriptions...")
        with open("C:/Users/Andrew/Desktop/njt_bus_adv_data/word_lists/uncategorized_descriptions.txt", "w") as f:
            f.write("{} Uncategorized:\n".format(len(misc)))
            for line in misc:
                f.write("{}\n".format(line))

        l.log("Writing Multiple Associated Descriptions...")
        with open("C:/Users/Andrew/Desktop/njt_bus_adv_data/word_lists/multi_words.txt", "w") as f:
            f.write("{} Descriptions with 2 Associations:\n".format(len(dups)))
            for line in dups:
                f.write("{}\n".format(line))

        l.log("Writing the words that fit into one category...")
        create_text_files_foreach_common()

        l.log("Updating freq_df.csv...")
        common_bus_line_for_each_word()

        l.log("Updating and accounting for ties ranking_df.csv")
        create_top_bus_line_account_for_ties()

    except Exception as e:
        l.log(e)
    finally:
        l.flush()
