import os

import streamlit as st
from PIL import Image

from package import hirau
#import config

APP_PATH = os.getcwd()

#st.write(APP_PATH)
image = Image.open(APP_PATH+'/images/HIRA.png')
st.image(image, caption='HIRA', width=500)

geo_address = st.text_input('住所',)


n_reader = st.number_input('リーダーの数', step=1, min_value=1)

n_people = st.number_input('避難弱者の数 (リーダーの数より小さい数値)', step=1, max_value=n_reader-1)
n_shelter = st.number_input('避難所の数', step=1, min_value=0)
n_route = st.number_input('経路パターンの数)', step=1, min_value=0)
exec_pass = st.text_input('実行パスワード', type="password")
select_quantum = st.radio('計算方法',('openjij', 'd-wave'))


if select_quantum=='d-wave':
  api_key = st.text_input('api_key', type="password")


map_button = st.checkbox("地図表示", key="A")

if map_button and exec_pass==st.secrets["exec_pass"]:
  fig, G, hirau_list,end_list, leader_list, nodes_color_list, nodes_for_plot = hirau.plot_map(geo_address=geo_address, S=n_reader, M=n_people, E=n_shelter)
  st.pyplot(fig)



option_button = st.button('避難経路最適化スタート')
if option_button and map_button:

  fig2 = hirau.calc_evacuation_route(G=G, hirau_list=hirau_list,end_list=end_list, leader_list=leader_list, nodes_color_list=nodes_color_list, nodes_for_plot=nodes_for_plot,S=n_reader, M=n_people, E=n_shelter, K=n_route)
  st.pyplot(fig2)


