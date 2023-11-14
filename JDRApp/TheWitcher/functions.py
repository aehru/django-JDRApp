from dashboard.models import Character
from .models import AlchemicalSubstance, CharacterInventory, Item
from django.db.models import Sum


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

def get_total_quantity_of_substance_in_character_inventory(character_id: int, substance_id: int) -> int:
    return CharacterInventory.objects.filter(character=character_id, item__substances=substance_id).aggregate(Sum('quantity'))['quantity__sum'] or 0

def remove_substances_from_character_inventory(character_id: int, s: AlchemicalSubstance, qty: int) -> None:
    """
    Remove enough items with substance in CharacterInventory to reach qty
    """
    inventory_entries = CharacterInventory.objects.filter(character=character_id, item__substance=s)
    total_qty = sum(entry.quantity for entry in inventory_entries)
    if total_qty < qty:
        raise ValueError(f"Not enough {s} in stock")
    remaining_qty = qty
    for entry in inventory_entries:
        if remaining_qty <= 0:
            break
        if entry.quantity <= remaining_qty:
            remaining_qty -= entry.quantity
            # entry.delete()
            entry.quantity = 0
            entry.save()
        else:
            entry.quantity -= remaining_qty
            entry.save()
            remaining_qty = 0