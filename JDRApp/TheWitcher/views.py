import json
from typing import Any
from django import forms
from django.db.models.query import QuerySet, Q
from django.forms import formset_factory, inlineformset_factory
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from .forms import AlchemyRecipeIngredientForm, CharacterRecipeLearnForm, CraftRecipeIngredientForm, InventoryAddForm, InventoryEditForm
from .functions import get_total_quantity_of_substance_in_character_inventory, is_htmx_request, add_to_character_inventory, remove_from_character_inventory, remove_substances_from_character_inventory
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from dashboard.models import Campaign
from .models import AlchemyRecipe, AlchemyRecipeIngredient, Character, CharacterCharacteristic, CharacterInventory, CharacterRecipe, CharacterSkill, Item, Recipe, CraftRecipe, CraftRecipeIngredient

from django.contrib.auth.forms import UserCreationForm
class AuthenticationView(FormView):
    template_name = "TheWitcher/login.html"
    form_class = UserCreationForm

class CampaignCreateView(CreateView):
    model = Campaign
    fields = ["name", "universe"]


class CampaignDetailView(DetailView):
    model = Campaign
    context_object_name = "campaign"
    template_name = "TheWitcher/campaign_detail.html"

class RecipeListView(ListView):
    model = Recipe
    context_object_name = "recipes"

class RecipeToLearnListView(ListView):
    model = Recipe
    context_object_name = "recipes"
    template_name = "TheWitcher/recipe_list.html"

    def get_template_names(self) -> list[str]:
        if is_htmx_request(self.request):
            return ["TheWitcher/includes/recipe_list.hx.html"]
        else:
            return super().get_template_names()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        character = get_object_or_404(Character, pk=self.kwargs["character_pk"])
        character_recipes = CharacterRecipe.objects.filter(character=character).values_list("recipe", flat=True)
        if "category" in self.kwargs:
            context["recipes"] = Recipe.objects.filter(category=self.kwargs["category"]).exclude(pk__in=character_recipes)
        else:
            context["recipes"] = Recipe.objects.exclude(pk__in=character_recipes)
        context["character_pk"] = self.kwargs["character_pk"]
        context["learn"] = True
        return context

class LearnRecipe(FormView):
    template_name = "TheWitcher/recipe_list.html"
    form_class = InventoryAddForm

    def get_template_names(self) -> list[str]:
        if is_htmx_request(self.request):
            return ["TheWitcher/includes/recipe_list.hx.html"]
        else:
            return super().get_template_names()
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["recipes"] = Recipe.objects.all()
        context["character_pk"] = self.kwargs["character_pk"]
        return context
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        RecipeToLearn = get_object_or_404(Recipe, pk=self.kwargs["recipe_pk"])
        character = get_object_or_404(Character, pk=self.kwargs["character_pk"])
        if CharacterRecipe.objects.filter(character=character, recipe=RecipeToLearn).exists():
            raise ValueError(f"{character} already knows {RecipeToLearn}")
        
        CharacterRecipe.objects.create(character=character, recipe=RecipeToLearn)
        r = HttpResponseRedirect(reverse_lazy("TheWitcher:character-recipes-to-learn", kwargs={"character_pk": self.kwargs["character_pk"]}))        
        r["HX-Trigger"] = "character-known-recipes-refresh"
        return r


class CraftRecipeCreateView(CreateView):
    model = CraftRecipe
    fields = [
        "name", "level", "difficulty", "duration", 
        "investment", "price", "item_crafted", "category"
        ]
    widgets = {
        "name": forms.TextInput(attrs={"class": "form-control"}),
        "level": forms.NumberInput(attrs={"class": "form-control"}),
    }

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        ingredients_formset = formset_factory(CraftRecipeIngredientForm)(self.request.POST or None) #formset_factory(CraftRecipe, CraftRecipeIngredient, fields=("ingredient", "quantity"), extra=1)
        context["ingredients_formset"] = ingredients_formset
        return context
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        context = self.get_context_data()
        ingredients = context["ingredients_formset"]
        with transaction.atomic():
            self.object = form.save()
            if ingredients.is_valid():
                for f in ingredients:
                    i = f.save(commit=False)
                    i.recipe = self.object
                    i.save()

        return super().form_valid(form)


class ALchemyRecipeCreateView(CreateView):
    model = AlchemyRecipe
    fields = [
        "name", "level", "difficulty", "duration", 
        "investment", "price", "item_crafted"
        ]
    widgets = {
    }

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        ingredients_formset = formset_factory(AlchemyRecipeIngredientForm)(self.request.POST or None)
        context["ingredients_formset"] = ingredients_formset
        return context
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        context = self.get_context_data()
        ingredients = context["ingredients_formset"]
        with transaction.atomic():
            if ingredients.is_valid():
                ingredients_data = ingredients.cleaned_data
                ingredients_list = [ingredient['substance'] for ingredient in ingredients_data]
                if len(ingredients_list) != len(set(ingredients_list)):
                    form.add_error(None, "Duplicate ingredients are not allowed.")
                    return self.form_invalid(form)
                self.object = form.save()
                for f in ingredients:
                    i = f.save(commit=False)
                    i.recipe = self.object
                    i.save()

        return super().form_valid(form)

    def clean_category(self) -> str:
        return "formula"

class CharacterCreateView(CreateView):
    model = Character
    fields = ["name", "money", "xp"]


class CharacterUpdateMoneyView(View):
    model = Character
    # fields = ["money"]
    template_name = "TheWitcher/includes/character_money_form.hx.html"

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        char:Character = get_object_or_404(Character, pk=kwargs["pk"])
        context = {"object": char }
        return render(request, self.template_name, context=context)
                      
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if 'money' in request.POST and 'operation' in request.POST:
            char:Character = get_object_or_404(Character, pk=kwargs["pk"])
            if request.POST.get("operation") == "add":  # Check if operation is "add"
                char.money += float(request.POST.get("money"))
            else:
                char.money -= float(request.POST.get("money"))
            char.save()

        return HttpResponseRedirect(reverse_lazy("TheWitcher:character-update-money", kwargs={"pk": self.kwargs["pk"]}))


class CharacterUpdateXPView(View):
    model = Character
    # fields = ["money"]
    template_name = "TheWitcher/includes/character_xp_form.hx.html"

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        char:Character = get_object_or_404(Character, pk=kwargs["pk"])
        context = {"object": char }
        return render(request, self.template_name, context=context)
                      
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if 'xp' in request.POST and 'operation' in request.POST:
            char:Character = get_object_or_404(Character, pk=kwargs["pk"])
            if request.POST.get("operation") == "add":  # Check if operation is "add"
                char.xp += float(request.POST.get("xp"))
            else:
                char.xp -= float(request.POST.get("xp"))
            char.save()

        return HttpResponseRedirect(reverse_lazy("TheWitcher:character-update-xp", kwargs={"pk": self.kwargs["pk"]}))


class CharacterDetailView(DetailView):
    model = Character
    context_object_name = "character"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["character_pk"] = self.kwargs["pk"]
        return context

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
        context["character"] = get_object_or_404(Character, pk=self.kwargs["pk"])
        return context

# class AddToInventoryView(CreateView):
#     model = CharacterInventory
#     form_class = InventoryAddForm
#     template_name = "TheWitcher/add_to_inventory.html"

class AddToInventoryView(FormView):
    template_name = "TheWitcher/add_to_inventory.html"
    form_class = CharacterRecipeLearnForm

    def get_template_names(self) -> list[str]:
        if is_htmx_request(self.request):
            return ["TheWitcher/includes/add_to_inventory.hx.html"]
        else:
            return super().get_template_names()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        character_id = self.kwargs["character_pk"]
        context["character"] = Character.objects.get(pk=character_id)
        items = Item.objects.all()
        if self.request.POST.get("search"):
            s = self.request.POST.get("search")
            context["search"] = s
            items = items.filter(Q(name__icontains=s))
        context["ingredients"] = items

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

        r = super().post(request, *args, **kwargs)
        # r = redirect(request.path)
        
        r["HX-Trigger"] = "character-inventory-refresh"
        return r


class ItemsToAddToInventoryListView(ListView):
    model = Item
    context_object_name = "ingredients"

    def get_template_names(self) -> list[str]:
        if is_htmx_request(self.request):
            return [ "TheWitcher/includes/ingredients_table.hx.html" ]
        else:
            return super().get_template_names()
        
    def get_queryset(self) -> QuerySet[Any]:
        q = super().get_queryset()
        if self.request.GET.get("ingredient-to-search"):
            q = q.filter(Q(name__icontains=self.request.GET.get("ingredient-to-search")))
        
        return q

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

    def get_template_names(self) -> list[str]:
        if is_htmx_request(self.request):
            return ["TheWitcher/includes/characterrecipe_list.hx.html"]
        else:
            return super().get_template_names()
        
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        character_id = self.kwargs["character_pk"]
        context["recipes"] = CharacterRecipe.objects.filter(character=character_id)
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
        crafted_items[R.item_crafted.pk] = item_crafted.quantity
        context["crafted_items_inventory_quantities"] = crafted_items
        context["character_pk"] = character_id

        return context


class CharacterCharacteristicListView(ListView):
    model = Character
    template_name = "TheWitcher/charactercharacteristic_list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["characteristics"] = CharacterCharacteristic.objects.filter(character=self.kwargs["pk"])
        context["character_pk"] = self.kwargs["pk"]
        return context


class CharacterSkillListView(ListView):
    model = Character
    template_name = "TheWitcher/characterskill_list.html"
    # context_object_name = "skills"

    def get_template_names(self) -> list[str]:
        if is_htmx_request(self.request):
            return ["TheWitcher/includes/characterskill_list.hx.html"]
        else:
            return super().get_template_names()
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["skills"] = CharacterSkill.objects.filter(character=self.kwargs["pk"])
        fields = ["characteristic_id", "value"]
        context["character_characteristics"] = CharacterCharacteristic.objects.filter(character=self.kwargs["pk"]).values_list(*fields)
        return context


class CharacterUpdateView(UpdateView):
    model = Character
    fields = ["money", "xp"]
    template_name = "TheWitcher/character_update.html"

    def get_success_url(self) -> str:
        return reverse_lazy("TheWitcher:character-detail", kwargs={"pk": self.kwargs["pk"]})

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
            context["ingredients"] = AlchemyRecipeIngredient.objects.filter(recipe=self.get_object())
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

        if recipe.category == "formula":
            recipe_substances = AlchemyRecipeIngredient.objects.filter(recipe=recipe_id)
            try:
                with transaction.atomic():
                    for s in recipe_substances:
                        # qty:int = get_total_quantity_of_substance_in_character_inventory(character_id, s.id)
                        # if qty < 1:
                        #     raise ValueError(f"Can't use {recipe} : {character} doesn't have {s}")
                        remove_substances_from_character_inventory(character_id, s.substance, s.quantity)
                    add_to_character_inventory(character, recipe.item_crafted, 1)
            except:
                msg:str = f"Can't use {recipe} : not enough {s} in stock"
                raise ValueError(msg)
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
                #ToDo properly
                return redirect(request.path)
        
        # r["HX-Trigger"] = "character-inventory-refresh"
        # return r
        return HttpResponseRedirect(reverse_lazy("TheWitcher:character-recipe-detail", kwargs={"character_pk": character_id, "pk": recipe_id}))