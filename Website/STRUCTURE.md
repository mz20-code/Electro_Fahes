# TechVerse structure

- app.py: Flask routes, accounts, guide, technician directory/application, advertising payments, admin.
- inventory.py: private inventory, validated photos, CSV import/export, snapshots.
- i18n.py: English/Arabic interface strings.
- data/products.json: seed inventory (only adds missing IDs; does not overwrite host edits).
- data/PRODUCTS.csv: initial UTF-8 CSV example.
- data/catalogs.json: active exact-model catalogs.
- data/catalogs_additions.json: reviewed additional manual scopes retained by generator.
- static/images: supplied and sourced product/model reference photos.
- static/manuals: original available PDF manuals.
- templates, static/css, static/js: bilingual website interface.
- instance: private runtime database, products.csv snapshot, uploaded product_images, session key; never distribute this directory.
- tests: behavioral regression checks.
- ../Reports: catalog comparison and guidance review.

R5: /membership is the technician directory; /membership/apply is its private application/payment flow. /technicians redirects to /membership. Videos is empty. The public homepage redirects signed-in accounts to Shop.
