from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import Characteristic, Recipe, Skill
from .models import AlchemicalSubstance, AlchemyRecipe, AlchemyRecipeIngredient, CharacterCharacteristic, CharacterSkill
from .models import Character, CharacterInventory, CharacterRecipe, Item, CraftRecipe, CraftRecipeIngredient

admin.site.register(Characteristic)
admin.site.register(Skill)
admin.site.register(AlchemicalSubstance)

#https://gist.github.com/Grokzen/a64321dd69339c42a184
class CraftRecipeIngredientAdmin(admin.ModelAdmin):
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "ingredients":
            kwargs["queryset"] = CraftRecipe.objects.filter(category="armor") #filter(owner=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

class CraftRecipeAdminForm(forms.ModelForm):
    class Meta:
        model = CraftRecipe
        fields = '__all__'
        widgets = {
            'ingredients': FilteredSelectMultiple("ingredients", False),
        }
    
    craft_recipe_ingredients = forms.ModelMultipleChoiceField(
        queryset=Item.objects.all(), #.filter(category="armor"),
        required=False,
        widget=FilteredSelectMultiple("ingredients", False),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['craft_recipe_ingredients'].initial = self.instance.ingredients.all()
    
    def save_m2m(self):
        self.instance.ingredients.set(self.cleaned_data['craft_recipe_ingredients'])

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            self.save_m2m()
        return instance
    
class CraftRecipeAdmin(admin.ModelAdmin):
    form = CraftRecipeAdminForm
    filter_horizontal = ('ingredients',)

admin.site.register(Item)
admin.site.register(Recipe)
# admin.site.register(CraftRecipe, CraftRecipeAdmin)
admin.site.register(CraftRecipe)

admin.site.register(CraftRecipeIngredient)
admin.site.register(AlchemyRecipe)
admin.site.register(AlchemyRecipeIngredient)

admin.site.register(Character)
admin.site.register(CharacterInventory)
admin.site.register(CharacterRecipe)
admin.site.register(CharacterCharacteristic)
admin.site.register(CharacterSkill)