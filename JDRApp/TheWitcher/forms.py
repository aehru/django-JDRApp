from django import forms
from .models import CharacterInventory
from .models import CharacterRecipe

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