from itemscraping import Buyma
from itemscraping import Asos

asos = Asos()
stock_list = asos.item_stock_info('https://www.asos.com/collusion/collusion-x001-skinny-jeans-in-blue-mid-wash/prd/10286741/')
del asos

bu = Buyma()
print(bu.get_sell_item_stock())
del bu
