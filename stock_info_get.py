from itemscraping.asos import Asos

asos = Asos('https://www.asos.com/collusion/collusion-x001-skinny-jeans-in-blue-mid-wash/prd/10286741/','test')

print(asos.item_stock_info())