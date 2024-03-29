# Generated by Django 4.2.6 on 2024-01-11 19:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('TheWitcher', '0001_initial'),
        ('dashboard', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='character',
            name='campaign',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.campaign'),
        ),
        migrations.AddField(
            model_name='character',
            name='characteristics',
            field=models.ManyToManyField(related_name='characteristic_for_character', through='TheWitcher.CharacterCharacteristic', to='TheWitcher.characteristic'),
        ),
        migrations.AddField(
            model_name='character',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='character',
            name='skills',
            field=models.ManyToManyField(related_name='skill_for_character', through='TheWitcher.CharacterSkill', to='TheWitcher.skill'),
        ),
        migrations.AddField(
            model_name='alchemyrecipeingredient',
            name='substance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TheWitcher.alchemicalsubstance'),
        ),
        migrations.AddField(
            model_name='craftrecipeingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TheWitcher.craftrecipe'),
        ),
        migrations.AddField(
            model_name='craftrecipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='ingredient_for_recipe', through='TheWitcher.CraftRecipeIngredient', to='TheWitcher.item'),
        ),
        migrations.AddField(
            model_name='alchemyrecipeingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TheWitcher.alchemyrecipe'),
        ),
        migrations.AddField(
            model_name='alchemyrecipe',
            name='substances',
            field=models.ManyToManyField(related_name='substance_for_recipe', through='TheWitcher.AlchemyRecipeIngredient', to='TheWitcher.alchemicalsubstance'),
        ),
    ]
