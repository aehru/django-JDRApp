from django import forms
from .models import CharacterInventory
from .models import CharacterRecipe
from .models import Item, CraftRecipeIngredient, AlchemyRecipeIngredient

class InventoryAddForm(forms.ModelForm):
    class Meta:
        model = CharacterInventory
        fields = ["quantity", "item"]

class InventoryEditForm(forms.ModelForm):
    class Meta:
        model = CharacterInventory
        fields = ["quantity"]

class CharacterRecipeLearnForm(forms.ModelForm):
    class Meta:
        model = CharacterRecipe
        fields = ["recipe"]

class CraftRecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = CraftRecipeIngredient
        fields = ["ingredient", "quantity"]

class AlchemyRecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = AlchemyRecipeIngredient
        fields = ["substance", "quantity"]