from django.contrib import admin

from .models import Characteristic, Skill
from .models import AlchemicalSubstance, AlchemyRecipe, AlchemyRecipeIngredient, CharacterCharacteristic, CharacterSkill
from .models import Character, CharacterInventory, CharacterRecipe, Item, CraftRecipe, CraftRecipeIngredient

admin.site.register(Characteristic)
admin.site.register(Skill)
admin.site.register(AlchemicalSubstance)
admin.site.register(Item)

admin.site.register(CraftRecipe)
admin.site.register(CraftRecipeIngredient)
admin.site.register(AlchemyRecipe)
admin.site.register(AlchemyRecipeIngredient)

admin.site.register(Character)
admin.site.register(CharacterInventory)
admin.site.register(CharacterRecipe)
admin.site.register(CharacterCharacteristic)
admin.site.register(CharacterSkill)