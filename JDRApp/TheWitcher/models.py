from collections.abc import Iterable
from django.db import models
from django.contrib.auth.models import User
from dashboard.models import Character

ALCHEMICAL_SUBSTANCE = (
    ('vitriol', 'Vitriol'),
    ('rebis', 'Rebis'),
    ('caelum', 'Caelum'),
    ('hydragenum', 'Hydragenum'),
    ('vermillion', 'Vermillion'),
    ('sol', 'Sol'),
    ('fulgur', 'Fulgur'),
    ('aether', 'Aether'),
    ('quebrith', 'Quebrith'),
)

RECIPE_LEVEL = (
    ('novice', 'Novice'),
    ('journeyman', 'Journeyman'),
    ('master', 'Master'),
    ('grandmaster', 'Grandmaster'),
)

RECIPE_CATEGORY = (
    ('formula', 'Alchemy'),
    ('armor', 'Armor'),
    ('weapon', 'Weapon'),
)

class AlchemicalSubstance(models.Model):
    name = models.CharField(max_length=20, choices=ALCHEMICAL_SUBSTANCE)

    def __str__(self) -> str:
        return f"{self.name}"


class Item(models.Model):
    """
    Base class for all items
    - Items can be ingredients or equipment
    - Items can be crafted from recipes
    - Items can be found in the world
    """
    name = models.CharField(max_length=50, unique=True)
    difficulty = models.PositiveIntegerField()
    price = models.PositiveIntegerField() #in crowns
    weight = models.FloatField() #in kg
    location = models.CharField(max_length=80)

    substance = models.ForeignKey(AlchemicalSubstance, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        label:str = f"{self.name} - {self.weight}kg - {self.price} crowns - {self.location} - diff:{self.difficulty}"
        if self.substance:
            label += f" | {self.substance}"
        return label


class Recipe(models.Model):
    """
    Recipes are used to craft items
    """
    name = models.CharField(max_length=50, unique=True)
    level = models.CharField(max_length=20, choices=RECIPE_LEVEL)
    duration = models.PositiveIntegerField() #in minutes
    item_crafted = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="item_crafted_by_recipe") # if abstract requires : %(app_label)s_%(class)s_related
    category = models.CharField(max_length=20, choices=RECIPE_CATEGORY)

    def __str__(self) -> str:
        return f"{self.name} - {self.level} - {self.duration} minutes - {self.item_crafted.name}"

    # class Meta:
    #     abstract = True


class CraftRecipe(Recipe):
    """
    Recipes are used to craft items
    """
    ingredients = models.ManyToManyField(Item, through='CraftRecipeIngredient', related_name='ingredient_for_recipe')

    def clean(self) -> None:
        allowed_categories = ["armor", "weapon"]
        if self.category not in allowed_categories:
            raise ValueError(f"Category must be one of {allowed_categories}")
        return super().clean()


class CraftRecipeIngredient(models.Model):
    recipe = models.ForeignKey(CraftRecipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.quantity} {self.ingredient} in {self.recipe}"


class AlchemyRecipe(Recipe):
    vitriol = models.PositiveIntegerField(default=0)
    rebis = models.PositiveIntegerField(default=0)
    caelum = models.PositiveIntegerField(default=0)
    hydragenum = models.PositiveIntegerField(default=0)
    vermillion = models.PositiveIntegerField(default=0)
    sol = models.PositiveIntegerField(default=0)
    fulgur = models.PositiveIntegerField(default=0)
    aether = models.PositiveIntegerField(default=0)
    quebrith = models.PositiveIntegerField(default=0)

    def clean(self) -> None:
        if self.vitriol + self.rebis + self.caelum + self.hydragenum + self.vermillion + self.sol + self.fulgur + self.aether + self.quebrith <= 0:
            raise ValueError("The sum of all ingredients must be positive")
        return super().clean()
    
    def save(self) -> None:
        self.category = "formula"
        return super().save()

class Character(Character):
    reflex = models.PositiveIntegerField()
    dexterity = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.player}'s '{self.name}' from {self.campaign}"


class CharacterCharacteristic(models.Model):
    character = models.OneToOneField(Character, on_delete=models.CASCADE, primary_key=True)
    

class CharacterRecipe(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    # quantity = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.recipe.name} of {self.character.name}"


class CharacterInventory(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.quantity} {self.item} in {self.character}\'s inventory'


class ToastContent():
    title: str
    content: str
    type: str