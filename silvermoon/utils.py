import json
import random
from .models import *
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

def genKey():
    symbols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
           'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U',
           'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4',
           '5', '6', '7', '8', '9']
    x = 0
    newKey = ""
    while x < 17:
        digit = random.randint(0, 34)
        if x == 5 or x == 11:
            newKey += '-'
        else:
            newKey += symbols[digit]
        x += 1
    return newKey

def cookieCart(request):
	try:
		cart = json.loads(request.COOKIES['cart'])
	except:
		cart = {}

	items = []
	order = {'get_cart_total':0, 'get_cart_items':0}

	for i in cart:
		try:	
			if(cart[i]['quantity'] > 0):  

				product = Game.objects.get(id=i)
				total = (product.price * cart[i]['quantity'])

				order['get_cart_total'] += total
				order['get_cart_items'] += cart[i]['quantity']

				item = {
					'game':{
						'id':product.id,
						'title':product.title, 
						'price':product.price, 
						'imageURL':product.image.url
						}, 
					'quantity':cart[i]['quantity'],
					'get_total':total,
				}
				items.append(item)

		except:
			pass
			
	return {'order':order, 'items':items}

	
def guestOrder(request, data):
	email = data['paymentData']['email']

	cookieData = cookieCart(request)
	items = cookieData['items']

	order = Order.objects.create(
		email = email,
	)

	for item in items:
		game = Game.objects.get(id=item['game']['id'])
		orderGame = OrderGame.objects.create(
			order=order,
			game=game,
			quantity=(item['quantity'] if item['quantity']>0 else -1*item['quantity']),
		)
	return order


def recommendations():
	gameslist = Game.objects.all().values_list('id','title','descriptionEng')
	df = pd.DataFrame(gameslist)
	df.columns = ['id', 'title', 'description']
	tfidf = TfidfVectorizer(stop_words="english")
	df['description'] = df['description'].fillna("")
	tfidf_matrix = tfidf.fit_transform(df['description'])
	cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
	indexes = pd.Series(df.index, index=df['title']).drop_duplicates()

	return df, cosine_sim, indexes
		

def get_recommendation(title, cosine_sim, indexes, df):
	idx = indexes[title]
	sim_scores = enumerate(cosine_sim[idx])
	sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
	sim_scores = sim_scores[1:11]
	sim_index = [i[0] for i in sim_scores]
	return df['title'].iloc[sim_index].tolist()

def collaborative_recommendations():
	gameslist = Game.objects.all().values_list('id','title')
	df_games = pd.DataFrame(gameslist)
	df_games.columns = ['game_id', 'title']
	ratinglist = Rating.objects.all().values_list('user_id','game_id', 'rating')
	df_ratings = pd.DataFrame(ratinglist)
	df_ratings.columns = ['user_id','game_id', 'rating']
	user_item_matrix = df_ratings.pivot(index='game_id', columns='user_id', values='rating')
	user_item_matrix.fillna(0, inplace=True)

	users_votes = df_ratings.groupby('user_id')['rating'].agg('count')
	games_votes = df_ratings.groupby('game_id')['rating'].agg('count')
	user_mask = users_votes[users_votes > 2].index
	game_mask = games_votes[games_votes > 0].index

	user_item_matrix = user_item_matrix.loc[game_mask,:]
	user_item_matrix = user_item_matrix.loc[:, user_mask]

	csr_data = csr_matrix(user_item_matrix.values)

	user_item_matrix = user_item_matrix.rename_axis(None, axis = 1).reset_index()

	knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=5, n_jobs=-1)
	knn.fit(csr_data)

	return df_games, user_item_matrix, knn, csr_data

def get_collaborative_recommendation(recommendations, search_word, df_games, user_item_matrix, knn, csr_data):
	# recommendations = 10
	# search_word = 'The Witcher 3: Wild Hunt'

	games_search = df_games[df_games['title'].str.contains(search_word)]
	searched_game_ig = games_search.iloc[0]['game_id']
	try:
		searched_game_ig = user_item_matrix[user_item_matrix['game_id'] == searched_game_ig].index[0]
	except:
		return []
	
	distances, indices = knn.kneighbors(csr_data[searched_game_ig], n_neighbors=recommendations+1)

	indices_list = indices.squeeze().tolist()
	distances_list = distances.squeeze().tolist()

	indices_distances = list(zip(indices_list, distances_list))

	indices_distances_sorted = sorted(indices_distances, key = lambda x: x[1])
	indices_distances_sorted = indices_distances_sorted[1:]

	recom_list = []

	for ind_dist in indices_distances_sorted:
		matrix_game_id = user_item_matrix.iloc[ind_dist[0]]['game_id']

		id = df_games[df_games['game_id'] == matrix_game_id].index

		title = df_games.iloc[id]['title'].values[0]
		dist = ind_dist[1]

		recom_list.append(title)

	return recom_list