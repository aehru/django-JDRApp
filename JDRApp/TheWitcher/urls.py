from django.urls import path
from TheWitcher.views import ALchemyRecipeCreateView, AuthenticationView, CampaignCreateView, CampaignDetailView, CharacterCreateView, CharacterDetailView, CharacterInventoryListView, ItemsToAddToInventoryListView
from TheWitcher.views import AddToInventoryView, EditInventoryEntryView
from TheWitcher.views import IngredientListView
from TheWitcher.views import CharacterRecipeListView, CharacterRecipeDetailView, CharacterRecipeIngredientListView, UseRecipeView
from TheWitcher.views import CharacterCharacteristicListView, CharacterSkillListView
from TheWitcher.views import CharacterUpdateView, CharacterUpdateMoneyView, CharacterUpdateXPView
from TheWitcher.views import CraftRecipeIngredientListView, CraftRecipeCreateView
from TheWitcher.views import RecipeListView, RecipeDetailView, LearnRecipe, RecipeToLearnListView

app_name = 'TheWitcher'
urlpatterns = [

    path("campaign/<int:pk>", CampaignDetailView.as_view(), name="campaign-detail"),

    # path("campaigns/add", CampaignCreateView.as_view(), name="campaign-add"),
    path("campaigns/<int:pk>/characters/add", CharacterCreateView.as_view(), name="character-add"),
    path("ingredients", IngredientListView.as_view(), name="ingredient-list"),
    path("ingredients/to-add", ItemsToAddToInventoryListView.as_view(), name="ingredient-to-add-list"),
    path("characters/<int:pk>", CharacterDetailView.as_view(), name="character-detail"),
    path("characters/<int:pk>/inventory", CharacterInventoryListView.as_view(), name="character-inventory"),
    path("characters/<int:character_pk>/inventory/add", AddToInventoryView.as_view(), name="add-to-inventory"),
    path("characters/<int:character_pk>/inventory/edit/<int:pk>", EditInventoryEntryView.as_view(), name="edit-inventory-entry"),
    path("characters/<int:pk>/characteristic", CharacterCharacteristicListView.as_view(), name="character-characteristic"),
    path("characters/<int:pk>/skills", CharacterSkillListView.as_view(), name="character-skill"),
    path("characters/<int:pk>/update", CharacterUpdateView.as_view(), name="character-update"),
    path("characters/<int:pk>/update/money", CharacterUpdateMoneyView.as_view(), name="character-update-money"),
    path("characters/<int:pk>/update/xp", CharacterUpdateXPView.as_view(), name="character-update-xp"),

    path("characters/<int:character_pk>/recipes", CharacterRecipeListView.as_view(), name="character-recipe-list"),
    path("characters/<int:character_pk>/recipes-to-learn", RecipeToLearnListView.as_view(), name="character-recipes-to-learn"),
    path("characters/<int:character_pk>/recipes-to-learn/<str:category>", RecipeToLearnListView.as_view(), name="character-recipes-to-learn-categorised"),
    path("characters/<int:character_pk>/recipe/<int:recipe_pk>/learn", LearnRecipe.as_view(), name="character-learn-recipe"),
    path("characters/<int:character_pk>/recipes/<int:pk>/", CharacterRecipeDetailView.as_view(), name="character-recipe-detail"),
    path("characters/<int:character_pk>/recipes/<int:recipe_pk>/make", UseRecipeView.as_view(), name="use-recipe"),
    
    path("recipes", RecipeListView.as_view(), name="recipe-list"),
    path("recipes/<int:pk>", RecipeDetailView.as_view(), name="recipe-detail"),
    path("recipes/<int:pk>/ingredients", CraftRecipeIngredientListView.as_view(), name="recipe-ingredient-list"),
    path("recipes/craft/create", CraftRecipeCreateView.as_view(), name="craftrecipe-create"),
    path("recipes/alchemy/create", ALchemyRecipeCreateView.as_view(), name="alchemyrecipe-create"),
]