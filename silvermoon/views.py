from django.shortcuts import render, redirect, HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .utils import *
from .serializers import GameCartSerializer
import json
from django.http import JsonResponse
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.urls import reverse_lazy

from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO

from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django import forms

from silvermoon.forms import MyUserCreationForm

from random import sample, shuffle

class CustomLoginView(LoginView):
    template_name = 'silvermoon/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('shop_page')
    
class RegisterPage(FormView):
    template_name = 'silvermoon/register.html'
    form_class = MyUserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('shop_page')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('shop_page')
        return super(RegisterPage, self).get(*args, **kwargs)

def shop_page(request):
    queryset = Game.objects.all()
    if 'game_title' in request.GET:
          title = request.GET['game_title']
          if title != '':
                 queryset = queryset.filter(title__icontains=title)
    if 'genre' in request.GET:
          id = request.GET['genre']
          if id != '':
                 queryset = queryset.filter(genre__id=id)
    if 'subgenre' in request.GET:
          id = request.GET['subgenre']
          if id != '':
                 queryset = queryset.filter(subgenre__id=id)
    if 'visual' in request.GET:
          id = request.GET['visual']
          if id != '':
                 queryset = queryset.filter(visual__id=id)
    if 'theme' in request.GET:
          id = request.GET['theme']
          if id != '':
                 queryset = queryset.filter(theme__id=id)
    if 'feature' in request.GET:
          id = request.GET['feature']
          if id != '':
                 queryset = queryset.filter(feature__id=id)
    if 'playerType' in request.GET:
          id = request.GET['playerType']
          if id != '':
                 queryset = queryset.filter(playersType__id=id)

    if 'sort_by' in request.GET:
          category = request.GET['sort_by']
          if category != '':
                 queryset = queryset.order_by(category)
    
    context = {
        "Games": queryset,
        "Genres": Genre.objects.all(),
        "Subgenres": Subgenre.objects.all(),
        "Visuals": Visual.objects.all(),
		"Themes": Theme.objects.all(),
        "Features": Feature.objects.all(),
        "Players": PlayersType.objects.all()
	}

    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, status=False)
        context["cartCounter"] = order.get_items_quantity
        orderItemsIds = order.ordergame_set.values_list('game_id', flat=True)
        context["orderItemsIds"] = orderItemsIds
        wishlist = Wishlist.objects.filter(user=user).all()
        context["wishlist"] = wishlist.values_list('game_id', flat=True)
        wishlist_count = wishlist.count()
        gr_titles = []
        gr_titles_collaborative = []
        df, cosine_sim, indexes = recommendations()
        df_games, user_item_matrix, knn, csr_data = collaborative_recommendations()

        if wishlist_count > 0:
            for wish in wishlist:
                rec = get_recommendation(wish.game.title, cosine_sim, indexes, df)
                rec_collaborative = get_collaborative_recommendation(3, wish.game.title, df_games, user_item_matrix, knn, csr_data)
                gr_titles.append(rec)
                gr_titles_collaborative.append(rec_collaborative)

            flat_gr_titles = [x for xs in gr_titles for x in xs]
            flat_gr_titles_collaborative = [x for xs in gr_titles_collaborative for x in xs]

            unique_flat_gr_titles = list(dict.fromkeys(flat_gr_titles))
            unique_flat_gr_titles_collaborative = list(dict.fromkeys(flat_gr_titles_collaborative))

            for wish in wishlist:
                if wish.game.title in unique_flat_gr_titles:
                    unique_flat_gr_titles.remove(wish.game.title)
                if wish.game.title in unique_flat_gr_titles_collaborative:
                    unique_flat_gr_titles_collaborative.remove(wish.game.title)
            if len(unique_flat_gr_titles) > 10:
                unique_flat_gr_titles = sample(unique_flat_gr_titles, 10)
            if len(unique_flat_gr_titles_collaborative) > 10:
                unique_flat_gr_titles_collaborative = sample(unique_flat_gr_titles_collaborative, 10)
            
            game_recs = Game.objects.filter(title__in=unique_flat_gr_titles)
            game_recs = list(game_recs)
            random.shuffle(game_recs)

            game_recs_collaborative = Game.objects.filter(title__in=unique_flat_gr_titles_collaborative)
            game_recs_collaborative_count = game_recs_collaborative.count()
            game_recs_collaborative = list(game_recs_collaborative)
            random.shuffle(game_recs_collaborative)

            context["recommendations"] = game_recs
            context["recommendations_collaborative"] = game_recs_collaborative
            context["recommendations_collaborative_count"] = game_recs_collaborative_count
    

    return render(request, "silvermoon/shop_page.html", context)

def cart(request):
    context = {}
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, status=False)
        items = order.ordergame_set.all()
        context["cartCounter"] = order.get_items_quantity
        context["cartTotal"] = order.get_total_sum
        context["items"] = items
    
    return render(request, "silvermoon/cart.html", context)

def history_page(request):
    context = {}
    if request.user.is_authenticated:
        user = request.user
        orders = Order.objects.all().filter(user=user, status=True)
        # items = order.ordergame_set.all()
        # context["cartCounter"] = order.get_items_quantity
        # context["cartTotal"] = order.get_total_sum
        context["orders"] = orders
        order, created = Order.objects.get_or_create(user=user, status=False)
        context["cartCounter"] = order.get_items_quantity
    else:
        return redirect('login')
    
    return render(request, "silvermoon/history.html", context)

def wishlist_page(request):
    context = {}
    if request.user.is_authenticated:
        user = request.user
        wishlist = Wishlist.objects.all().filter(user=user)
        context["wishlist"] = wishlist
        order, created = Order.objects.get_or_create(user=user, status=False)
        context["cartCounter"] = order.get_items_quantity
    else:
        return redirect('login')
    
    return render(request, "silvermoon/wishlist.html", context)

def checkout_page(request):
    context = {}
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, status=False)
        items = order.ordergame_set.all()
        if not items:
            return redirect('shop_page')
        context["cartCounter"] = order.get_items_quantity
        context["cartTotal"] = order.get_total_sum
        context["items"] = items
        context["order"] = order
    else:
        data = cookieCart(request)
        order = data['order']
        items = data['items']
        if not items:
            return redirect('shop_page')
        context = {'items':items, 'order':order}
    
    return render(request, "silvermoon/checkout.html", context)

def game_page(request, id):
    game = Game.objects.get(pk=id)
    context = {'game':game}
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, status=False)
        context["cartCounter"] = order.get_items_quantity
        orderItemsIds = order.ordergame_set.values_list('game_id', flat=True)
        context["orderItemsIds"] = orderItemsIds
        context["wishlist"] = Wishlist.objects.filter(user=user).values_list('game_id', flat=True)
        rating, created = Rating.objects.get_or_create(user=user, game=game)
        context["rating"] = rating
        df, cosine_sim, indexes = recommendations()
        rec = get_recommendation(game.title, cosine_sim, indexes, df)
        game_recs = Game.objects.filter(title__in=rec)
        game_recs = list(game_recs)
        random.shuffle(game_recs)
        print(game_recs)
        context["recommendations"] = game_recs

    return render(request, "silvermoon/game_page.html", context)

def pdf_report_create(request, order):
    if request.user.is_authenticated:
        order_details = {'get_cart_total':order.get_total_sum, 'get_cart_items':order.get_items_quantity}
        items = order.ordergame_set.all()
        game_keys = []
        for k in range(order_details['get_cart_items']):
            game_keys.append(genKey())
    else:
        data = cookieCart(request)
        order_details = data['order']
        items = data['items']
        game_keys = []
        for k in range(order_details['get_cart_items']):
            game_keys.append(genKey())
    

    template_path = 'silvermoon/Invoice_template_for_pdf.html'

    context = {'items':items, 'order':order_details, 'specific_order': order, 'game_keys':game_keys}

    template = get_template(template_path)

    html = template.render(context)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    pdf = result.getvalue()
    
    if request.user.is_authenticated:
        to_emails = [str(order.user.email)]
    else:
        to_emails = [str(order.email)]
    
    subject = "Silvermoon замовлення"
    email = EmailMessage(subject, body="Дякуємо за покупку!", from_email=settings.EMAIL_HOST_USER, to=to_emails)
    email.attach("Silvermoon_invoice.pdf", pdf, "application/pdf")
    email.send(fail_silently=False)

def processPaymentResult(request):
    paymentResult = json.loads(request.body)
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, status=False)
    else:
        order = guestOrder(request, paymentResult)
    
    order.status = True
    order.save()
    pdf_report_create(request, order)
    return JsonResponse('Successful transaction', safe=False)

def processPaymentTester(request):
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, status=False)
    
    order.status = True
    order.save()
    pdf_report_create(request, order)

    return redirect('shop_page')

@api_view(['GET'])
def cart_data(request):
      games =  Game.objects.all()
      serializer = GameCartSerializer(games, many=True)
      return Response(serializer.data)

def addItemToCart(request):
    data = json.loads(request.body)
    productId = data['productId']

    if not request.user.is_authenticated:
        return JsonResponse('User is not authenticated', safe=False)

    user = request.user
    product = Game.objects.get(id=productId)
    order, created = Order.objects.get_or_create(user=user, status=False)

    orderItem, created = OrderGame.objects.get_or_create(order=order, game=product)

    if created:
        orderItem.quantity = 1
        orderItem.save()
        return JsonResponse('Item was added', safe=False)
    else:
        orderItem.delete()
        return JsonResponse('Item was deleted', safe=False)
    
def changeItemQuantity(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    if not request.user.is_authenticated:
        return JsonResponse('User is not authenticated', safe=False)

    user = request.user
    product = Game.objects.get(id=productId)
    order = Order.objects.get(user=user, status=False)
    orderItem = OrderGame.objects.get(order=order, game=product)
    
    if action == 'plus' and orderItem.quantity < 10:
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'minus' and orderItem.quantity > 1:
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()
    return JsonResponse('Quantity was changed', safe=False)

def deleteCartItem(request):
    data = json.loads(request.body)
    productId = data['productId']

    if not request.user.is_authenticated:
        return JsonResponse('User is not authenticated', safe=False)

    user = request.user
    product = Game.objects.get(id=productId)
    order = Order.objects.get(user=user, status=False)
    orderItem = OrderGame.objects.get(order=order, game=product)

    orderItem.delete()
    return JsonResponse('Item was deleted from cart', safe=False)


def addItemToWishList(request):
    data = json.loads(request.body)
    productId = data['productId']

    if not request.user.is_authenticated:
        return JsonResponse('User is not authenticated', safe=False)

    user = request.user
    product = Game.objects.get(id=productId)
    wish, created = Wishlist.objects.get_or_create(user=user, game=product)

    if created:
        wish.save()
        return JsonResponse('Item was added to wishlist', safe=False)
    else:
        wish.delete()
        return JsonResponse('Item was deleted from wishlist', safe=False)
    
def removeFromWishlist(request):
    data = json.loads(request.body)
    productId = data['productId']

    if not request.user.is_authenticated:
        return JsonResponse('User is not authenticated', safe=False)

    user = request.user
    product = Game.objects.get(id=productId)
    wish = Wishlist.objects.get(user=user, game=product)

    wish.delete()
    return JsonResponse('Item was deleted from wishlist', safe=False)

def rateGame(request):
    data = json.loads(request.body)
    productId = data['productId']
    points = data['points']

    if not request.user.is_authenticated:
        return JsonResponse('User is not authenticated', safe=False)

    user = request.user
    product = Game.objects.get(id=productId)
    rating, created = Rating.objects.get_or_create(user=user, game=product)

    if points >= 0 and points <= 5:
        rating.rating = points

    rating.save()
    return JsonResponse('Game was rated', safe=False)