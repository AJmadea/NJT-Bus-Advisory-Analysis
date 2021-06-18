import pandas as pd
import os
from datetime import datetime
from Logger import Logger


def convert_to_datetime(string, month_dict):
    # May 24, 2021 12:37:16 PM
    month = month_dict[string[0:3]]
    day = string[4:6]
    if len(day) == 1:
        day = "0"+day
    year = string[8:12]
    return '{}-{}-{} {}'.format(year, month, day, string[-11:])


def combine_files(_base):
    _files = os.listdir(_base)
    _frames = [pd.read_csv(_base + e, index_col=0) for e in _files]
    _frame = pd.concat(_frames)
    _frame.drop_duplicates(inplace=True)
    _frame.reset_index(drop=True, inplace=True)
    return _frame


def update_info_file(now, new_shape):
    info = pd.read_csv("C:/Users/Andrew/Desktop/njt_bus_adv_data/info.csv", index_col=0)
    info = info.append(other={'ROWS': new_shape,
                              'DATE_TIME': now.strftime("%Y-%m-%d_%H:%M:%S")},
                       ignore_index=True)
    info.to_csv("C:/Users/Andrew/Desktop/njt_bus_adv_data/info.csv")


if __name__ == "__main__":
    l = Logger(path="C:/Users/Andrew/Desktop/njt_bus_adv_data/logs/", max_files=100)

    try:
        month_dict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                      'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
        base = "C:/Users/Andrew/Desktop/njt_bus_adv_data/auto/"
        dirs = os.listdir(base)

        if len(dirs) == 0:
            raise ValueError("There were no files in the auto folder...")

        l.log("Amount of files in the auto folder: " + str(len(dirs)))

        frames = []
        for file_name in dirs:
            temp = pd.read_csv(base + file_name, index_col=0)
            print(base+file_name)
            for i in temp.index:
                temp_date = temp.loc[i, 'DATE_TIME']
                dt = str(convert_to_datetime(temp_date, month_dict))
                temp.loc[i, 'DATE_TIME'] = dt
                bus = str(temp.loc[i, 'BUS'])

                temp.loc[i, 'BUS_DATETIME'] = bus + " " + dt
                #print(temp.loc[i, "DESCRIPTION"])
                #print(temp.dtypes)
                temp_string = str(temp.loc[i, 'DESCRIPTION']).strip()
                temp_string = temp_string.replace("&amp;", "")
                temp.loc[i, 'DESCRIPTION'] = temp_string
            frames.append(temp)
        all_data = pd.concat(frames)
        print(all_data.head())
        all_data.drop_duplicates(inplace=True)

        l.log("Amount of rows in the combined auto csv " + str(all_data.shape[0]))

        for e in dirs:
            print('Tyring to remove {}{}'.format(base,e))
            os.remove(base+e)

        base2 = "C:/Users/Andrew/Desktop/njt_bus_adv_data/combined/"
        files = os.listdir(base2)
        l.log("There are {} files in the combined folder".format(len(files)))
        now = datetime.now()
        if len(files) < 1:
            all_data.to_csv(base2 + "current_total_{}.csv".format(now.strftime("%y%m%d_%H%M%S")))
        else:
            frames = []
            new_data = combine_files(base2)
            data = pd.concat([new_data, all_data])
            data.drop_duplicates(inplace=True)

            data.to_csv(base2 + "current_total_{}.csv".format(now.strftime("%y%m%d_%H%M%S")))

            update_info_file(now, data.shape[0])
            l.log("Updating the info.csv... with {} rows".format(data.shape[0]))
            for e in files:
                os.remove(base2+e)

    except Exception as err:  # Use specific exception
        l.log(err)
    finally:
        l.flush()
