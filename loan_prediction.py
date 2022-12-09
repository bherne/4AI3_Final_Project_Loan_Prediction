# -*- coding: utf-8 -*-
"""Loan_Prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oAYFHCxltgmKQtzxjdBcKOhSvrUuGJKc
"""

import pandas as pd
import seaborn
from matplotlib import pyplot as plt
from google.colab import files
import io
import numpy as np

uploaded = files.upload()

"""# Load the Datasets"""

#open datasets
dataset = pd.read_csv(io.BytesIO(uploaded['train_u6lujuX_CVtuZ9i.csv']))
#dataset_test = pd.read_csv(io.BytesIO(uploaded['test_Y3wMUE5_7gLdaTN.csv']))

dataset.head()

"""# Visualize the Data:"""

credit_hist = dataset['Credit_History']

for x in range(len(credit_hist)):
  if credit_hist[x] == 1:
    credit_hist[x] = 'good'
  elif credit_hist[x] == 0:
    credit_hist[x] = 'bad'

#print(credit_hist)

fig, axes = plt.subplots(3,4, figsize=(24, 15))

seaborn.histplot(data=dataset, x='Gender', ax=axes[0, 0])
seaborn.histplot(data=dataset, x='Married', ax=axes[0,1])
seaborn.histplot(data=dataset, x='Dependents', ax=axes[0,2])
seaborn.histplot(data=dataset, x='Education', ax=axes[0,3])
seaborn.histplot(data=dataset, x='Self_Employed', ax=axes[1,0])
seaborn.boxplot(data=dataset, x='ApplicantIncome', ax=axes[1,1])
seaborn.boxplot(data=dataset, x='CoapplicantIncome', ax=axes[1,2])
seaborn.boxplot(data=dataset, x='LoanAmount', ax=axes[1,3])
seaborn.histplot(data=dataset, x='Loan_Amount_Term', ax=axes[2,0])
seaborn.histplot(data=credit_hist, ax=axes[2,1])
seaborn.histplot(data=dataset, x='Property_Area', ax=axes[2,2])
seaborn.histplot(data=dataset, x='Loan_Status', ax=axes[2,3])

dataplot = seaborn.heatmap(dataset.corr(), cmap="YlGnBu", annot=True)

"""# Preprocess Data"""

#convert all to numerical
dataset['Gender'] = dataset['Gender'].map({'Male':0, 'Female':1}, na_action='ignore')
dataset['Married'] = dataset['Married'].map({'Yes':1, 'No':0}, na_action='ignore')
dataset['Dependents'] = dataset['Dependents'].map({'0':0, '1':1, '2':2, '3+':3}, na_action='ignore')
dataset['Education'] = dataset['Education'].map({'Graduate':1, 'Not Graduate':0}, na_action='ignore')
dataset['Self_Employed'] = dataset['Self_Employed'].map({'Yes':1, 'No':0}, na_action='ignore')
dataset['Property_Area'] = dataset['Property_Area'].map({'Urban':0, 'Semiurban':1, 'Rural':2}, na_action='ignore')
dataset['Loan_Status'] = dataset['Loan_Status'].map({'Y':1, 'N':0}, na_action='ignore')
dataset

#check for na values
dataset.isna().sum()

dataset_clean = dataset

#replace na in Married with 0
dataset_clean['Married'].fillna(0, inplace=True)

#replace na in dependents with 0
dataset_clean['Dependents'].fillna(0, inplace=True)

#replace loan amount with average
dataset_clean['LoanAmount'].fillna(dataset_clean['LoanAmount'].mean(), inplace=True)

#replace loan term wiht median
dataset_clean['Loan_Amount_Term'].fillna(dataset_clean['Loan_Amount_Term'].median(), inplace=True)

#remove all rest
dataset_clean = dataset_clean.dropna()

dataset_clean.isna().sum()

#visulaize outliers 
fig, axes = plt.subplots(3, figsize=(10, 10))

seaborn.boxplot(data=dataset_clean, x='ApplicantIncome', ax=axes[0])
seaborn.boxplot(data=dataset_clean, x='CoapplicantIncome', ax=axes[1])
seaborn.boxplot(data=dataset_clean, x='LoanAmount', ax=axes[2])

#remove major outliers in dataset
dataset_out = dataset_clean
Q1 = dataset_out.quantile(0.25)
Q3 = dataset_out.quantile(0.75)
IQR = Q3 - Q1

#remove only the largest outliers
df = dataset_out[~((dataset_out < (Q1 - 2 * IQR)) |(dataset_out > (Q3 + 2 * IQR))).any(axis=1)]

print("Before removing outliers:", dataset_out.size)
print("After removing outliers:", df.size)
print("Outliers are ", df.size/dataset_out.size *100, "% of the dataset")

#after removing outliers
fig, axes = plt.subplots(3, figsize=(24, 15))

seaborn.boxplot(data=df, x='ApplicantIncome', ax=axes[0])
seaborn.boxplot(data=df, x='CoapplicantIncome', ax=axes[1])
seaborn.boxplot(data=df, x='LoanAmount', ax=axes[2])

#split features and labels
labels = dataset_clean['Loan_Status']
features = dataset_clean.drop(['Loan_Status', 'Loan_ID'], axis=1)

features

from imblearn.over_sampling import RandomOverSampler

#check if balanced
occurances = labels.value_counts()

if occurances[1] == occurances[0]:
  print('balanced dataset')

  features_bal = features
  labels_bal = labels
else:
  print('Unbalanced dataset')  
  print(occurances)

  #balance dataset
  over_sampler = RandomOverSampler(random_state=42)
  features_bal, labels_bal = over_sampler.fit_resample(features, labels)

  print("\nAchive balance via oversampling")
  
print(labels_bal.value_counts())

#normalize data
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler().fit(features_bal)

features_scaled = scaler.transform(features_bal)

"""# Perfrom Feature Selection"""

#split into train, test, and val sets
from sklearn.model_selection import train_test_split

X_train, X_test, Y_train, Y_test = train_test_split(features_scaled, labels_bal, test_size=0.2)

X_train, X_val, Y_train, Y_val = train_test_split(X_train, Y_train, test_size=0.2)

print(X_train.shape)
print(Y_train.shape)
print(X_test.shape)
print(Y_test.shape)
print(X_val.shape)
print(Y_val.shape)

from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.svm import SVC

#determine the best features to use

model = SVC()

best_score = 0

for k in range(1,11):
   #get best k number of features
   #best_features = SelectKBest(score_func=f_classif, k=k).fit_transform(train_features_scaled, train_labels)
   train_features_selected = SelectKBest(score_func=f_classif, k=k).fit_transform(X_train, Y_train)

   #determine the score of the model
   model.fit(train_features_selected, Y_train)

   test_features_selected = SelectKBest(score_func=f_classif, k=k).fit_transform(X_test, Y_test)

   score = model.score(test_features_selected, Y_test) 

   #compare score to best score
   if score >= best_score:
     best_score = score
     selected_features_train = train_features_selected
     selected_features_test = test_features_selected
     num_features = k

#get names of best fetures
selector = SelectKBest(score_func=f_classif, k=num_features).fit(features_bal, labels_bal)
feature_names = selector.get_feature_names_out()

#selected_features
print("Best score:", best_score)
print("Best number of features:", num_features)
print("Selected features:", feature_names)

"""# Determine Best Algorithim to Predict the Loan"""

#model parameter selection
kernel = ['linear', 'poly', 'rbf', 'sigmoid']
best_score = 0

for i in range(len(kernel)):
  #train model with sepecified parameters
  model = SVC(kernel=kernel[i])
  model.fit(selected_features_train, Y_train)

  #deterimine score
  score = model.score(selected_features_test, Y_test) 

  #check if the best score so far
  if score >= best_score:
    best_score = score
    kernel_selected = kernel[i]

print('Best score:', best_score)
print('Selected kernel:', kernel_selected)

"""# Train the Model and Predict the Loan"""

#train model with sepecified parameters
model = SVC(kernel= kernel_selected)
history = model.fit(selected_features_train, Y_train)

#deterimine score
score = model.score(selected_features_test, Y_test) 
print(score)

#predictions

#get selected features from valid


predicted = model.predict(selected_features_test)
print('predicted:')
print(predicted)
print('actual:')
y_test_arr = Y_test.to_numpy()
print(y_test_arr)

num_cor = 0
num_incor = 0

for i in range(len(predicted)):
  if predicted[i] == y_test_arr[i]:
    num_cor = num_cor + 1
  else:
    num_incor = num_incor + 1

print("Number correctly classified:", num_cor)
print("Number incorrectly classified:", num_incor)

#get the selected features not split
selected_feat = features[feature_names]

#re normalize the features
scaler = StandardScaler().fit(selected_feat)
scaled_feat = scaler.transform(selected_feat)

from sklearn.model_selection import learning_curve

#plot learning curve

train_sizes, train_scores, test_scores, fit_times, _ = learning_curve(model, scaled_feat, labels, cv=10,return_times=True)

plt.plot(train_sizes,np.mean(train_scores,axis=1))
plt.plot(train_sizes,np.mean(test_scores,axis=1))
plt.title('Learning Curve')
plt.ylabel('Score')
plt.xlabel('Data Size')
plt.legend(['Train', 'Test'])
plt.show()