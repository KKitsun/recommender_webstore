from django.contrib import admin
from .models import Genre, Subgenre, Visual, Theme, Feature, PlayersType, Game, Order, OrderGame, Wishlist, Rating

admin.site.register(Genre)
admin.site.register(Subgenre)
admin.site.register(Visual)
admin.site.register(Theme)
admin.site.register(Feature)
admin.site.register(PlayersType)
admin.site.register(Game)
admin.site.register(Order)
admin.site.register(OrderGame)
admin.site.register(Wishlist)
admin.site.register(Rating)
