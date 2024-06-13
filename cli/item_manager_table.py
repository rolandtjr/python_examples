import pickle
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.text import Text
from rich.table import Table

@dataclass
class Item:
    id: str
    name: str
    json_data_list: List[Dict[str, Any]] = field(default_factory=list)
    data_type: str = 'new'

    def add_json_data(self, json_data: Dict[str, Any], data_type: str):
        if json_data not in self.json_data_list:
            self.json_data_list.append(json_data)
            self.data_type = data_type

class ItemManager:
    def __init__(self):
        self.items_by_id: Dict[str, Item] = {}
        self.items_by_name: Dict[str, Item] = {}
        self.ordered_items: List[Item] = []
        self.new_count: int = 0
        self.old_count: int = 0
        self.total_count: int = 0

    def add_item(self, json_obj: Dict[str, Any], data_type: str = 'new'):
        item_id = json_obj['id']
        item_name = json_obj['name']
        if item_id not in self.items_by_id:
            item = Item(id=item_id, name=item_name)
            self.items_by_id[item_id] = item
            self.items_by_name[item_name] = item
            self.ordered_items.append(item)
            self.total_count += 1
            if data_type == 'new':
                self.new_count += 1
            else:
                self.old_count += 1
        else:
            item = self.items_by_id[item_id]
            if item.data_type == 'new' and data_type == 'old':
                self.new_count -= 1
                self.old_count += 1
            elif item.data_type == 'old' and data_type == 'new':
                self.old_count -= 1
                self.new_count += 1
        item.add_json_data(json_obj['data'], data_type)
        print(f"Item added or updated: {item}")

    def add_items_from_json_list(self, json_list: List[Dict[str, Any]], data_type: str = 'new'):
        for json_obj in json_list:
            self.add_item(json_obj, data_type)

    def remove_item_by_id(self, item_id: str):
        if item_id in self.items_by_id:
            item_to_remove = self.items_by_id.pop(item_id)
            self.ordered_items = [item for item in self.ordered_items if item.id != item_id]
            if item_to_remove.name in self.items_by_name:
                del self.items_by_name[item_to_remove.name]
            self.total_count -= 1
            if item_to_remove.data_type == 'new':
                self.new_count -= 1
            else:
                self.old_count -= 1
            print(f"Item removed: {item_to_remove}")
        else:
            print(f"Item with ID {item_id} not found.")

    def remove_item_by_name(self, name: str):
        if name in self.items_by_name:
            item_to_remove = self.items_by_name.pop(name)
            self.ordered_items = [item for item in self.ordered_items if item.name != name]
            if item_to_remove.id in self.items_by_id:
                del self.items_by_id[item_to_remove.id]
            self.total_count -= 1
            if item_to_remove.data_type == 'new':
                self.new_count -= 1
            else:
                self.old_count -= 1
            print(f"Item removed: {item_to_remove}")
        else:
            print(f"Item with name {name} not found.")

    def search_by_name(self, name: str) -> Optional[Item]:
        return self.items_by_name.get(name)

    def search_by_id(self, item_id: str) -> Optional[Item]:
        return self.items_by_id.get(item_id)

    def get_all_items(self) -> List[Item]:
        return self.ordered_items

    def get_counts(self) -> Dict[str, int]:
        return {
            'new': self.new_count,
            'old': self.old_count,
            'total': self.total_count
        }

    def get_item_tuples(self) -> List[tuple]:
        tuples = []
        for item in self.ordered_items:
            color = "#D08770" if item.data_type == "new" else "#B48EAD"
            tuples.append((item.name, color))
        return tuples

    def print_items_as_table(self):
        console = Console()
        table = Table(title="Items")
        table.add_column("Item Name", justify="left", style="bold")

        for item_name, color in self.get_item_tuples():
            text = Text(item_name)
            text.stylize(color)
            table.add_row(text)

        console.print(table)

    def save_to_file(self, filename: str):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
        print(f"ItemManager saved to {filename}")

    @staticmethod
    def load_from_file(filename: str) -> 'ItemManager':
        with open(filename, 'rb') as f:
            item_manager = pickle.load(f)
        print(f"ItemManager loaded from {filename}")
        return item_manager

    @classmethod
    def from_json_list(cls, json_list: List[Dict[str, Any]]):
        item_manager = cls()
        item_manager.add_items_from_json_list(json_list)
        return item_manager

item_manager = ItemManager()

json_list_1 = [
    {"id": "1", "name": "Item1", "data": {"key1": "value1"}},
    {"id": "2", "name": "Item2", "data": {"key2": "value2"}},
    {"id": "1", "name": "Item1", "data": {"key1": "value1a"}}
]

item_manager.add_items_from_json_list(json_list_1, data_type='new')

json_list_2 = [
    {"id": "3", "name": "Item3", "data": {"key3": "value3"}},
    {"id": "4", "name": "Item4", "data": {"key4": "value4"}}
]

item_manager.add_items_from_json_list(json_list_2, data_type='old')

item_manager.print_items_as_table()

# Save to file
item_manager.save_to_file('item_manager.pkl')

# Load from file
loaded_item_manager = ItemManager.load_from_file('item_manager.pkl')

# Print loaded items as table
loaded_item_manager.print_items_as_table()
