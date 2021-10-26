# 災害時避難誘導アプリ HIRAU

量子アニーリングを利用した組合せ最適化問題に関するワークショップで作成した量子アニーリングを使用した、避難経路最適化アプリ。  
http://www.tfc.tohoku.ac.jp/special/qca/20210510.html  

<br>
<br>
<br>
<br>



# streamlit sharingで公開されております。

https://share.streamlit.io/onhrs/hirau/main/app/app.py



# ai-expo 手順書


clone
```bash
git clone -b demo-gae git@github.com:onhrs/hirau.git

```


```bash
# 仮想環境
python3 -m venv venv

# 新たに仮想環境を作成
source venv/bin/activate

# pipインストール　
pip install -r requirements.txt
```


geocoderの不具合によりgooglemapapiを使用。.envファイルを新たに作成しGOOGLE_MAP_KEYに発行されたapiキーを格納
```
GOOGLE_MAP_KEY = 'xxxxxx'
```

app.yamlに必要事項を記入し以下のコマンドによりデプロイ（gcloudコマンドが必要です）

```bash
gcloud app deploy

```
