from itemscraping import SiteAccess, Buyma
from models import BuymaItem, ItemMeta

im = ItemMeta()

im.url = 'https://www.asos.com/nike/nike-mini-swoosh-oversized-hoodie-in-olive-green/prd/14878448?CTAref=We+Recommend+Carousel_3&featureref1=we+recommend+pers'
im.color = 'rose gold'
im.size = 'X'

im_list = [im]

bi = BuymaItem(item_id='50270103',item_name='',item_info=im_list)

by = Buyma()

# 商品情報の入力
by.input_item_stock(bi)

