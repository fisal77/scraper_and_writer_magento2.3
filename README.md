**Python Web Scraper by Selenium library, Import to Magento2 storefront**

Python Web Scraper by Selenium library, Import product details from external website to Magento2 storefront website

***Python Web Scraper steps:***

1 - Run python web scarper script from my local environment for testing (You can install the script anywhere as schedule task as cron in Linux). You can see the output now.

2 - Login to external website and start scraping product details data from it such as name, price, description, image url, etc... (each product has unique url page based on it's number) as you can see in output.

3 - After finished scraping all product details (For testing here are 5 products only and I interrupt it to run next script "SaveToCsvTable.py") this uses output from previous script, reads data files and prepares product details, html etc. and then produces csv table file used for Magento2 products importer to store front website.

4 - After scrapped data successfully for products into results_latest.csv table file, then import it to Magento2 storefront (importer) and you will see the new products with category.