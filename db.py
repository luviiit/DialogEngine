import os
import re
from collections import defaultdict
from pymongo import MongoClient

import parse
import download_pages

def dropDB():
    client = MongoClient()
    client.drop_database("dialogengine")

def getDB():
    client = MongoClient()
    db = client.dialogengine
    return db

def getCollections():
    db = getDB()
    return db.collection_names()

def findProductFeatureValue(product, feature):
    print product
    db = getDB()
    colls = getCollections()
    for coll in colls:
        cursor = db[coll].find({"brand name": product})
        docs = [d for d in cursor]
        if len(docs) == 0:
            continue
        for doc in docs:
            try:
                if feature == "all_features":
                    return doc
                else:
                    return doc[feature]
            except:
                pass
    for coll in colls:
        cursor = db[coll].find({"brand": product})
        docs = [d for d in cursor]
        if len(docs) == 0:
            continue
        for doc in docs:
            try:
                if feature == "all_features":
                    return doc
                else:
                    return doc[feature]
            except:
                pass

def findProductsInRange(feature, r, category):
    db = getDB()
    products = db[category].find()
    out = []
    for p in products:
        val = re.findall(r'[\d\.]+', p[feature])[0]
        try:
            val = float(val)
        except:
            return "range specified for wrong feature"        
        if val >= float(r[0]) and val <= float(r[1]):
            out.append(p)
    return out

# def findAllFeaturesOfAProduct(product):
#     db = getDB()
#     colls = getCollections()
#     for coll in colls:
#         cursor = db[coll].

def insert_one(table, value):
    db = getDB()
    db[table].insert_one(value)

def dummy_insert():
    db = getDB()
    val = [{"price": "10$", "brand name": "bomadic"}, {"price": "20$", "brand": "belkin"}, {"price": "30$"}]
    insert_many("dummy", val)

def insert_many(table, values):
    db = getDB()
    print table
    print values
    db[table].insert_many(values)

def pushintofile(features):
    fname = 'ForSpellChecking.txt'
    if len(features) == 0:
        return
    features = '\n'.join(str(feature) for feature in features)
    features += '\n'
    with open(fname, 'a+') as f:
        f.write(features)

def get_all_brands(all_info):
    all_brands = []
    for info in all_info:
        try:
            brand = info["brand name"]
        except:
            try:
                brand = info["brand"]
            except:
                brand = None
        if brand:
            all_brands.append(brand)
    return all_brands

def dropStuff():
    dropDB()
    # fnames = ["categories", "brands", "features"]
    # fnames = [fname+"ForSpellChecking" for fname in fnames]
    # for fname in fnames:
    try:
        os.remove("ForSpellChecking.txt")
    except:
        pass

def dump():
    dropStuff()
    file_path = 'ProductId_Electronics.txt'
    categorized_pids = download_pages.process_product_pages(file_path)
    pushintofile([category for category in categorized_pids])

    for category in categorized_pids:
        all_info = []
        all_features = []
        for pid in categorized_pids[category]:
            info = parse.get_table_info('data/%s'%(pid))
            if not info:
                continue
            all_features += info.keys()
            all_info.append(info)
        features = set(all_features)
        pushintofile(features)
        all_brands = get_all_brands(all_info)
        pushintofile(all_brands)
        if len(all_info) == 0:
            continue
        insert_many(category, all_info)


if __name__ == "__main__":
    dump()