from csvparse.csvparse import CsvParse


def test():
    csv = CsvParse('/Users/denkaseifutoshi/PycharmProjects/stock_info_transfer/TestDriver/TestData/testdata.csv')

    return csv.create_csv_data()


def test2():
    csv = CsvParse('/Users/seita/Program/python/stock_info_transfer/input_data/input_csv.csv')

    return csv

a = test2()

print(a.get_item_size_for_shop('0062129588',"mid blue 90's wash",'W34-L32inch'))
print(a.get_item_size_list_for_buyma('0050270103'))
print(a.get_item_color_list_for_shop('0050270103'))
print(a.get_item_size_list_for_shop('0050270103'))
# print(a.get_item_url_list_for_shop('0050270104'))
