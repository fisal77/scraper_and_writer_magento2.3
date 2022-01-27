

import csv, glob, codecs
from dbfread import DBF
import ProductsFileLoader
from selenium import webdriver
import time, requests, os, sys, json
import datetime


class SaveToCsvTable:

    def write_to_csv():
        """
        this uses output from previous script, reads data files and prepares html etc. and then produces csv file to
        update for running from cron setup full path on server below
        """
        # setup full path on server here
        print("reading products folders...")
        item_folders = glob.glob("data//*")

        print("processing items")
        i = 0
        for item_f in item_folders:
            try:
                if i < 41:
                    i = i + 1

                print("doing item "+str(i))
                createDateTime = datetime.datetime.now()
                json_data_file = item_f + os.sep + "en_info.json"
                json_data = json.load(open(json_data_file, encoding='utf-8'))
                name = json_data.get('title').strip()
                images = json_data.get('images')

                # define category
                if json_data.get('category').strip() == json_data.get('subcategory').strip():
                    categories = "Default Category/" + json_data.get('group').strip().replace(" - ", "$-$").replace(" -", "-")\
                        .replace("- ", "-").replace("$-$", " - ") + '/' + json_data.get('category').strip()
                else:
                    categories = "Default Category/" + json_data.get('group').strip().replace(" - ", "$-$").replace(" -", "-")\
                        .replace(
                        "- ", "-").replace("$-$", " - ") + '/' + json_data.get('category').strip() + '/' + json_data.get(
                        'subcategory').strip().replace(" - ", "$-$").replace(" -", "-").replace("- ", "-").replace("$-$", " - ")

                attributes = json_data.get('specs')
                attrs = []

                for attr_key, attr_value in attributes.items():
                    attrs.append("<span style='font-weight: 500;'>"+attr_key.replace(" "," ").title().replace("\n","") + ": </span>" + attr_value.replace("\n","<br/>"))

                attrs_ready = "<br/>".join(attrs)

                no_duplicated_imgs = []
                for image in images:
                    if image not in no_duplicated_imgs:
                        no_duplicated_imgs.append(image)

                data_to_write = {}
                data_to_write.update({'sku': json_data.get('part_number').strip()})
                data_to_write.update({'base_image': images[0]})
                data_to_write.update({'small_image': images[0]})
                data_to_write.update({'thumbnail_image': images[0]})
                data_to_write.update({'additional_images': ",".join(no_duplicated_imgs[1:])})
                # data_to_write.update({'manufacturer': json_data.get("vendor")})
                data_to_write.update({'store_view_code': 'default'})
                data_to_write.update({'attribute_set_code': 'Default'})
                data_to_write.update({'product_type': 'simple'})
                data_to_write.update({'categories': categories})
                data_to_write.update({'product_websites': 'base'})
                data_to_write.update({'name': name})
                description_html = json_data.get('description').replace("\n","<br/>").replace("\t","").replace("Description\n\t\t\tDescription: ","").strip().replace('"',"'")
                description_html = description_html.replace("Description<br/>Description:","").strip()
                description_html_break = description_html.split("<br/>")

                if (len(description_html) >= 2):
                    first_line = description_html_break.pop(0)
                    second_line = description_html_break.pop(0)
                    description_html = "<h3 style='font-weight: 500;'>"+first_line+"</h3>"
                    description_html += "<h4>"+second_line+"</h4>"
                    description_html += "<br/>".join(description_html_break)
                else:
                    description_html = "<br/>".join(description_html_break)

                data_to_write.update({
                    'description': description_html,
                    'specs': attrs_ready
                })
                data_to_write.update({'short_description': 'short_description'})
                # data_to_write.update({'cost': json_data.get('cost')})
                # data_to_write.update({'list_price': json_data.get('list_price')})
                # data_to_write.update({'retail_price': json_data.get('retail_price')})
                data_to_write.update({'product_online': '1'})
                data_to_write.update({'status': '1'})
                data_to_write.update({'visibility': 'Catalog, Search'})
                data_to_write.update({'price': json_data.get('list_price')})
                data_to_write.update({'meta_title': name})
                data_to_write.update({'created_at': createDateTime})
                data_to_write.update({'updated_at': createDateTime})
                data_to_write.update({'quantity': json_data.get('quantity')})
                data_to_write.update({'qty': json_data.get('quantity')})
                data_to_write.update({'is_in_stock': '1'})
                data_to_write.update({'visibility': 'Catalog, Search'})
                print(data_to_write)


                ### write columns
                if i == 1:
                    with codecs.open('results_latest.csv', 'w+', encoding='utf-8') as f:
                        w = csv.writer(f, quoting=csv.QUOTE_ALL)
                        w.writerow(data_to_write.keys())
                    with codecs.open('errors.log', 'w+', encoding='utf-8') as f:
                        w = csv.writer(f, quoting=csv.QUOTE_ALL)
                        w.writerow(data_to_write.keys())

                with codecs.open('results_latest.csv', 'a+', encoding='utf-8') as f:
                    w = csv.writer(f, quoting=csv.QUOTE_ALL)
                    w.writerow(data_to_write.values())
            except Exception as e:
                print('got except on ',e)
                with codecs.open('errors.log', 'a+', encoding='utf-8') as f:
                   f.write("error on "+item_f['sku']+"\n")
                   f.close()
            i += 1

    write_to_csv()