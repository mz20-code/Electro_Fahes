"""Apply the researched photo references by product name, independent of row order."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def name_key(value):return ' '.join(value.casefold().split())

def apply_photos(products,root=ROOT):
    manifest=root/'data/photo_sources.json'
    if not manifest.exists():return 0
    references={name_key(entry['product_name']):entry for entry in json.loads(manifest.read_text(encoding='utf-8'))}
    applied=0
    for product in products:
        reference=references.get(name_key(product['name']))
        if not reference:continue
        asset=root/'static'/reference['filename']
        if not asset.is_file():raise FileNotFoundError(asset)
        product['image_path']=reference['filename'];product['image_kind']='photo'
        product['photo_source']={key:reference[key] for key in ('source_url','credit','match_type')}
        applied+=1
    return applied

if __name__=='__main__':
    file=ROOT/'data/products.json'
    products=json.loads(file.read_text(encoding='utf-8'))
    count=apply_photos(products)
    file.write_text(json.dumps(products,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Applied photo references:',count,'/',len(products))
