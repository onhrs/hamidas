import numpy as np
from matplotlib import pyplot as plt 

import osmnx as ox
import geocoder as geo
import streamlit as st
import networkx as nx

geo_address = '東京都品川区'

geo_location = geo.osm(geo_address)
lat = geo_location.latlng[0]
lng = geo_location.latlng[1]

mr = {
    'north': lat + 0.01, 'south': lat - 0.01,
    'east': lng + 0.01, 'west': lng - 0.01
}


G = ox.graph_from_bbox(mr['north'], mr['south'], mr['east'], mr['west'], network_type='drive')
# fig, ax  = ox.plot_graph(G)

# st.pyplot(fig)


api_key = st.text_input('api_key', type="password")
car_n = st.number_input('車の数', step=1)
num_route = st.number_input('経路パターンの数', step=1)

def penalty(G,route,pen):
  for k in range(len(route)-1):
      i = route[k]
      j = route[k+1]
      G[i][j][0]['length'] += pen
  return G


def plot_vw(G):

  node_list = []
  for key in G.nodes(data=False):
      node_list.append(key)

  node_list_perm = np.random.permutation(node_list)


  N = car_n*num_route

  start_list = node_list_perm[0:car_n]


  n = 0
  end_list = []

  while len(end_list) < car_n:
    k = len(end_list)
    cand = node_list_perm[car_n+k+n]
    check = nx.has_path(G,start_list[k],cand)
    if check == 1:
      end_list.append(cand)
    else:
      n = n + 1


  route_list = []
  for k in range(car_n):
      start_key = start_list[k]
      end_key = end_list[k]
      shortest_route1 = nx.shortest_path(G, start_key, end_key, 'length')
      route_list.append(shortest_route1) 
      G = penalty(G,shortest_route1,200)
      
      shortest_route2 = nx.shortest_path(G, start_key, end_key, 'length')
      route_list.append(shortest_route2) 
      G = penalty(G,shortest_route2,200)

      shortest_route3 = nx.shortest_path(G, start_key, end_key, 'length')
      route_list.append(shortest_route3) 
      G = penalty(G,shortest_route3,200)
      
      #長くした距離を戻す
      G = penalty(G,shortest_route1,-200)
      G = penalty(G,shortest_route2,-200)
      G = penalty(G,shortest_route3,-200)

  return G, route_list

option_button = st.button('スタート')

if option_button:
  G, route_list = plot_vw(G)
  fig, ax  = ox.plot_graph_routes(G, route_list, route_alpha=0.2)
  st.pyplot(fig)