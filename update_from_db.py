from dbfread import DBF
import ProductsFileLoader
from selenium import webdriver
import time, requests, os, sys

products_loader = ProductsFileLoader.ProductsFileLoader()
products_loader.load_groups()
products_loader.load_categories()
products_loader.load_subcategories()
products_loader.load_vendors()
products_loader.load_products(True, False)
repository = products_loader.get_repository()

done = 0
for product_key, product_data in products_loader.products.items():
    updated = repository.update_product(
        product_data.get('part_number'),
        {
            'quantity': product_data.get('quantity'),
            'list_price': product_data.get('list_price'),
            'retail_price': product_data.get('retail_price'),
            'cost': product_data.get('cost'),
        }
    )

    if updated is True:
        done = done + 1
    print('done '+str(done))
