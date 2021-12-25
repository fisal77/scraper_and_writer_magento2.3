from dbfread import DBF
import os, sys
import ItemsRepository

class ProductsFileLoader:
    def __init__(self):
        self.items_repository = ItemsRepository.ItemsRepository()
        self.products = {}
        self.groups = {}
        self.categories = {}
        self.subcategories = {}
        self.vendors = {}
        self.exceptions = []


    def initalize(self):
        print('init')
        self.load_groups()
        self.load_categories()
        self.load_subcategories()
        self.load_vendors()
        self.load_products()

    def load_groups(self):
        groups = DBF('ProdCOD' + os.sep + 'comgrp.dbf')
        for group in groups:
            self.groups.update({
                group['GRP']: group['DESCR']
            })

    def load_categories(self):
        categories = DBF('ProdCOD' + os.sep + 'comcat.dbf')
        for category in categories:
            self.categories.update({
                category['GRP']+'-'+category['CAT']: category['DESCR']
            })

    def load_subcategories(self):
        subcategories = DBF('ProdCOD' + os.sep + 'comsub.dbf')
        for subcategory in subcategories:
            self.subcategories.update({
                subcategory['GRP']+'-'+subcategory['CAT']+'-'+subcategory['SUB']: subcategory['DESCR']
            })

    def load_vendors(self):
        vendors = DBF('ProdCOD' + os.sep + 'manuf.dbf')
        for vendor in vendors:
            self.vendors.update({
                vendor['VEND_CODE']: vendor['VEND_NAME']
            })

    def load_products(self, skipEmpty=True, skipLoaded=True):
        print("loading products from database file...")
        products_to_import = DBF('ProdCOD'+os.sep+'products.dbf')
        for product in products_to_import:
            # if its 0 quantity we skip it
            if skipEmpty is True and int(product['QTY']) == 0:
                continue
            # if its already scraped we skip it
            if skipLoaded is True and self.items_repository.product_present(product['PART_NUM']) is True:
                print('skipping '+product['PART_NUM'])
                continue
            # else we add it for scrape
            self.add_available_product(product)

    def add_available_product(self, product):
        # print("Got "+str(len(self.products)))
        group = product['GRP']
        category = product['CAT']
        subcategory = product['SUB']
        vendor = product['VEND_CODE']
        quantity = product['QTY']
        cost = product['COST']
        list_price = product['LIST_PRICE']
        retail_price = product['RETAIL']

        category_key = group+"-"+category
        subcategory_key = category_key+"-"+subcategory
        vendor_key = vendor

        # print('adding item...')
        try:
            self.products.update({
                str(product['PART_NUM']): {
                    "group": str(self.groups[group]),
                    "category": str(self.categories[category_key]),
                    "subcategory": str(self.subcategories[subcategory_key]),
                    "vendor": str(self.vendors[vendor_key]),
                    "manufacturer_part": str(product['MANU_PART']),
                    "part_number": str(product['PART_NUM']),
                    "quantity": quantity,
                    "cost": cost,
                    "list_price": list_price,
                    "retail_price": retail_price
                }
            })
        except Exception as e:
            # print('fail', e)
            self.exceptions.append(product['PART_NUM'])

    def get_repository(self):
        return self.items_repository