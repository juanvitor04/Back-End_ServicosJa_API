from django.contrib import admin
from .models import PortfolioItem

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('prestador', 'created_at', 'descricao')
    list_filter = ('prestador',)
    readonly_fields = ('created_at',)