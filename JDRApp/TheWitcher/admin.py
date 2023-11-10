from django.contrib import admin

from .models import AlchemicalSubstance, AlchemyRecipe
from .models import Character, CharacterInventory, CharacterRecipe, Item, CraftRecipe, CraftRecipeIngredient

admin.site.register(Character)
admin.site.register(AlchemicalSubstance)
admin.site.register(Item)
admin.site.register(CraftRecipe)
admin.site.register(CraftRecipeIngredient)
admin.site.register(AlchemyRecipe)
admin.site.register(CharacterInventory)
admin.site.register(CharacterRecipe)