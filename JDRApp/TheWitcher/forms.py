from django import forms
from .models import CharacterInventory

class InventoryAddForm(forms.ModelForm):
    class Meta:
        model = CharacterInventory
        fields = ["quantity", "item"]

class InventoryEditForm(forms.ModelForm):
    class Meta:
        model = CharacterInventory
        fields = ["quantity"]