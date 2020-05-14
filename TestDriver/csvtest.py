from csvparse.csvparse import CsvParse

csv = CsvParse('../TestDriver/TestData/testdata.csv')

print(csv.create_csv_text_for_dict())