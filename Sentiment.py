import pandas as pd
import numpy as np
def get_sentiment(rating_data):
    """
    https: // github.com / cjhutto / vaderSentiment
    :return:
    """
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    rating_data['sent_neg'] = -10
    rating_data['sent_neu'] = -10
    rating_data['sent_pos'] = -10
    rating_data['sent_compound'] = -10
    for i in range(len(rating_data)):
        sentence = rating_data['Sentences'][i]
#         print sentence
        ss = sid.polarity_scores(sentence.encode('ascii', 'ignore'))
        print(ss['neg'])
        rating_data.iloc[i, 1] = float(ss['neg'])
        print(rating_data.iloc[i, 1])
        rating_data.iloc[i, 2] = ss['neu']
        rating_data.iloc[i, 3] = ss['pos']
        rating_data.iloc[i, 4] = ss['compound']
    return rating_data

rating_data = pd.read_csv("insta_comments_natgeo_master_111517.csv", encoding = 'latin1')
sentiment_data = get_sentiment(rating_data)
sentiment_data.to_excel("sentiment_data.xlsx", index = False)