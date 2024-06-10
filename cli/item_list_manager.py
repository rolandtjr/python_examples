from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from collections import defaultdict

@dataclass
class Item:
    id: str
    name: str
    json_data_list: List[Dict[str, Any]] = field(default_factory=list)

    def add_json_data(self, json_data: Dict[str, Any]):
        if json_data not in self.json_data_list:
            self.json_data_list.append(json_data)

class ItemManager:
    def __init__(self):
        self.items_by_id: Dict[str, Item] = {}
        self.items_by_name: Dict[str, Item] = {}
        self.ordered_items: List[Item] = []

    def add_item(self, json_obj: Dict[str, Any]):
        item_id = json_obj['id']
        item_name = json_obj['name']
        if item_id not in self.items_by_id:
            item = Item(id=item_id, name=item_name)
            self.items_by_id[item_id] = item
            self.items_by_name[item_name] = item
            self.ordered_items.append(item)
        else:
            item = self.items_by_id[item_id]
        item.add_json_data(json_obj['data'])
        print(f"Item added or updated: {item}")

    def add_items_from_json_list(self, json_list: List[Dict[str, Any]]):
        for json_obj in json_list:
            self.add_item(json_obj)

    def remove_item_by_id(self, item_id: str):
        if item_id in self.items_by_id:
            item_to_remove = self.items_by_id.pop(item_id)
            self.ordered_items = [item for item in self.ordered_items if item.id != item_id]
            if item_to_remove.name in self.items_by_name:
                del self.items_by_name[item_to_remove.name]
            print(f"Item removed: {item_to_remove}")
        else:
            print(f"Item with ID {item_id} not found.")

    def search_by_name(self, name: str) -> Optional[Item]:
        return self.items_by_name.get(name)

    def search_by_id(self, item_id: str) -> Optional[Item]:
        return self.items_by_id.get(item_id)

    def get_all_items(self) -> List[Item]:
        return self.ordered_items

# Example usage:
item_manager = ItemManager()

# Initial JSON list
json_list_1 = [
    {"id": "1", "name": "Item1", "data": {"key1": "value1"}},
    {"id": "2", "name": "Item2", "data": {"key2": "value2"}},
    {"id": "1", "name": "Item1", "data": {"key1": "value1a"}}
]

# Add items from the first list
item_manager.add_items_from_json_list(json_list_1)
item_manager.add_items_from_json_list(json_list_1)

# Fetch more JSON objects
json_list_2 = [
    {"id": "3", "name": "Item3", "data": {"key3": "value3"}},
    {"id": "4", "name": "Item4", "data": {"key4": "value4"}}
]

# Add new items if they are not already in the manager
item_manager.add_items_from_json_list(json_list_2)
item_manager.add_items_from_json_list(json_list_2)

# Remove an item by ID
item_manager.remove_item_by_id("1")

# Get all items
all_items = item_manager.get_all_items()
for item in all_items:
    print(item)
