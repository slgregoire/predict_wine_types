#cleaning wine data pulled from TW's california store and training a model that will predict the 'color' of the wine using the text of the description
#Note that I am not using cross validation on this model. I am using the out of bag error estimate/score to grade model.

import pandas as pd 
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

#first clean/process all data. 
file = 'complete_list.json'

wine = pd.read_json(file)

#the index is strangely numbered so we replace it with the expected index
wine['key']=range(len(wine))
wine = wine.set_index('key')

#drop record if no color/type
blanks = wine['color']==''
wine = wine[~blanks]
nulls = wine['color'].isnull()
wine = wine[~nulls]

#remove all punction, numerals and all non-letter characters
wine['description'] = wine['description'].str.replace('[^A-Za-z]',' ')
#condense all non-single spacing to single spacing
wine['description'] = wine['description'].str.replace('\s{2,}',' ')
#lowercase all letters
wine['description'] = wine['description'].str.lower()
#remove spaces from the beginning and ending of sentences 
wine['description'] = wine['description'].str.strip()

#now need to remove all the english stop words from all the descriptions. to do this need to split the sentences on spaces, but i don't think i can do this in pandas since splitting would create new fields. so need to export values to array, split, remove stop words, then reinsert values into description column in dataframe
stopwords = set(stopwords.words('english'))
list_desc = wine['description'].values.tolist()
list_desc_cleaned = []

#compile a list of the unique words used in color labels for wines. this will be used to remove all of these words from descriptions so as not to make the classification task obvious
colors = wine['color'].str.replace('[^A-Za-z]',' ').unique()
color_list = []
for color in colors:
	color_split = color.split()
	color_list.extend(color_split)

color_words = []
for el in color_list:
	el_lower = el.lower()
	if el_lower not in color_words:
		color_words.append(el_lower)

#remove any words contained either in the color labels or stop words list
for desc in list_desc:
	words = desc.split()
	meaningful_words = [w for w in words if (w not in stopwords) and (w not in color_words)]
	desc_cleaned = ' '.join(meaningful_words)
	list_desc_cleaned.append(desc_cleaned)

wine['description'] = list_desc_cleaned

#create a matrix of token counts
vectorizer = CountVectorizer(analyzer='word', \
							tokenizer=None, \
							preprocessor=None, \
							stop_words=None, \
							max_features=500)

train_data_features = vectorizer.fit_transform(wine['description'].tolist())
train_data_features = train_data_features.toarray()

#now we train a random forest 
forest = RandomForestClassifier(n_estimators=100, oob_score=True)
forest = forest.fit(train_data_features, wine['color'])

#what's the most important features?
#create a list of tuples that pair feature names and a measure of feature importance
importance = zip(vectorizer.get_feature_names(), forest.feature_importances_) 

#create pandas dataframe from this list
df_importance = pd.DataFrame(importance)
df_importance = df_importance.sort(columns=1, ascending=False)
cols_to_rename = {0: 'feature', 1: 'importance'}
df_importance = df_importance.rename(columns=cols_to_rename)
df_importance = df_importance.set_index('feature')
df_importance.iloc[:20,:].plot(kind='barh') #just plotting top 20 so graph is not too crowded.
plt.show()
