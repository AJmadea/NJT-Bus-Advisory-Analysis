from datetime import datetime

import ibm_db
import pandas as pd
import word_categorize as wc
from Logger import Logger


def convert_datetime_to_timestamp(dt_string):
    #assert len(dt_string) == 22
    # It should currently have this format
    # 2021-06-01 01:14:31 PM
    # To
    # 2021-06-01 13:14:31

    # 11 & 12 index are the hour numbers
    pivot = dt_string[11:13]
    if "PM" in dt_string:
        if pivot != '12':
            pivot = str(int(pivot) + 12)
    elif 'AM' in dt_string:
        if pivot == '12':
            pivot = "00"

    return '{} {}{}{}'.format(dt_string[:10], pivot, dt_string[13:16], ":00")


def update_common_table():
    common_attr = create_int_map_common_attr()
    try:
        sql_delete = "delete from common_attr"
        _dsn, _uid, _pwd = __get_credentials__()
        conn = ibm_db.connect(_dsn, _uid, _pwd)
        ibm_db.exec_immediate(conn, sql_delete)

        for k in common_attr.keys():
            sql = "INSERT INTO COMMON_ATTR(id, common) VALUES ({},\'{}\')".format(common_attr[k], k)
            ibm_db.exec_immediate(conn, sql)

        ibm_db.exec_immediate(conn, "INSERT INTO COMMON_ATTR(id, common) values (-1, 'undefined')")
        result = ibm_db.exec_immediate(conn, "SELECT COUNT(*) FROM NJT_BUS")
        row = ibm_db.fetch_tuple(result)

    except Exception as err:
        print(err)
    finally:
        ibm_db.close(conn)


def create_int_map_common_attr():
    common = wc.get_common_attr()
    d = {}
    for i, c in enumerate(common):
        d[c] = int(i)
    return d


def prepare_data_for_db(data):
    common_dictionary = create_int_map_common_attr()
    common = common_dictionary.keys()

    for i in data.index:
        for c in common:
            if c in str(data.loc[i, 'DESCRIPTION']).lower():
                data.loc[i, "COMMON"] = common_dictionary[c]
                data.loc[i,'COMMON PHRASE'] = c
                break
            data.loc[i, 'COMMON'] = -1

    data.to_csv('C:/Users/Andrew/Desktop/njt_bus_adv_data/blah.csv')


def add_to_njt_bus_table(data, l):
    update_common_table()
    l.log("Attempting to Update Table in DB")

    prepare_data_for_db(data)
    l.log("Creating base SQL statement")

    try:
        _dsn, _uid, _pwd = __get_credentials__()
        conn = ibm_db.connect(_dsn, _uid, _pwd)
        l.log("Creating & Executing SQL Statements from data...")
        data.reset_index(inplace=True, drop=True)
        for i in data.index:
            sql = "insert into njt_bus(bus, date_time, common_description_id) values ({}, \'{}\', {})"
            bus = data.loc[i, 'BUS']
            ts = convert_datetime_to_timestamp(data.loc[i, 'DATE_TIME'])
            _c = data.loc[i, 'COMMON']

            sql = sql.format(
                bus, ts, _c
            )

            l.log(sql)
            ibm_db.exec_immediate(conn, sql)

        l.log("Updated table")
        ibm_db.exec_immediate(conn,
                              "DELETE FROM "
                              "(SELECT ROW_NUMBER() OVER (PARTITION BY bus, date_time, common_description_id) "
                              "AS RN FROM njt_bus) "
                              "AS A WHERE RN > 1;")
        l.log("Dropped Duplicates")

        result = ibm_db.exec_immediate(conn, "SELECT COUNT(*) FROM NJT_BUS")
        row = ibm_db.fetch_tuple(result)
        l.log("Rows in database: {}".format(row[0]))

    except Exception as err:
        l.log(err)
    finally:
        l.log("DB connection is closed: {}".format(ibm_db.close(conn)))


def update_word_categorization(now, categories, multiple, one, no_categorization, l):
    try:
        l.log("Attempting to connect to database")
        _dsn, _uid, _pwd = __get_credentials__()
        conn = ibm_db.connect(_dsn, _uid, _pwd)
        sql = "INSERT INTO word_categorization" \
              "(date_time, number_categories, rows, multiple_categories, one_category, " \
              "uncategorized) values (\'{}\', {}, {}, {}, {}, {})".format(
                now.strftime("%Y-%m-%d %H:%M:%S"),
                categories, get_rows(), multiple, one, no_categorization
              )

        ibm_db.exec_immediate(conn, sql)
        l.log("Updated database")
    except Exception as err:
        l.log(err)
    finally:
        l.log('Closed Database Connection: {}'.format(ibm_db.close(conn)))


def update_njt_bus_rows(now, rows, l):
    l.log("Attempting to connect to db")
    try:
        _dsn, _uid, _pwd = __get_credentials__()
        conn = ibm_db.connect(_dsn, _uid, _pwd)
        sql = "INSERT INTO NJT_BUS_ROWS(date_time, rows) values (\'{}\', {})".format(
            now.strftime("%Y-%m-%d %H:%M:%S"),
            rows
        )

        ibm_db.exec_immediate(conn, sql)
    except Exception as err:
        l.log(err)
    finally:
        l.log('Closed Database Connection: {}'.format(ibm_db.close(conn)))


def get_rows():
    try:
        _dsn, _uid, _pwd = __get_credentials__()
        conn = ibm_db.connect(_dsn, _uid, _pwd)
        result = ibm_db.exec_immediate(conn, "SELECT COUNT(*) FROM NJT_BUS")
        row = ibm_db.fetch_tuple(result)
        return row[0]
    finally:
        ibm_db.close(conn)


def bus_bin(data, l):
    # tranform data into bins
    data['BUS_GROUP'] = data['BUS']/100
    data['BUS_GROUP'] = data['BUS_GROUP'].astype(int)
    d = data['BUS_GROUP'].value_counts()

    n = []
    freq = []
    for k in d.keys():
        n.append(k)
        freq.append(d[k])
    df = pd.DataFrame(data={"BUS_GROUP": n, 'Freq': freq})
    df.to_csv('C:/Users/Andrew/Desktop/njt_bus_adv_data/bus_bin.csv')

    try:
        _dsn, _uid, _pwd = __get_credentials__()
        conn = ibm_db.connect(_dsn, _uid, _pwd)
        ibm_db.exec_immediate(conn, "DELETE FROM BUS_BIN")
        for k in d.keys():
            sql = 'INSERT INTO BUS_BIN(BUS_GROUP, FREQ) VALUES({}, {})'.format(k, d[k])
            #l.log(sql)
            ibm_db.exec_immediate(conn, sql)
        l.log("Updated BUS_BIN")
        l.log(sum(d.values()) == data.shape[0])
    except Exception as err:
        print(err)
    finally:
        l.log("Closing connection for BUS_BIN: {}".format(ibm_db.close(conn)))


def get_data_from_database():
    try:
        _dsn, _uid, _pwd = __get_credentials__()
        conn = ibm_db.connect(_dsn, _uid, _pwd)

        bus = []
        timestamp = []
        common_id = []
        sql = "SELECT * FROM NJT_BUS"
        result = ibm_db.exec_immediate(conn, sql)
        row = ibm_db.fetch_tuple(result)
        while row:
            bus.append(row[0])
            timestamp.append(row[1])
            common_id.append(row[2])
            row = ibm_db.fetch_tuple(result)

        df = pd.DataFrame(data={'BUS': bus, 'DATE_TIME': timestamp, 'COMMON': common_id})
        df.head()
        print(df.shape)
        df.drop_duplicates(inplace=True)
        print(df.shape)
        return df
    finally:
        print("Closing connection: {}".format(ibm_db.close(conn)))


def export_db():
    data = get_data_from_database()
    now = datetime.now().strftime("%Y%m%d_%H%m%S")
    data.to_csv('db_data_{}.csv'.format(now))


def drop_everything(l):
    l.log("Attempting to connect to db")
    try:
        _dsn, _uid, _pwd = __get_credentials__()
        conn = ibm_db.connect(_dsn, _uid, _pwd)

        sql = "DELETE FROM NJT_BUS"

        l.log(sql)
        ibm_db.exec_immediate(conn, sql)
    except Exception as err:
        l.log(err)
    finally:
        l.log('Closed Database Connection: {}'.format(ibm_db.close(conn)))


def purge_and_populate():
    export_db()
    try:
        data = wc.get_data()
        prepare_data_for_db(data)
        l = Logger('quicklogs/', max_files=10)

        drop_everything(l)

        add_to_njt_bus_table(data, l)
    except Exception as err:
        l.log(err)
    finally:
        l.flush()


def __get_credentials__():
    lines = None
    with open("C:/Users/Andrew/Desktop/pythonMTAanalysis/database_credentials.txt", "r") as f:
        lines = f.read().split("|")
    return lines[0], lines[1], lines[2]
