from collections.abc import Iterable
from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
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

ITEM_CATEGORY = (
    ("alchemy_ingredient", "Alchemy Ingredient"),
    ("craft_material", "Craft Material"),
    ("animals", "Animals"),
    ("alchemy_treatment", "Alchemy Treatment"),
    ("minerals", "Minerals"),
)

RECIPE_LEVEL = (
    ('novice', 'Novice'),
    ('journeyman', 'Journeyman'),
    ('master', 'Master'),
    ('grandmaster', 'Grandmaster'),
)

RECIPE_CATEGORY = (
    ('formula', 'Alchemy'),
    ('ingredient', 'Ingredient'),
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

    category = models.CharField(max_length=20, choices=ITEM_CATEGORY)
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
    difficulty = models.PositiveIntegerField()
    duration = models.PositiveIntegerField() #in minutes
    investment = models.PositiveIntegerField() #in crowns
    price = models.PositiveIntegerField() #in crowns
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
        allowed_categories = ["armor", "weapon", "ingredient"]
        if self.category not in allowed_categories:
            raise ValueError(f"Category must be one of {allowed_categories}")
        return super().clean()
    
    def __str__(self) -> str:
        if self.category == "ingredient":
            return f"Schéma de {self.name}"
        else:
            return super().__str__()


class CraftRecipeIngredient(models.Model):
    recipe = models.ForeignKey(CraftRecipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.quantity} {self.ingredient} in {self.recipe}"


class AlchemyRecipe(Recipe):
    """
    AlchemyRecipes are used to make potions
    """
    substances = models.ManyToManyField(AlchemicalSubstance, through='AlchemyRecipeIngredient', related_name='substance_for_recipe')

    # def clean(self) -> None:
    #     if self.vitriol + self.rebis + self.caelum + self.hydragenum + self.vermillion + self.sol + self.fulgur + self.aether + self.quebrith <= 0:
    #         raise ValueError("The sum of all ingredients must be positive")
    #     return super().clean()
    
    def save(self) -> None:
        self.category = "formula"
        return super().save()


class AlchemyRecipeIngredient(models.Model):
    recipe = models.ForeignKey(AlchemyRecipe, on_delete=models.CASCADE)
    substance = models.ForeignKey(AlchemicalSubstance, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.quantity} {self.substance} in {self.recipe}"


class Characteristic(models.Model):
    name = models.CharField(max_length=50, unique=True)
    tag = models.CharField(max_length=5, null=True)

    def __str__(self) -> str:
        return f"{self.tag}"


class Skill(models.Model):
    characteristic = models.ForeignKey(Characteristic, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self) -> str:
        return f"{self.name}"

class Character(Character):
    money = models.FloatField(default=0)
    xp = models.PositiveIntegerField(default=0)

    characteristics = models.ManyToManyField(Characteristic, through='CharacterCharacteristic', related_name='characteristic_for_character')
    skills = models.ManyToManyField(Skill, through='CharacterSkill', related_name='skill_for_character')
    
    def save(self) -> None:
        # When saving a new Character we need to create all the CharacterCharacteristics and CharacterSkills
        if not self.pk:
            with transaction.atomic():
                Char:Character = super().save()
                characteristics = Characteristic.objects.all()
                skills = Skill.objects.all()
                for characteristic in characteristics:
                    CharacterCharacteristic.objects.create(character=self, characteristic=characteristic)
                for skill in skills:
                    CharacterSkill.objects.create(character=self, skill=skill)
            return Char
        else:
            return super().save()


class CharacterCharacteristic(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    characteristic = models.ForeignKey(Characteristic, on_delete=models.CASCADE)
    
    value = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.characteristic.tag} | {self.value}"

class CharacterSkill(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    value = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.skill.name} | {self.value}"
    

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