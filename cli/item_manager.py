#!/usr/bin/env python3
""" This is a simple example of a class that manages items. """
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Item:
    """ This is a simple class that represents an item. """
    id: str
    name: str
    json_data: Dict[str, Any]

class ItemManager:
    """ This is a simple class that manages items. """
    def __init__(self):
        self.items_by_id: Dict[str, Item] = {}
        self.ordered_items: List[Item] = []

    def add_item(self, item: Item):
        if item.id not in self.items_by_id:
            self.items_by_id[item.id] = item
            self.ordered_items.append(item)
            print(f"Item added: {item}")
        else:
            print(f"Item with ID {item.id} already exists.")

    def add_items_from_json_list(self, json_list: List[Dict[str, Any]]):
        for json_obj in json_list:
            item = Item(id=json_obj['id'], name=json_obj['name'], json_data=json_obj)
            self.add_item(item)

    def remove_item_by_id(self, item_id: str):
        if item_id in self.items_by_id:
            item_to_remove = self.items_by_id.pop(item_id)
            self.ordered_items = [item for item in self.ordered_items if item.id != item_id]
            print(f"Item removed: {item_to_remove}")
        else:
            print(f"Item with ID {item_id} not found.")

    def fetch_more_items_and_add(self, json_list: List[Dict[str, Any]]):
        for json_obj in json_list:
            item = Item(id=json_obj['id'], name=json_obj['name'], json_data=json_obj)
            if item.id not in self.items_by_id:
                self.add_item(item)

    def get_all_items(self) -> List[Item]:
        return self.ordered_items


def main():
    item_manager = ItemManager()

    json_list_1 = [
        {"id": "1", "name": "Item1", "data": {"key1": "value1"}},
        {"id": "2", "name": "Item2", "data": {"key2": "value2"}},
        {"id": "1", "name": "Item1", "data": {"key1": "value1"}}
    ]

    item_manager.add_items_from_json_list(json_list_1)

    json_list_2 = [
        {"id": "3", "name": "Item3", "data": {"key3": "value3"}},
        {"id": "4", "name": "Item4", "data": {"key4": "value4"}}
    ]

    item_manager.fetch_more_items_and_add(json_list_2)

    item_manager.remove_item_by_id("2")

    all_items = item_manager.get_all_items()
    for item in all_items:
        print(item)

if __name__ == "__main__":
    main()