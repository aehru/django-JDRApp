from typing import Any
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from .forms import InventoryAddForm, InventoryEditForm
from .functions import is_htmx_request, add_to_character_inventory, remove_from_character_inventory
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from dashboard.models import Campaign
from .models import AlchemyRecipe, Character, CharacterInventory, CharacterRecipe, Item, Recipe, CraftRecipe, CraftRecipeIngredient

class CampaignCreateView(CreateView):
    model = Campaign
    fields = ["name", "universe"]

class CharacterCreateView(CreateView):
    model = Character
    fields = ["name", "reflex", "dexterity"]

class IngredientListView(ListView):
    model = Item
    template_name = "TheWitcher/ingredient_list.html"
    context_object_name = "ingredients"

class CharacterInventoryListView(ListView):
    model = CharacterInventory
    template_name = "TheWitcher/character_inventory_list.html"
    context_object_name = "inventory"

    def get_template_names(self) -> list[str]:
        if is_htmx_request(self.request):
            return ["TheWitcher/includes/character_inventory_list.hx.html"]
        else:
            return super().get_template_names()
        
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["character_pk"] = self.kwargs["pk"]
        return context

# class AddToInventoryView(CreateView):
#     model = CharacterInventory
#     form_class = InventoryAddForm
#     template_name = "TheWitcher/add_to_inventory.html"

class AddToInventoryView(FormView):
    template_name = "TheWitcher/add_to_inventory.html"
    form_class = InventoryAddForm

    def get_template_names(self) -> list[str]:
        if is_htmx_request(self.request):
            return ["TheWitcher/includes/add_to_inventory.hx.html"]
        else:
            return super().get_template_names()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        character_id = self.kwargs["character_pk"]
        context["character"] = Character.objects.get(pk=character_id)
        context["ingredients"] = Item.objects.all()

        # Add the current quantity of each ingredient in the character's inventory
        character_inventory = CharacterInventory.objects.filter(character=character_id)
        context['inventory_quantities'] = {entry.item.id: entry.quantity for entry in character_inventory}

        return context
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        character_id = self.kwargs["character_pk"]
        character:Character = Character.objects.get(pk=character_id)

        ingredient_id = self.request.POST.get("add_ingredient")
        ingredient:Item = Item.objects.get(pk=ingredient_id)
        quantity:int = int(self.request.POST.get("quantity_" + ingredient_id))
        
        if quantity < 0:
            raise ValueError("Quantity must be positive")
        
        add_to_character_inventory(character, ingredient, quantity)

        r = redirect(request.path)
        
        r["HX-Trigger"] = "character-inventory-refresh"
        return r

class EditInventoryEntryView(UpdateView):
    model = CharacterInventory
    form_class = InventoryEditForm
    template_name = "TheWitcher/edit_inventory_entry.html"


class CharacterRecipeListView(ListView):
    """
    List of recipes known by a character
    """
    model = CharacterRecipe
    context_object_name = "recipes"

    # def get_template_names(self) -> list[str]:
    #     if is_htmx_request(self.request):
    #         return ["TheWitcher/includes/characterrecipe_list.hx.html"]
    #     else:
    #         return super().get_template_names()
        
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        character_id = self.kwargs["character_pk"]
        crafted_items = {}
        for item in self.object_list:
            item_crafted:CharacterInventory = CharacterInventory.objects.filter(character=character_id, item=item.recipe.item_crafted).first()
            crafted_items[item.recipe.item_crafted.pk] = item_crafted.quantity if item_crafted else 0
        # context["crafted_item"] = CharacterInventory.objects.filter(character=character_id, item=self.item_crafted).first()
        context["crafted_items_inventory_quantities"] = crafted_items
        context["character_pk"] = character_id
        return context


class CharacterRecipeDetailView(DetailView):
    """
    List of ingredients needed to craft a recipe but with the quantity of each ingredient in the character's inventory
    """
    model = Recipe
    context_object_name = "recipe"
    template_name = "TheWitcher/craftrecipe_detail.html"

    def get_template_names(self) -> list[str]:
        if is_htmx_request(self.request):
            return ["TheWitcher/includes/recipe_card.hx.html"]
        else:
            return super().get_template_names()
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        character_id = self.kwargs["character_pk"]
        crafted_items = {}
        R:Recipe = self.get_object()
        item_crafted:CharacterInventory = CharacterInventory.objects.filter(character=character_id, item=R.item_crafted).first()
        crafted_items[item_crafted.pk] = item_crafted.quantity
        context["crafted_items_inventory_quantities"] = crafted_items
        context["character_pk"] = character_id

        return context

class CraftRecipeIngredientListView(DetailView):
    """
    List of ingredients needed to craft a recipe
    """
    model = Recipe
    context_object_name = "recipe"
    template_name = "TheWitcher/craftrecipe_ingredients_list.html"

    def get_template_between_craft_or_alchemy(self) -> str:
        path:str = "TheWitcher/"
        ext:str = ".html"
        if is_htmx_request(self.request):
            path += "includes/"
            ext = ".hx.html"

        if self.object.category == "formula":
            return f"{path}alchemyrecipe_ingredients_list{ext}"
        else:
            return f"{path}craftrecipe_ingredients_list{ext}"

    def get_template_names(self) -> list[str]:
        return [self.get_template_between_craft_or_alchemy()]
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        r:Recipe = self.get_object()
        if r.category == "formula":
            context["ingredients"] = None
        else:
            context["ingredients"] = CraftRecipeIngredient.objects.filter(recipe=self.get_object())
        
        return context

class CharacterRecipeIngredientListView(ListView):
    """
    List of ingredients needed to craft a recipe
    """
    model = CraftRecipeIngredient
    template_name = "TheWitcher/recipe_ingredient_list.html"
    context_object_name = "ingredients"

    def get_template_names(self) -> list[str]:
        if is_htmx_request(self.request):
            return ["TheWitcher/includes/recipe_ingredient_list.hx.html"]
        else:
            return super().get_template_names()
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        character_id = self.kwargs["character_pk"]
        recipe_id = self.kwargs["recipe_pk"]
        character:Character = Character.objects.get(pk=character_id)
        recipe:Recipe = Recipe.objects.get(pk=recipe_id)
        context["character"] = character
        context["recipe"] = recipe
        ingredient_of_recipe = CraftRecipeIngredient.objects.filter(recipe=recipe_id)
        inventory_quantities = {entry.item.id: entry.quantity for entry in CharacterInventory.objects.all().filter(character=character)}
        can_craft = True

        for ior in ingredient_of_recipe:
            if ior.ingredient.id not in inventory_quantities or inventory_quantities[ior.ingredient.id] < ior.quantity:
                can_craft = False
                break

        context["can_craft"] = can_craft
        return context


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "TheWitcher/craftrecipe_detail.html"

# @method_decorator(login_required, name="dispatch")
class UseRecipeView(FormView):
    template_name = "TheWitcher/use_recipe.html"

    def get_template_names(self) -> list[str]:
        if is_htmx_request(self.request):
            return ["TheWitcher/includes/recipe_card.hx.html"]
        else:
            return super().get_template_names()

    # def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
    #     context = super().get_context_data(**kwargs)
    #     character_id = self.kwargs["character_pk"]
    #     context["character"] = Character.objects.get(pk=character_id)
    #     context["ingredients"] = Ingredient.objects.all()

    #     # Add the current quantity of each ingredient in the character's inventory
    #     character_inventory = CharacterInventory.objects.filter(character=character_id)
    #     context['inventory_quantities'] = {entry.ingredient.id: entry.quantity for entry in character_inventory}

    #     return context
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        character_id = self.kwargs["character_pk"]
        character:Character = Character.objects.get(pk=character_id)

        recipe_id = self.kwargs["recipe_pk"]
        recipe:Recipe = Recipe.objects.get(pk=recipe_id)

        if not CharacterRecipe.objects.filter(character=character_id, recipe=recipe_id).exists():
            raise ValueError(f"Can't use {recipe} : {character} doesn't know it")

        #ToDo : it's different if it's a potion or an item
        if recipe.category == "alchemy":
            print("alchemy")
        else:
            recipe_ingredients = CraftRecipeIngredient.objects.filter(recipe=recipe_id)
            errors = []
            try:
                with transaction.atomic():
                    for recipe_ingredient in recipe_ingredients:
                        ingredient = recipe_ingredient.ingredient
                        quantity = recipe_ingredient.quantity
                        try:
                            remove_from_character_inventory(character, ingredient, quantity)
                        except:
                            msg:str = f"Can't use {recipe} : not enough {ingredient} in stock"
                            errors.append(msg)
                            raise ValueError(msg)
                    
                    add_to_character_inventory(character, recipe.item_crafted, 1)
            except ValueError as e:
                # return a toast template ?
                # r = redirect(request.path)
                if is_htmx_request(request):
                    # r = JsonResponse({"toast": {"title": "Success", "content": f"{recipe} successfully used", "type": "success"}})
                    return render(request, "TheWitcher/includes/toast.hx.html", {"title": "Success", "content": f"{recipe} successfully used", "type": "success"})
                else:
                    return render(request, "TheWitcher/use_recipe.html", {"character": character, "recipe": recipe})
        
        # r["HX-Trigger"] = "character-inventory-refresh"
        # return r
        return HttpResponseRedirect(reverse_lazy("TheWitcher:character-recipe-list", kwargs={"character_pk": character_id, "recipe_pk": recipe_id}))