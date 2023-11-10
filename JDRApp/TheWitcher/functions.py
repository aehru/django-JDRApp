from dashboard.models import Character
from .models import CharacterInventory, Item


def is_htmx_request(request):
    return request.META.get("HTTP_HX_REQUEST") == "true"

def add_to_character_inventory(character:Character, ingredient:Item, quantity:int) -> None:
    try:
        inventory_entry = CharacterInventory.objects.get(character=character, item=ingredient)
        inventory_entry.quantity += quantity
        inventory_entry.save()
        print(f"{quantity} {ingredient} added to {character}'s inventory")
    except CharacterInventory.DoesNotExist:
        CharacterInventory.objects.create(character=character, item=ingredient, quantity=quantity)

def remove_from_character_inventory(character:Character, ingredient:Item, quantity:int) -> None:
    try:
        inventory_entry = CharacterInventory.objects.get(character=character, item=ingredient)
        if inventory_entry.quantity < quantity:
            raise ValueError(f"Can't remove {quantity} {ingredient} from {character}'s inventory: only {inventory_entry.quantity} in stock")
        inventory_entry.quantity -= quantity
        inventory_entry.save()
        print(f"{quantity} {ingredient} removed from {character}'s inventory")
    except CharacterInventory.DoesNotExist:
        pass