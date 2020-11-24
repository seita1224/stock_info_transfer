import logout
from itemscraping import Asos

asos = Asos()

item_list = asos.get_item_stock('https://www.asos.com/nike/nike-mini-swoosh-oversized-cropped-grey-zip-through-hoodie'
                                '/prd/20121315?ctaref=recently+viewed')

logout.output_log_debug(None, str(item_list))
