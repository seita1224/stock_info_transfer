from csvparse.csvparse import CsvParse


def test():
    csv = CsvParse('/Users/denkaseifutoshi/PycharmProjects/stock_info_transfer/TestDriver/TestData/testdata.csv')

    return csv.create_csv_data()


def test2():
    csv = CsvParse('/Users/denkaseifutoshi/PycharmProjects/stock_info_transfer/TestDriver/TestData/testdata.csv')

    return csv

a = test2()

print(a.get_item_color_list_for_buyma('0050270103'))
print(a.get_item_size_list_for_buyma('0050270103'))
print(a.get_item_color_list_for_shop('0050270103'))
print(a.get_item_size_list_for_shop('0050270103'))
# print(a.get_item_url_list_for_shop('0050270104'))
