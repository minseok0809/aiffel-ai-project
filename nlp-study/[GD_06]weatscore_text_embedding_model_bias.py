# -*- coding: utf-8 -*-
"""[GD_06]WEATScore_Text_Embedding_Model_Bias.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wYmwQCU-ZLUpOlvh9Ajz62V8iIQBFZOW

##임베딩 내 편향성 알아보기

개발 환경
<br/>데이터 정보

Word Embedding
<br/>Tokenizer
<br/>Word2Vec

Target-Attribute Word Set
<br/>WEAT(Word Embedding Association Test)

결론
<br/>어휘의미망
<br/>데이터의 수학적 구조

참고문헌

#개발 환경
"""

!sudo apt-get install -y fonts-nanum
!sudo fc-cache -fv
!rm ~/.cache/matplotlib -rf

"""한글 폰트를 설치한다.
<br/>혹시 깨짐현상이 발생하는 경우 런타임을 다시 시작하고 matplotlib 혹은 seaborn 모듈을 실행하면 한글이 출력된다.
"""

from matplotlib import font_manager as fm

font_list = [font.name for font in fm.fontManager.ttflist]
font_list

"""Google Colab에 한글 폰트가 설치되어 있는지 확인한다."""

# Commented out IPython magic to ensure Python compatibility.
# %%bash
# apt-get update
# apt-get install g++ openjdk-8-jdk python-dev python3-dev
# pip3 install JPype1
# pip3 install konlpy

# Commented out IPython magic to ensure Python compatibility.
# %env JAVA_HOME "/usr/lib/jvm/java-8-openjdk-amd64"

"""Okt를 작동하기 위한 KoNLPy 환경을 구성한다.
<br/>bash 셸로 명령어 입력하여 라이브러리를 설치한다.<br/>JAVA_HOME 환경변수를 설정한다.
"""

!pip install gensim

import os
import pandas as pd
import seaborn as sns
import matplotlib as plt

import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer

import konlpy
from konlpy.tag import Okt

import gensim
from gensim.models import KeyedVectors
from gensim.models import Word2Vec

import numpy as np
from numpy import dot
from numpy.linalg import norm

from google.colab import drive
drive.mount('/content/drive')

pip freeze > '/content/drive/MyDrive/lms/library_version.txt'

library_name = ['scikit-learn=', 'seaborn=', 'matplotlib=', 'konlpy=', 'gensim=', 'numpy=']
library_version = []
count = 0

import sys
print(sys.version)
print()

with open('/content/drive/MyDrive/lms/library_version.txt', 'r') as f:
    lines = f.read().splitlines() 

for i in range(len(lines)):
  for line in lines[i:i+1]:
    for library in library_name:
      if library in line:
        library_version.append(line)
        count += 1
        print(line, end = '    ')
        if count % 3 == 0:
          print()

gpu_info = !nvidia-smi
gpu_info = '\n'.join(gpu_info)
if gpu_info.find('failed') >= 0:
  print('Not connected to a GPU')
else:
  print(gpu_info)

from psutil import virtual_memory
ram_gb = virtual_memory().total / 1e9
print('Your runtime has {:.1f} gigabytes of available RAM\n'.format(ram_gb))

if ram_gb < 20:
  print('Not using a high-RAM runtime')
else:
  print('You are using a high-RAM runtime!')

"""Google Colab에서 할당된 GPU를 확인한다.
<br/>고용량 메모리 VM에 액세스한다

#데이터 정보

[KOBIS 영화정보 시놉시스](https://www.kobis.or.kr/kobis/business/mast/mvie/searchMovieList.do)

KOBIS(영화관입장권통합전산망) 사이트에서
<br/>2001년부터 2019년 8월까지 제작된 영화의 시놉시스 정보를 수집했다.
"""

print(os.listdir('/content/drive/MyDrive/lms/weat_score/synopsis'))

"""[synopsis](https://d3s0tskafalll9.cloudfront.net/media/documents/synopsis.zip)

영화 구분과 장르 구분에 따라 시놉시스를 분류한다.
<br/>KOBIS에서 제공한 정보를 기준으로 분류한다.

영화 구분 정보는 일반영화(gen), 예술영화(art)로 구분된 정보이다.

장르 구분 정보는 SF, 가족(family), 공연(sbow), 공포(horror), 기타(etc), 다큐멘터리(documentary), 드라마(drama), 멜로/로맨스(romance),
<br/>뮤지컬(musical), 미스터리(mystery), 범죄(crime), 사극(historical), 서부극(western), 성인물(adult), 스릴러(thriller), 
<br/>애니메이션(animation), 액션(action), 어드벤처(adventure), 전쟁(war), 코미디(comedy), 판타지(fantasy)로 구분된 정보이다.
"""

with open('/content/drive/MyDrive/lms/weat_score/synopsis/synopsis.txt', 'r') as file:
    for i in range(11):
      print(file.readline(), end='')

"""#Word Embedding

##Tokenizer
"""

okt = Okt()

tokenized = []
with open('/content/drive/MyDrive/lms/weat_score/synopsis/synopsis.txt', 'r') as file:
    while True:
        line = file.readline()
        if not line: break
        words = okt.pos(line, stem=True, norm=True)
        res = []
        for w in words:
            if w[1] in ["Noun"]:      # "Noun", "Adjective", "Verb" 등을 포함할 수도 있다.
                res.append(w[0])    # 명사일 때만 tokenized에 저장한다. 
        tokenized.append(res)

print(len(tokenized))

"""##Word2Vec"""

model = Word2Vec(tokenized, size=100, window=5, min_count=3, sg=0)

model.wv.most_similar(positive=['영화'])

model.wv.most_similar(positive=['사랑'])

model.wv.most_similar(positive=['연극'])

"""#Target-Attribute Word Set

일반영화와 예술영화라는 영화구분을 Target으로 삼고
<br/>모든 장르를 포함한 장르구분을 Attribute로 삼아 WEAT Score를 구한다.
<br/>장르마다 편향성이 워드 임베딩 상에 얼마나 나타나고 있는지를 측정한다.
"""

def read_token(file_name):
    okt = Okt()
    result = []
    with open('/content/drive/MyDrive/lms/weat_score/synopsis/'+file_name, 'r') as fread: 
        while True:
            line = fread.readline() 
            if not line: break 
            tokenlist = okt.pos(line, stem=True, norm=True) 
            for word in tokenlist:
                if word[1] in ["Noun"]: # "Noun", "Adjective", "Verb" 등을 포함할 수도 있다.
                    result.append((word[0])) # 명사일 때만 tokenized에 저장한다. 
    return ' '.join(result)

art_txt = 'synopsis_art.txt'
gen_txt = 'synopsis_gen.txt'

art = read_token(art_txt)
gen = read_token(gen_txt)

"""WEAT 계산을 위해서는 총 4개의 단어 세트 X, Y, A, B가 필요하다.
<br/>예를 들면 예술영화의 시놉시스 art_txt를 처리해서 만든 art라는 단어 리스트에서부터 예술영화라는 개념을 나타내는 단어를 골라낸다.
"""

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform([art, gen])

print(X.shape)

"""단어 세트 구성을 위해 TF-IDF방식을 사용한다.
<br/>코퍼스에서 자주 나타나는(TF가 높은) 단어이지만, 다른 코퍼스에까지 두루 걸쳐 나오지는 않는(IDF가 높은) 단어를 선정한다.
"""

print(vectorizer.vocabulary_['영화'])
print(vectorizer.get_feature_names_out()[23976])

m1 = X[0].tocoo()     
m2 = X[1].tocoo()  

w1 = [[i, j] for i, j in zip(m1.col, m1.data)]
w2 = [[i, j] for i, j in zip(m2.col, m2.data)]

w1.sort(key=lambda x: x[1], reverse=True)   
w2.sort(key=lambda x: x[1], reverse=True)   

print('예술영화')
for i in range(100):
    if i % 10 == 0 and i > 0:
        print()
    print(vectorizer.get_feature_names_out()[w1[i][0]], end=', ')

print("\n\n")
    
print('일반영화')
for i in range(100):
    if i % 10 == 0 and i > 0:
        print()
    print(vectorizer.get_feature_names_out()[w2[i][0]], end=', ')

"""<br/>

art, gen을 TF-IDF로 표현한 Sparse Matrix를 가져온다.
<br>art, gen을 구성하는 단어를 TF-IDF가 높은 순으로 정렬한다.

개념을 대표하는 단어를 TF-IDF가 높은 순으로 추출하고 싶었는데 양쪽에 중복된 단어가 너무 많은 것을 볼 수 있다.
<br/>두 개념축이 대조되도록 대표하는 단어 세트를 구성하기 위해 단어가 서로 중복되지 않게 단어세트를 추출한다.
"""

n = 15
w1_, w2_ = [], []
for i in range(100):
    w1_.append(vectorizer.get_feature_names_out()[w1[i][0]])
    w2_.append(vectorizer.get_feature_names_out()[w2[i][0]])


target_art, target_gen = [], []
for i in range(100):
    if (w1_[i] not in w2_) and (w1_[i] in model.wv): target_art.append(w1_[i])
    if len(target_art) == n: break 

for i in range(100):
    if (w2_[i] not in w1_) and (w2_[i] in model.wv): target_gen.append(w2_[i])
    if len(target_gen) == n: break

"""상위 100개의 단어들 중 중복되는 단어를 제외하고 상위 n(15)개의 단어를 추출한다."""

print(target_art)

"""w1에 있고 w2에 없는 예술영화를 대표하는 단어를 15개 추출한다."""

print(target_gen)

"""w2에 있고 w1에 없는 일반영화를 대표하는 단어를 15개 추출한다."""

file_txt = os.listdir('/content/drive/MyDrive/lms/weat_score/synopsis')
genre_txt = [ x for x in file_txt if x != 'synopsis.txt' if x != 'synopsis_art.txt' if x != 'synopsis_gen.txt']
genre_txt =  sorted(genre_txt)
genre_name = ['SF', '액션', '성인물(에로)', '어드벤처', '애니메이션', '코미디', '범죄',
              '다큐멘터리', '드라마', '기타', '가족', '판타지', '사극', '공포(호러)',
              '뮤지컬', '미스터리', '멜로로맨스', '공연', '스릴러', '전쟁', '서부극(웨스턴)']

genre = []
for file_name in genre_txt:
    genre.append(read_token(file_name))

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(genre)

print(X.shape)

m = [X[i].tocoo() for i in range(X.shape[0])]

w = [[[i, j] for i, j in zip(mm.col, mm.data)] for mm in m]

for i in range(len(w)):
    w[i].sort(key=lambda x: x[1], reverse=True)
attributes = []
for i in range(len(w)):
    print(genre_name[i])
    attr = []
    j = 0
    while (len(attr) < 15):
        if vectorizer.get_feature_names_out()[w[i][j][0]] in model.wv:
            attr.append(vectorizer.get_feature_names_out()[w[i][j][0]])
            print(vectorizer.get_feature_names_out()[w[i][j][0]], end=', ')
        j += 1
    attributes.append(attr)
    print("\n")

"""<br/>

각 장르를 대표하는 단어들을 추출한다.
<br/>중복된 것이 종종 있지만 art, gen 두 개의 단어 세트를 추출했을 때에 비해 적다.
<br/>따라서 중복을 체크해서 삭제하기보다 그대로 사용한다.

#WEAT(Word Embedding Association Test)
"""

def cos_sim(i, j):
    return dot(i, j.T)/(norm(i)*norm(j))

def s(w, A, B):
    c_a = cos_sim(w, A)
    c_b = cos_sim(w, B)

    mean_A = np.mean(c_a, axis=-1)
    mean_B = np.mean(c_b, axis=-1)
    return mean_A - mean_B #, c_a, c_b

def weat_score(X, Y, A, B):

    s_X = s(X, A, B)
    s_Y = s(Y, A, B)

    mean_X = np.mean(s_X)
    mean_Y = np.mean(s_Y)
    
    std_dev = np.std(np.concatenate([s_X, s_Y], axis=0))
    
    return  (mean_X-mean_Y)/std_dev

matrix = [[0 for _ in range(len(genre_name))] for _ in range(len(genre_name))]

X = np.array([model.wv[word] for word in target_art])
Y = np.array([model.wv[word] for word in target_gen])

for i in range(len(genre_name)-1):
    for j in range(i+1, len(genre_name)):
        A = np.array([model.wv[word] for word in attributes[i]])
        B = np.array([model.wv[word] for word in attributes[j]])
        matrix[i][j] = weat_score(X, Y, A, B)

for i in range(len(genre_name)-1):
    for j in range(i+1, len(genre_name)):
      if j == i+1:
        print(genre_name[i])
      elif j % 7 == 0:
        print()
      print(genre_name[j], round(matrix[i][j], 2), end = '     ')
    print("\n\n")

"""영화 구분, 장르에 따른 편향성을 측정하여 WEAT Score로 계산한다.

X는 예술영화, Y는 일반영화인 Target이다.
<br/>A와 B는 영화 장르인 Attribute이다.

WEAT 점수가 양수로 나오면 X가 A에 가깝고 Y가 B에 가까운 것이다.
<br/>WEAT 점수가 음수로 나오면 X가 B에 가깝고 Y가 A에 가까운 것이다.

<br/>
"""

weat_score_df = pd.DataFrame({'X':['X'],
                             'Y':['Y'],
                             'A':['A'],
                             'B':['B'],
                             'WEAT Score':[0.0],
                             'Analysis':['Comment']})

for i in range(len(genre_name)-1):
    for j in range(i+1, len(genre_name)):
        if matrix[i][j] > 0.8:
          weat_score_df.loc[i] = ['예술영화', '일반영화', genre_name[i], genre_name[j], round(matrix[i][j], 2), 
                                  f'예술영화는 {genre_name[i]}에 가깝고 일반영화는 {genre_name[j]}에 가깝다고 본다']
        elif matrix[i][j] < -0.8:
          weat_score_df.loc[i] = ['예술영화', '일반영화', genre_name[i], genre_name[j], round(matrix[i][j], 2), 
                                 f'예술영화는 {genre_name[j]}에 가깝고 일반영화는 {genre_name[i]}에 가깝다고 본다']

weat_score_df

"""<br/>

WEAT Score 절댓값 0.8을 기준으로 편향성이 두드러지는 영화장르 attribute 구성에는 어떤 케이스가 있는지 파악한다.

<br/>
"""

np.random.seed(0)

sns.set(font='NanumGothic')
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.figsize'] = (18, 16)
ax = sns.heatmap(matrix, xticklabels=genre_name, yticklabels=genre_name, annot=True,  cmap='RdYlGn_r', annot_kws={'size': 14})
ticks = ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

"""<br/>

WEAT Score를 Heatmap 형태로 시각화한다.
<br/>편향성이 두드러지는 영화장르 attribute 구성에는 어떤 케이스가 있는지 시각적으로 나타낸다.

<br/>

#결론

##어휘의미망

단어 세트에 속한 여러 단어들은 개념의 정체성을 나타내는 고유한 의미망을 구축한다.
<br/>일반영화 단어 세트는 일반영화의 정체성을 구성하는 여러 단어의 집합이다.
<br/>예술영화 단어 세트는 예술영화의 정체성을 구성하는 여러 단어의 집합이다.

여기서 더 나아가 무수한 단어 세트가 존재한다.
<br/>단어 세트의 종류는 사전 속에 등재된 단어의 개수처럼 무수하다.
<br/>사전을 펼치면 그 단어를 설명하는 여러 단어가 문장으로 연결된것처럼 단어 세트에는 여러 단어가 속해있다.
<br/>단어는 자기자신을 대표하는 단어 세트의 개념(진부분집합, Proper Subset)인 것과 동시에
<br/>다른 단어 세트에 속해있는 하나의 원소(Element)인 것이다.
<br/>그 집합과 원소들은 거미줄처럼 어휘 네트워크가 구성되어 있다.

WEAT Score는 Target-Attribute Word Set라는 어휘의미망에서 추출해낸 일종의 수치이다.
<br/>Target-Attribute Word Set와 같이 컴퓨터로 구축할 수 있는 어휘의미망으로 무엇이 있을까?
<br/>NLP 기술의 발달으로 어학사전과 같은 밀도있고 다양성있는 어휘의미망을 구축할 수 있을까?

##데이터의 수학적 구조

WEAT Score의 데이터 형태는 상삼각행렬(Upper Triangular Matrix)으로 나타난다.
<br/>WEAT Score을 계산하기 위한 적절한 수학적 구조는 상삼각행렬인 것이다.

데이터마다 수학적으로 표현할 수 있는 양식이 다르다.
<br/>머신러닝과 딥러닝에서 사용하는 데이터의 수학적 구조는 무엇일까?

**Feature Extraction**
<br/>CountVectorizer
<br/>TfidfVectorizer
<br/>HashingVectorizer

**Matrix Decomposition**
<br/>LU Decomposition
<br/>QR Decomposition
<br/>Cholesky Decomposition
<br/>Spectral Decomposition
<br/>Jordan Decomposition
<br/>Eigen Value Decomposition
<br/>Singular Value Decomposition

**Sparse Matrix**
<br/>BSR(Block Sparse Row) Matrix
<br/>COO(Codinate Format) Matrix
<br/>CSC(Compressed Sparse Column) Matrix
<br/>CSR(Compressed Sparse Row) Matrix
<br/>DIA(Diagonal Storage) Matrix
<br/>DOK(Dictionary Of Keys based) Matrix
<br/>LIL(Row-based Linked List) Matrix

**Dense Matrix**
<br/>Frequency Based Embedding&emsp;&emsp;|&emsp;BOW(Bag of Words), CountVector, TF-IDF
<br/>Prediction Based Embedding&emsp;&emsp;|&emsp;CBOW, Skip-gram, Word2Vec

**IDK**
<br/>NMF(Nonnegative Matrix Factorization)
<br/>Gram Matrix
<br/>Co-occurence matrix
<br/>PMI Matrix
<br/>PPMI Matrx
<br/>Similarity matrix
<br/>Adjacent matrix
<br/>Laplacian matrix
<br/>Square matrix

#참고문헌

<br/>**LMS**
<br/>yjseraphina89

<br/>**공식 사이트**
<br/>KOBIS(영화관입장권통합전산망) 
<br/>[영화정보](https://www.kobis.or.kr/kobis/business/mast/mvie/searchMovieList.do)

<br/>**Github**
<br/>Jeongeun-Kwak
<br/>[(G6)WEAT Project.ipynb](https://github.com/Jeongeun-Kwak/GD)
<br/><br/>nevermet
<br/>[G6_WEAT_Score.ipynb](https://github.com/nevermet/AIFFEL/blob/master/G6_WEAT_Score.ipynb)
<br/><br/>lovit
<br/>[(한국어) 텍스트 마이닝을 위한 튜토리얼](https://github.com/lovit/textmining-tutorial)

<br/>**웹사이트**
<br/>[구글 코랩(colab) 한글 깨짐 현상 해결방법](https://teddylee777.github.io/colab/colab-korean)
<br/>[Hide text before seaborn barplot duplicate](https://stackoverflow.com/questions/57165540/hide-text-before-seaborn-barplot)

<br/>**공부**
<br/>[Python 영화진흥위원회 상영관 데이터 웹크롤링](https://littleworks.tistory.com/3)
<br/>[python 크롤링 및 개인프로젝트 시작](https://angehende-ingenieur.tistory.com/180)
<br/>[KOFIC(영화진흥위원회) 영화상세정보 조회 API 서비스](https://www.kobis.or.kr/kobisopenapi/homepg/apiservice/searchServiceInfo.do)
<br/>[파이썬으로 영화오픈API파싱](https://yeowool0217.tistory.com/550)
<br/>[영화진흥위원회 오픈API 사용하는 방법 + csv 추출](https://fjdkslvn.tistory.com/27)
<br/>[행렬 분해(Matrix Decomposition) 종류](https://dhpark1212.tistory.com/entry/SVD%ED%8A%B9%EC%9D%B4%EA%B0%92-%EB%B6%84%ED%95%B4)
<br/>[Scipy sparse matrix handling](https://lovit.github.io/nlp/machine%20learning/2018/04/09/sparse_mtarix_handling/)
<br/>[Implementing PMI (Practice handling matrix of numpy & scipy)](https://lovit.github.io/nlp/2018/04/22/implementing_pmi_numpy_practice/)
<br/>[워드 임베딩(Word Embedding)](http://blog.skby.net/%EC%9B%8C%EB%93%9C-%EC%9E%84%EB%B2%A0%EB%94%A9word-embedding/)
<br/>[그래프와 인접 행렬, 라플라시안 행렬(Adjacent matrix, Laplacian matrix)](https://junklee.tistory.com/112)
<br/>[주어진 사진을 원하는 화풍으로 만드는 Neural Style](https://junklee.tistory.com/69)
"""