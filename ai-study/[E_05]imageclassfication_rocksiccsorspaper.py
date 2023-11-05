# -*- coding: utf-8 -*-
"""[E_05]ImageClassfication_RockSiccsorsPaper.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Duc2sKSKP7SyMkYR6zj9414yQZM4Fslt

##인공지능과 가위바위보 하기

개발 환경
<br/>데이터 정보
<br/>데이터 전처리

모델
<br/>Drop-Out
<br/>Non-Drop-Out

모델 학습
<br/>모델 평가
<br/>과적합 문제
<br/>과적합을 방지하는 방법
<br/>결론
<br/>참고문헌

#개발 환경
"""

!pip install split-folders

import os
import glob
from PIL import Image
import splitfolders as sp
import matplotlib.pyplot as plt

"""os(Operating System)는 운영체제에서 제공되는 여러 기능을 파이썬에서 수행한다. <br/>예를 들어, 파일 복사, 디렉터리 생성, 파일 목록을 구할 수 있다.

glob은 사용자가 제시한 조건에 맞는 파일명을 리스트 형식으로 반환한다. 단, 조건에 정규식을 사용할 수 없으며 엑셀 등에서도 사용할 수 있는 '*'와 '?'같은 와일드카드만을 지원한다.

PIL(Python Image Library)는 다양한 이미지 파일 형식을 지원하는 작업 모듈이다. 다만, PIL의 지원이 2011년 중단되고, Pillow가 PIL의 후속 프로젝트로 나왔다.

splitfolders는 데이터를 훈련 데이터, 평가 데이터, 검증 데이터로 분리한다.

matplotlib은 다양한 데이터와 학습 모델을 시각화한다.
"""

import tensorflow as tf
from tensorflow import keras
import numpy as np

"""tensorflow는 구글이 개발한 오픈소스 소프트웨어 딥러닝 및 머신러닝 라이브러리이다. 수학 계산식과 데이터의 흐름을 노드와 엣지를 사용한 방향성 그래프, 데이터 플로우 그래프로 나타낸다.

Keras는 Tensorflow 위에서 동작하는 라이브러리이다.
<br/>사용자 친화적으로 개발된 Keras의 쉽다는 장점과
<br/>딥러닝 프로젝트에서 범용적으로 활용할 수 있는
<br/>Tensorflow의 장점을 통합할 수 있는 환경을 설정한다.

numpy는 array 단위로 벡터와 행렬을 계산한다.
"""

from google.colab import drive
drive.mount('/content/drive')

pip freeze > '/content/drive/MyDrive/lms/library_version.txt'

library_name = ['pandas=', 'numpy=', 'matplotlib=', 'split-folders=', 'tensorflow=', 'keras=', 'Pillow=', 'glob']
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
<br/>고용량 메모리 VM에 액세스한다.

#데이터 정보

**rock_scissors_paper**

2021년 아이펠(Aiffel) 수강생이 촬영했던 가위, 바위, 보 이미지를 통합하여 만든 데이터셋이다.
<br/>포토윅스라는 프로그램을 이용하여 이미지를 편집했다.

이 데이터셋은 224X224 pixel의 6792개의 이미지로 구성되어 있다.
<br/>rock(2202개), scissors(2320개), paper(2270개)의 이미지는 가위바위보 게임의 동작을 나타낸다.

#데이터 전처리
"""

change_path = '/content/drive/MyDrive/lms/rock_scissors_paper'

os.chdir(change_path)
os.getcwd()

sp.ratio('rock', output='rock_output',
                  seed=1337, ratio=(.7, .0, .3))

sp.ratio('scissors', output='scissors_output',
                  seed=1337, ratio=(.7, .0, .3))

sp.ratio('paper', output='paper_output',
                  seed=1337, ratio=(.7, .0, .3))

"""splitfolder는 데이터를 훈련 데이터, 평가 데이터, 검증 데이터로 분리한다.

디렉토리에 따라 폴더를 생성하여 이미지 파일을 이동한다.

train
* rock_train
* scissors_train
* paper_train

test
* rock_test
* scissors_test
* paper_test
"""

def resize_images(img_path):
	images=glob.glob(img_path + "/*.jpg")  
    
	print(len(images), " images to be resized.")

	target_size=(28,28)
	for img in images:
		old_img=Image.open(img)
		new_img=old_img.resize(target_size,Image.ANTIALIAS)
		new_img.save(img, "JPEG")
    
	print(len(images), " images resized.")

"""파일마다 모두 28x28 사이즈로 바꾼다.

왜 28X28인가?
<br/>'Why 28x28 pixel'라고 검색해보았으나 나오지 않는다.
<br/>784(28 x 28)개의 각 뉴런들은 각 픽셀의 밝기를 나타낸다고만 검색 결과가 나올 뿐이다.
"""

image_dir_path1 = '/content/drive/MyDrive/lms/rock_scissors_paper/train/rock_train/'
resize_images(image_dir_path1)

"""rock 이미지를 28x28 사이즈로 바꾼다."""

image_dir_path2 = '/content/drive/MyDrive/lms/rock_scissors_paper/train/scissors_train/'
resize_images(image_dir_path2)

"""scissors 이미지를 28x28 사이즈로 바꾼다."""

image_dir_path3 = '/content/drive/MyDrive/lms/rock_scissors_paper/train/paper_train/'
resize_images(image_dir_path3)

"""paper 이미지를 28x28 사이즈로 바꾼다."""

def load_data(img_path, number_of_data):
    img_size = 28
    color = 3
    
    imgs = np.zeros(number_of_data * img_size * img_size * color, dtype = np.int32).reshape(number_of_data, img_size, img_size, color)
    labels = np.zeros(number_of_data, dtype = np.int32)

    idx = 0
    for file in glob.iglob(img_path + '/rock_train/*.jpg'):
        img = np.array(Image.open(file), dtype = np.int32)
        imgs[idx, :, :, :] = img
        labels[idx] = 0
        idx = idx + 1   

    for file in glob.iglob(img_path + '/scissors_train/*.jpg'):
        img = np.array(Image.open(file), dtype = np.int32)
        imgs[idx, :, :, :] = img
        labels[idx] = 1
        idx = idx + 1
    
    for file in glob.iglob(img_path + '/paper_train/*.jpg'):
        img = np.array(Image.open(file), dtype = np.int32)
        imgs[idx, :, :, :] = img
        labels[idx] = 2
        idx = idx + 1
        
    return imgs, labels

"""라벨을 rock(0), scissors(1), paper(2)로 한다.
<br/>이미지와 라벨을 담은 행렬을 생성한다.

for문을 실행하기 앞서 np.zeros와 reshape를 통해 행렬을 초기화한다.
<br/>np.zeros는 크기(number_of_data x img_size x img_size x color)만큼의 0으로만 채워진 1차원 벡터를 생성한다.
<br/>reshape은 크기(number_of_data x img_size x img_size x color)만큼의 3차원 텐서를 생성한다.
"""

image_dir_path4 = '/content/drive/MyDrive/lms/rock_scissors_paper/train/'
(x_train,y_train) = load_data(image_dir_path4, 4755)
x_train_norm = x_train/255.0

"""훈련 데이터 4755개, 시험 데이터 2038개로 분리한 폴더에서 훈련 데이터를 불러온다.
<br/>255로 나누어 입력은 0~1 사이의 값으로 정규화한다.
"""

print("x_train shape: {}".format(x_train.shape))
print("y_train shape: {}".format(y_train.shape))

"""#모델 학습

Drop-out은 서로 연결된 연결망(layer)에서 0부터 1 사이의 확률로 뉴런을 제거(drop)하는 기법이다.
<br/>Drop-out을 적용하여 상관관계가 강한 Feature를 제외하여
<br/>해당 Feature에만 출력값이 좌지우지되는 과대적합(overfitting)을 방지한다.

Drop-Out 적용한 모델의 이름은 model1
<br/>Drop-Out 적용하지 않은 모델의 이름은 model2로 설정한다.

##Drop-Out
"""

n_channel_1 = 256
n_channel_2 = 512
n_dense = 512
n_class = 3
n_drop_rate = 0.3
n_train_epoch = 10

"""레이어의 개수, 분류 클래스의 개수, drop rate, 최적화의 학습단위(train epoch) 등 하이퍼파라미터 튜닝을 한다."""

model1 =keras.models.Sequential()
model1.add(keras.layers.Conv2D(n_channel_1, (3,3), activation='relu', input_shape=(28,28,3)))
model1.add(keras.layers.MaxPool2D(2,2))
model1.add(keras.layers.Dropout(n_drop_rate))
model1.add(keras.layers.Conv2D(n_channel_2, (3,3), activation='relu'))
model1.add(keras.layers.MaxPooling2D((2,2)))
model1.add(keras.layers.Dropout(n_drop_rate))
model1.add(keras.layers.Flatten())
model1.add(keras.layers.Dense(n_dense, activation='relu'))
model1.add(keras.layers.Dense(n_class, activation='softmax'))

print('Model1 (Drop-Out 적용)에 추가된 Layer 개수: ', len(model1.layers))

"""첫번째 레이어는 사이즈 3의 256개의 필터로 구성되어 있다. 이미지 형태는 28X28 크기이다.
<br/>relu는 활성화함수로 구성된다.
<br/>2 x 2 max-pooling 레이어를 가진다. 추상화된 형태를 오버피팅을 방지하는데 도움을 준다.
<br/>Flatten은 입력을 1차원으로 변환한다.
<br/>Dropout은 오버피팅을 방지한다.
<br/>Dense는 최종적으로 지정된 Class로 분류한다.
"""

model1.summary()

model1.compile(optimizer='adam',
             loss='sparse_categorical_crossentropy',
             metrics=['accuracy'])
model1.fit(x_train_norm, y_train, epochs= n_train_epoch)

"""하이퍼파라미터 최적화 알고리즘으로 Adam을 사용한다.
<br/>Adam은 모멘텀과 AdaGrad를 결합한다.
<br/>매개변수 공간을 효율적으로 탐색해주며 하이퍼파라미터의 편향 보정을 진행한다.

Dropout을 적용했을 때의 모델 성능이다.
<br/>loss가 0.0882일 때, 97.06%의 accuracy가 나온다.

##Non-Drop-Out
"""

n_channel_1 = 256
n_channel_2 = 512
n_channel_3 = 512
n_dense = 512
n_class = 3
n_train_epoch = 10

model2 =keras.models.Sequential()
model2.add(keras.layers.Conv2D(n_channel_1, (3,3), activation='relu', input_shape=(28,28,3)))
model2.add(keras.layers.MaxPooling2D(2,2))
model2.add(keras.layers.Conv2D(n_channel_2, (3,3), activation='relu'))
model2.add(keras.layers.MaxPooling2D((2,2)))
model2.add(keras.layers.Conv2D(n_channel_3, (3,3), activation='relu'))
model2.add(keras.layers.MaxPooling2D((2,2)))
model2.add(keras.layers.Flatten())
model2.add(keras.layers.Dense(n_dense, activation='relu'))
model2.add(keras.layers.Dense(n_class, activation='softmax'))

print('Model2 (Drop-Out 미적용)에 추가된 Layer 개수: ', len(model2.layers))

model2.summary()

model2.compile(optimizer='adam',
             loss='sparse_categorical_crossentropy',
             metrics=['accuracy'])
model2.fit(x_train_norm, y_train, epochs= n_train_epoch)

"""Dropout을 적용하지 않았을 때 모델 성능이 더 높다.
<br/>loss가 0.0317일 때, 99.05%의 accuracy가 나온다.

#모델 평가
"""

image_dir_path5 = '/content/drive/MyDrive/lms/rock_scissor_paper/test/rock_test/'
resize_images(image_dir_path5)

image_dir_path6 = '/content/drive/MyDrive/lms/rock_scissor_paper/test/scissors_test/'
resize_images(image_dir_path6)

image_dir_path7 = '/content/drive/MyDrive/lms/rock_scissors_paper/test/paper_test/'
resize_images(image_dir_path7)

def load_test_data(img_path, number_of_data):
    img_size = 28
    color = 3
    
    imgs = np.zeros(number_of_data * img_size * img_size * color, dtype = np.int32).reshape(number_of_data, img_size, img_size, color)
    labels = np.zeros(number_of_data, dtype = np.int32)

    idx = 0
    for file in glob.iglob(img_path + '/rock_test/*.jpg'):
        img = np.array(Image.open(file), dtype = np.int32)
        imgs[idx, :, :, :] = img
        labels[idx] = 0
        idx = idx + 1   

    for file in glob.iglob(img_path + '/scissors_test/*.jpg'):
        img = np.array(Image.open(file), dtype = np.int32)
        imgs[idx, :, :, :] = img
        labels[idx] = 1
        idx = idx + 1
    
    for file in glob.iglob(img_path + '/paper_test/*.jpg'):
        img = np.array(Image.open(file), dtype = np.int32)
        imgs[idx, :, :, :] = img
        labels[idx] = 2
        idx = idx + 1
        
    return imgs, labels

image_dir_path = '/content/drive/MyDrive/lms/rock_scissors_paper/test/'
(x_test, y_test)=load_test_data(image_dir_path, 2038)
x_test_norm = x_test / 255.0

"""##Drop-Out"""

test1_loss, test1_accuracy = model1.evaluate(x_test_norm, y_test, verbose=2)
print("test_loss: {} ".format(test1_loss))
print("test_accuracy: {}".format(test1_accuracy))

"""##Non-Drop-Out"""

test2_loss, test2_accuracy = model2.evaluate(x_test_norm, y_test, verbose=2)
print("test_loss: {} ".format(test2_loss))
print("test_accuracy: {}".format(test2_accuracy))

"""훈련 데이터와 시험 데이터가 비슷해서 모델 설정이 쉽기 때문에 과적합이 발생한다.

#과적합 문제

과적합 문제를 파악하기 위해 모양이 다른 사진을 시험 데이터로 사용한다.

real_test
* rock
* scissors
* paper
"""

image_dir_path9 = '/content/drive/MyDrive/lms/rock_scissors_paper/real_test/rock/'
resize_images(image_dir_path9)

image_dir_path8 = '/content/drive/MyDrive/lms/rock_scissors_paper/real_test/scissors/'
resize_images(image_dir_path8)

image_dir_path10 = '/content/drive/MyDrive/lms/rock_scissors_paper/real_test/paper/'
resize_images(image_dir_path10)

def load_real_test_data(img_path, number_of_data):
    img_size = 28
    color = 3
    
    imgs = np.zeros(number_of_data * img_size * img_size * color, dtype = np.int32).reshape(number_of_data, img_size, img_size, color)
    labels = np.zeros(number_of_data, dtype = np.int32)

    idx = 0
    for file in glob.iglob(img_path + '/rock/*.jpg'):
        img = np.array(Image.open(file), dtype = np.int32)
        imgs[idx, :, :, :] = img
        labels[idx] = 0
        idx = idx + 1   

    for file in glob.iglob(img_path + '/scissors/*.jpg'):
        img = np.array(Image.open(file), dtype = np.int32)
        imgs[idx, :, :, :] = img
        labels[idx] = 1
        idx = idx + 1
    
    for file in glob.iglob(img_path + '/paper/*.jpg'):
        img = np.array(Image.open(file), dtype = np.int32)
        imgs[idx, :, :, :] = img
        labels[idx] = 2
        idx = idx + 1
        
    return imgs, labels

image_dir_path11 = '/content/drive/MyDrive/lms/rock_scissors_paper/real_test/'
(x_test, y_test)=load_real_test_data(image_dir_path11, 12)
x_test_norm = x_test / 255.0

"""##Drop-Out"""

test3_loss, test3_accuracy = model1.evaluate(x_test_norm, y_test, verbose=2)
print("test_loss: {} ".format(test3_loss))
print("test_accuracy: {}".format(test3_accuracy))

"""##Non-Drop-Out"""

test4_loss, test4_accuracy = model2.evaluate(x_test_norm, y_test, verbose=2)
print("test_loss: {} ".format(test4_loss))
print("test_accuracy: {}".format(test4_accuracy))

"""시험 데이터의 accuracy가 75% 이하로 떨어졌다.
<br/>이유는 훈련 데이터에 대한 과적합이 발생했기 때문이다.
<br/>훈련 데이터와 다른 형태의 데이터가 들어온다면 융통성이 없어서 그 데이터에 적응을 못하는 것이다.

##과적합을 방지하는 방법

> **추가 데이터 수집**
<br/>모형을 일반화하기 위해서는 더 많은 예제를 수집해야 한다.

> **데이터 확대 및 노이즈**
<br/>데이터를 여러 가지 형태로 변형시켜 다양성에 적응할 수 있는 모델의 범용성을 확대한다.
<br/>적당한 노이즈를 추가하여 정제되지 않을 가능성 있는 데이터의 현실성을 반영한다.

> **모델 단순화**
<br/>복잡한 모델을 단순화하여 모델의 학습시간을 줄인다.
<br/>이로 인해 더 많은 학습횟수를 확보할 수 있다.

#결론

model1과 model2는 과적합을 방지할 수 있는 보완점을 마련해야 한다.
<br/>그렇지 않으면 과거 1990년대 후반 ~ 2000년대 초반 MNIST 데이터셋의 매우 쉬운 학습과 같은 한계에 머무를 것이다.
<br/>이러한 MNIST의 한계를 극복하기 위해 Fashion MNIST 등 다양하고 범용성 높은 데이터셋이 사용되기 시작했다는 역사적 배경을 되돌아본다.

과적합을 방지하는 문제를 해결하고 나서야
<br/>이 프로젝트의 목표 Drop-out 하이퍼파라미터 적용이 효과가 있는지 알아보는 것을 달성할 수 있을 것이다.
<br/>현재 model1과 model2 상황으로는 비교할 수 없다.
<br/>또한 Drop-out 하이퍼파라미터는 모델 성능을 끌어올리는 최후의 수단으로 쓰일 것이라고 생각하기에 
<br/>Drop-out보다 과적합 문제 해결이 우선이다.

#참고문헌

**LMS**
<br/>[DrSonicwave](https://github.com/modulabs)

<br/>**단행본**
<br/>정용범, 손상우 외 1명, 『사장님 몰래 하는 파이썬 업무자동화(부제 : 들키면 일 많아짐)』, Wikidocs, 2022
<br/>[Pillow 설치 및 이미지 불러오기](https://wikidocs.net/153080)
<br/>
<br/>권상기 외 1명, 『토닥토닥 파이썬 - 이미지를 위한 딥러닝』, Wikidocs, 2022
<br/>[가위 바위 보 분류 모델 학습](https://wikidocs.net/73612)

<br/>**웹사이트**
<br/>[딥러닝 프레임워크 종류별 장. 단점 - 텐서플로, 케라스, 파이토치](https://hongong.hanbit.co.kr/%EB%94%A5%EB%9F%AC%EB%8B%9D-%ED%94%84%EB%A0%88%EC%9E%84%EC%9B%8C%ED%81%AC-%EB%B9%84%EA%B5%90-%ED%85%90%EC%84%9C%ED%94%8C%EB%A1%9C-%EC%BC%80%EB%9D%BC%EC%8A%A4-%ED%8C%8C%EC%9D%B4%ED%86%A0%EC%B9%98/)
<br/>[Python glob.glob() 사용법](https://m.blog.naver.com/PostView.naver?isHttpsRedirect=true&blogId=siniphia&logNo=221397012627)
<br/>[딥러닝Drop-out(드롭아웃)은 무엇이고 왜 사용할까?](https://heytech.tistory.com/127)
<br/>[Keras를 사용한 머신 러닝 mnist 코드 탐구 (3)](https://m.blog.naver.com/PostView.nhn?isHttpsRedirect=true&blogId=ksg97031&logNo=221302568652)
<br/>[기계학습 : 과적합을 방지하는 방법 6가지](https://iotnbigdata.tistory.com/15)
"""