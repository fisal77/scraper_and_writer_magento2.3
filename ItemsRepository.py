import os, json, codecs, sys
from dbfread import DBF

class ItemsRepository:
    def __init__(self):
        f = open("current_products.txt")
        self.data = f.read().splitlines()
        f.close()

    def product_present(self, item_code):
        if item_code in self.data:
            return True

        return False

    def save_product(self, product_data):
        filename = "data" + os.sep + product_data.get('part_number') + os.sep + "en_info.json"
        print('saving product data', product_data)
        with codecs.open(filename, "w+", encoding='utf-8') as outfile:
            json.dump(product_data, outfile, ensure_ascii=False)

    def update_product(self, part_number, changes):
        filename = "C:\\Users\\t0m3k\\Desktop\\projekty\\YVon\\home\\debian\\pack\\data\\"+part_number+"\\en_info.json"

        if os.path.isfile(filename) is False:
            return
        print('updating product...')
        print("got "+filename+", opening with codecs")
        success = False
        json_content = {}
        try:
            with codecs.open(filename, "r+", encoding='utf-8') as outfile:
                json_content = json.load(outfile)
                for change_key, change_value in changes.items():
                    json_content.update({
                        change_key: change_value
                    })
                success = True
        except:
            print(".")

        if success is True:
            self.save_product(json_content)

        return success