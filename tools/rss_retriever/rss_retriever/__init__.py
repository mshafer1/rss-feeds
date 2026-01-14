import json
import pathlib
import re
import typing

import markupsafe
import requests
import xmltodict

from rss_retriever import _datastore

def _merge_data_with_stored(data: dict, uri: str, items_path: str, cache_dir: pathlib.Path, max_size: int=-1, item_id_key: typing.Optional[str]=None) -> dict:
    # assumptions:
    # - new data is sorted newest to oldest
    # - old data is sorted newest to oldest
    # - old data may have items in new data
    # - since both are sorted newest to oldest, we can just prepend new items until we hit an old one
    name = markupsafe.escape(re.sub(r"[^a-zA-Z0-9\.]", "_", uri))

    list_path = items_path.split("/")

    working_point = data
    for key in list_path[:-1]:
        working_point = working_point.get(key, {})
    items = working_point.get(list_path[-1], [])
    with _datastore.DataStore(name, cache_path=cache_dir) as store:
        stored_working_point = store
        print("Retrieving stored items from cache under:", '/'.join(list_path))
        for key in list_path[:-1]:
            stored_working_point = stored_working_point.get(key, {})
        stored_items = stored_working_point.get(list_path[-1], [])
        print(f"Has {len(stored_items)} items previously stored")
        # special case, if items is one, make it a list
        if isinstance(items, dict):
            items = [items]
        # merge items
        if not stored_items:
            all_items = items
        else:
            newest_old_items = stored_items[0]
            all_items = []
            for i, item in enumerate(items):
                comparison = item == newest_old_items
                if item_id_key:
                    comparison = item.get(item_id_key) == newest_old_items.get(item_id_key)
                if comparison:
                    print("Found duplicate at new item index", i)
                    break
                print("Adding new item from index", i)
                all_items.append(item)
            print("Appending", len(stored_items), "item(s)")
            all_items.extend(stored_items)

        # enforce max size
        if max_size > 0:
            all_items = all_items[: max_size + 1]

        # bring in the current version of all other fields
        store.clear()
        store.update(data)
        stored_working_point = store
        for key in list_path[:-1]:
            stored_working_point = stored_working_point.get(key, {})
        stored_working_point[list_path[-1]] = all_items
    return store

def fetch_feed(uri: str, items_path: str, return_json: bool = False, cache_dir: typing.Optional[pathlib.Path]=None, max_size: int=-1, item_id_key: typing.Optional[str]=None):
    r = requests.get(uri, timeout=10)
    r.raise_for_status()
    data = r.text

    cache_dir = cache_dir or pathlib.Path.cwd()

    converted_data = xmltodict.parse(data)
    converted_data = _merge_data_with_stored(converted_data, uri, cache_dir=cache_dir, max_size=max_size, items_path=items_path, item_id_key=item_id_key)

    if return_json:
        result = json.dumps(converted_data)
    else:
        result = xmltodict.unparse(converted_data)

    return result
