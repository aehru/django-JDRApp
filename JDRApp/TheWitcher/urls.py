from django.urls import path
from TheWitcher.views import CampaignCreateView, CharacterCreateView, CharacterDetailView, CharacterInventoryListView
from TheWitcher.views import AddToInventoryView, EditInventoryEntryView
from TheWitcher.views import IngredientListView
from TheWitcher.views import CharacterRecipeListView, CharacterRecipeDetailView, CharacterRecipeIngredientListView, UseRecipeView
from TheWitcher.views import CharacterCharacteristicListView, CharacterSkillListView
from TheWitcher.views import CraftRecipeIngredientListView
from TheWitcher.views import RecipeListView, RecipeDetailView, LearnRecipe, RecipeToLearnListView

app_name = 'TheWitcher'
urlpatterns = [
    # path("campaigns/add", CampaignCreateView.as_view(), name="campaign-add"),
    path("campaigns/<int:pk>/characters/add", CharacterCreateView.as_view(), name="character-add"),
    path("ingredient/list", IngredientListView.as_view(), name="ingredient-list"),
    path("recipes", RecipeListView.as_view(), name="recipe-list"),
    
    path("character/<int:pk>", CharacterDetailView.as_view(), name="character-detail"),
    path("character/<int:pk>/inventory", CharacterInventoryListView.as_view(), name="character-inventory"),
    path("character/<int:character_pk>/inventory/add", AddToInventoryView.as_view(), name="add-to-inventory"),
    path("character/<int:character_pk>/inventory/edit/<int:pk>", EditInventoryEntryView.as_view(), name="edit-inventory-entry"),
    path("character/<int:pk>/characteristic", CharacterCharacteristicListView.as_view(), name="character-characteristic"),
    path("character/<int:pk>/skills", CharacterSkillListView.as_view(), name="character-skill"),

    path("character/<int:character_pk>/recipes", CharacterRecipeListView.as_view(), name="character-recipe-list"),
    path("character/<int:character_pk>/recipes-to-learn", RecipeToLearnListView.as_view(), name="character-recipes-to-learn"),
    path("character/<int:character_pk>/recipe/<int:recipe_pk>/learn", LearnRecipe.as_view(), name="character-learn-recipe"),
    path("character/<int:character_pk>/recipes/<int:pk>/", CharacterRecipeDetailView.as_view(), name="character-recipe-detail"),
    path("character/<int:character_pk>/recipes/<int:recipe_pk>/make", UseRecipeView.as_view(), name="use-recipe"),
    
    path("recipes/<int:pk>/ingredients", CraftRecipeIngredientListView.as_view(), name="recipe-ingredient-list"),
    path("recipes/<int:pk>", RecipeDetailView.as_view(), name="recipe-detail"),
]