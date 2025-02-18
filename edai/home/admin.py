from django.contrib import admin
from .models import Dictionary, WordPair

class WordPairInline(admin.TabularInline):
    model = WordPair
    extra = 1  # Number of empty forms to display by default

class DictionaryAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Fields to display in the list view
    inlines = [WordPairInline]  # Include the WordPairInline in the Dictionary Admin

# Register the models
admin.site.register(Dictionary, DictionaryAdmin)
admin.site.register(WordPair)
