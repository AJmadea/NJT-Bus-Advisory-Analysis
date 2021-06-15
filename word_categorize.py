import pandas as pd
import os
import plotly.express as px
from datetime import datetime

from Logger import Logger


def get_data():
    base = "C:/Users/Andrew/Desktop/njt_bus_adv_data/combined/"
    file = os.listdir(base)[0]
    print(base + file)
    data = pd.read_csv(base + file, index_col=0)
    data.reset_index(inplace=True, drop=True)

    for i in data.index:
        # Get rid of &amp;
        temp_string = data.loc[i, 'DESCRIPTION']
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


if __name__ == "__main__":
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
    except Exception as e:
        l.log(e)
    finally:
        l.flush()
