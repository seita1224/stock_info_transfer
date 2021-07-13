from collections import defaultdict
from os import error


def check_csv(file_path: str) -> dict:
    line_number = 0
    erro_info = defaultdict(list)

    with open(file_path, 'r', encoding='utf-8') as f:
        while True:
            line_number += 1
            try:
                row = f.readline()
            except Exception as e:
                erro_info['error_number'].append(line_number)
                erro_info['error_type'].append(type(e))
                erro_info['error_detail'].append(str(e))

            else:
                if not row:
                    break
    
    return erro_info


if __name__ == '__main__':
    error_info = check_csv('input_data/input_csv.csv')

    number_list = error_info['error_number']
    type_list = error_info['error_type']
    detail_list = error_info['error_detail']

    if not len(number_list):
        print('ファイルの内容に問題なし')
    else:
        for number, type, detail in zip(number_list, type_list, detail_list):
            print(f'{number}行目, エラーメッセージ: {type} {detail}')