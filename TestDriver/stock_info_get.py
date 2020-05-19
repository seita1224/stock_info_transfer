from itemscraping import Buyma
from itemscraping import Asos

asos = Asos()
stock_list = asos.item_stock_info('https://www.asos.com/collusion/collusion-x001-skinny-jeans-in-blue-mid-wash/prd/10286741/')
print(stock_list)
# del asos

# try:
#     bu = Buyma()
#     print(bu.get_sell_item_stock())
# except Exception as e:
#     print(e.args)
# # del bu

from itemscraping.sitesmeta import SitesMeta
# from models import ItemMeta, BuymaItem
#
# meta = ItemMeta()
# meta.size = 'a'
# meta.color = 'b'
# meta.existence = True
#
# by = BuymaItem()
# by.item_info = meta
#
# print(by.item_info[0])
#
try:
    bu = Buyma()
    item_id_list = bu.get_item_id_list()
    print(bu.get_item_id_list())
    print(bu.get_item_color_list(item_id_list[2]))
    print(bu.get_item_size_list(item_id_list[2]))
except Exception as e:
    print(e.args)

