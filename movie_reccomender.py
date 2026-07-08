#system handling
import ast, re, os, pickle
import time

#data handling
import numpy as np # linear algebra
import pandas as pd # data processing
import matplotlib.pyplot as plt
%matplotlib inline
import seaborn as sns
from collections import Counter

#machine learning handling
import sklearn.preprocessing
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

#remove warning
import warnings
warnings.filterwarnings('ignore')
print("Libraries imported ✅")