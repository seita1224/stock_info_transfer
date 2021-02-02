from itemscraping import SiteAccess, Buyma
from models import BuymaItem, ItemMeta, Existence

im = ItemMeta()

im.url = 'https://www.asos.com/asos-design/asos-design-baggy-jeans-in-mid-blue-90s-wash/prd/21434410?CTARef=Saved+Items+Image'
im.color = "mid blue 90's wash"
im.shop_size = 'W28in L30in - W71cm L76cm'
im.size = 'W28-L30inch'
im.existence = Existence.IN_STOCK
im_list = [im]

im = ItemMeta()
im.url = 'https://www.asos.com/asos-design/asos-design-baggy-jeans-in-mid-blue-90s-wash/prd/21434410?CTARef=Saved+Items+Image'
im.color = "mid blue 90's wash"
im.shop_size = 'W28in L32in - W71cm L81cm'
im.size = 'W28-L32inch'
im.existence = Existence.IN_STOCK
im_list.append(im)

bi = BuymaItem(item_id='0062129588', item_name='', item_info=im_list)
bi_list = [bi]

by = Buyma()

# 商品情報の入力
by.input_data(bi_list)

