### Everything else ###
# Open Jij simulator
from openjij import SQASampler
OJij_sampler = SQASampler()

import numpy as np
import matplotlib.pyplot as plt
#import pandas as pd
#import pandas_datareader.stooq as stooq
from IPython.display import clear_output
import pprint

# colabにデータ読み込み
#from google.colab import files

# 地図情報
import osmnx as ox
import geocoder as geo
import networkx as nx

### 定数入力 ###
#S = 10 # リーダーの数
#M = 5 # 避難弱者の数
#E = 4 # 避難所の数
#K = 3 # ひらわない経路の候補数


### dictに変換 ###
def toDict(full):
  dict = {}
  for i in range(full.shape[0]):
    for j in range(full.shape[1]):
      if full[i][j] != 0.0:
        dict[(i,j)] = full[i][j]
  return dict


### 経路インデックスを返す関数 ###
def x_indx(k,s, Ns):
  i = k + s*Ns
  return i 

### 経路の長さを返す関数 ###
def len_route(G,route):
  L = 0.0
  for l in range(len(route)-1):
    i = route[l]
    j = route[l+1]
    L += G[i][j][0]['length']
  return L

### 地図Gの指定された経路routeの長さをextend_factor倍して返すサブルーチン ###
###  210627修正：Gの複製に失敗していた。どうやらGはポインタ的なものらしい。
def extend_used_route(route,extend_factor, G):
  for k in range(len(route)-1):
    i = route[k]
    j = route[k+1]
    G[i][j][0]['length'] *= extend_factor

  return G

def restore_used_route(route,extend_factor, G):
  for k in range(len(route)-1):
    i = route[k]
    j = route[k+1]
    G[i][j][0]['length'] /= extend_factor
  return G

def plot_map(*, geo_address, S, M, E):

  geo_location = geo.osm(geo_address)
  print(geo_location)
  lat = geo_location.latlng[0]
  lng = geo_location.latlng[1]

  distance = 0.0055
  mr = {
      'north': lat + distance, 'south': lat - distance,
      'east': lng + distance, 'west': lng - distance
  }
  G = ox.graph_from_bbox(mr['north'], mr['south'], mr['east'], mr['west'], network_type='drive')
  G = ox.utils_graph.remove_isolated_nodes(G) # 孤立ノードを除くらしい。が、効果は見られない？

  ### node抽出 ###
  node_list_all = []
  for key in G.nodes(data=False):
      node_list_all.append(key)
  nNodes_all = len(node_list_all)
  print("エリア内のノード数 =",nNodes_all)

  # 繋がっていないノードを除く（ちょっと遅いけれど）
  node_list = []
  for i in range(nNodes_all):
    test_node = node_list_all[i]
    nConnected = 0
    for j in range(nNodes_all):
      nConnected += nx.has_path(G,test_node,node_list_all[j]) #目的地までのパスがある(1)かない(0)か
    if nConnected > nNodes_all/2:
      node_list.append(test_node)
  nNodes = len(node_list)
  print("使えるノード数 =",nNodes)



  ### 目的地をランダムに決める ###

  flag = 0
  nTry = 0
  while flag == 0:
    flag = 1
    nTry += 1
    perm_list = np.random.permutation(node_list).tolist()
    end_list = perm_list[:E]
    leader_list = perm_list[E:E+S]
    hirau_list = perm_list[E+S:E+S+M]
    for s in range(S):
      node = leader_list[s]
      for e in range(E):
        flag *= nx.has_path(G,node,end_list[e]) #目的地までのパスがある(1)かない(0)か
      if flag == 1:
        for m in range(M):
          flag *= nx.has_path(G,node,hirau_list[m]) #目的地までのパスがある(1)かない(0)か
    if flag == 1:
      for m in range(M):
        node = hirau_list[m]
        for e in range(E):
          flag *= nx.has_path(G,node,end_list[e]) #目的地までのパスがある(1)かない(0)か
  print(nTry)

  print("避難所リスト",end_list)
  print("リーダーリスト",leader_list)
  print("弱者リスト",hirau_list)
  temp_list = end_list + leader_list + hirau_list

  nodes_for_plot = [ [temp_list[i]] for i in range(len(temp_list)) ]
  nodes_color_list = ['w']*len(end_list) + ['r']*len(leader_list) + ['g']*len(hirau_list)
  fig, ax  = ox.plot_graph_routes(G, nodes_for_plot, route_colors=nodes_color_list, route_alpha=1.0)
  return fig, G, hirau_list,end_list, leader_list, nodes_color_list, nodes_for_plot

def calc_evacuation_route(*, G, hirau_list,end_list, leader_list, nodes_color_list, nodes_for_plot, S, M, E, K):
  ### 定数入力 ###
  Nh = M
  Ne = E * K
  Ns = Nh + Ne
  N = S * Ns
  #print("QUBOサイズ = ",N)


  ### 経路生成 ###
  # 経路生成 M-E
  MEroute_list = []
  for m in range(M):
    len_min = 1.0e10 # なんかデカい数
    for e in range(E):
      temp_route = nx.shortest_path(G, hirau_list[m], end_list[e], 'length') # M-E
      if len_route(G,temp_route) < len_min: # Eのうち一番近いもの
        shortest_route = temp_route
        len_min = len_route(G,shortest_route)
    MEroute_list.append(shortest_route)

  # 経路生成 S-M-EとS-E
  route_list = []
  route_penalty_factor = 2.0
  for s in range(S):
    for m in range(M):
      temp_route = nx.shortest_path(G, leader_list[s], hirau_list[m], 'length') # S-M
      # S-MとM-Eをつなげる
      route_list.append(temp_route + MEroute_list[m][1:]) # S-M終点とM-E始点の被り注意
    for e in range(E):
      for k in range(K):
        temp_route = nx.shortest_path(G, leader_list[s], end_list[e], 'length') # S-E
        route_list.append(temp_route)
        extend_used_route(temp_route,route_penalty_factor, G)
      for k in range(K):
        restore_used_route(route_list[-k-1],route_penalty_factor, G) # 一番後ろの要素は [-1]
  # print(len(route_list),N)

  ### 罰金 ###
  Q_pen1 = np.zeros(N**2).reshape(N,N)
  for s in range(S):
    for k1 in range(Ns):
      for k2 in range(Ns):
        Q_pen1[x_indx(k1,s, Ns),x_indx(k2,s, Ns)] += 1.0
        if k1 == k2:
          Q_pen1[x_indx(k1,s, Ns),x_indx(k2,s, Ns)] -= 2.0
  # offset_pen1 = S
    
  ### 罰金2 ###
  Q_pen2 = np.zeros(N**2).reshape(N,N)
  for m in range(M):
    for s1 in range(S):
      for s2 in range(S):
        Q_pen2[x_indx(m,s1, Ns),x_indx(m,s2, Ns)] += 1.0
        if s1 == s2:
          Q_pen2[x_indx(m,s1, Ns),x_indx(m,s2, Ns)] -= 2.0
  # offset_pen2 = M

  ### 総経路最短化 ###
  Q_len = np.zeros(N**2).reshape(N,N)
  len_ave = sum( len_route(G,route_list[i]) for i in range(N) )/N
  print(len_ave)
  for i in range(N):
    Q_len[i,i] = (len_route(G,route_list[i])-0.5*len_ave)/len_ave
  # offset_len = 0
    
  # 道路rを番号で定義
  road_dict = {}
  r = 0
  for route in route_list:
    for l in range(len(route)-1):
      road = ( min(route[l],route[l+1]), max(route[l],route[l+1]) )
      if road not in road_dict.keys():
        road_dict[road] = r
        r += 1

  # Cを作ろう
  C = np.zeros(N*len(road_dict)).reshape(N,len(road_dict))
  #D = np.zeros(N*len(road_dict)).reshape(N,len(road_dict))
  for k in range(N):
    route = route_list[k]
    for _ in range(len(road_dict)):
      for l in range(len(route)-1):
        r = road_dict[( min(route[l],route[l+1]), max(route[l],route[l+1]) )]
        C[k,r] = +1/len(route)
        # if route[l] < route[l+1]:
        #   D[k,r] = +1/len(route)
        # else:
        #   D[k,r] = -1/len(route)

  Q_jam = np.dot(C,C.T)
  for i in range(N):
    Q_jam[i,i] = 0.0


  ### QUBO行列合成 ###
  # 係数は適宜調整すること！
  Qdict = toDict( 1*Q_pen1 + 1*Q_pen2 + 1.0*Q_len + 1.0*Q_jam)
  sampleset = OJij_sampler.sample_qubo(Qdict, num_reads=5)
  sortedset = sorted(sampleset.record, key=lambda x: x[1])
  pprint.pprint(sortedset)

  answer = sortedset[0][0]
  answer_route_list = []
  answer_color_list = []
  answer_list = np.where(answer == 1)
  for i in answer_list[0]:
    answer_route_list.append(route_list[i])
    if i%Ns < M:
      answer_color_list.append('y') # ひらう経路の色
    else:
      answer_color_list.append('b') # ひらわない経路の色

  ### 結果表示 ###
  color_list = answer_color_list + nodes_color_list
  fig, ax  = ox.plot_graph_routes(G, answer_route_list + nodes_for_plot, route_colors=color_list, route_alpha= 0.5)

  return fig