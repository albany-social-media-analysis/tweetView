import requests
from flask import Markup

def get_final_url(tweet_id):
    """
    :param tweet_id: tweet_id should be the id_str of the tweet. It should have any non-numerical characters
     (such as "ID_") removed before being passed to this function. 
    :return: tweet_url is the full url for the tweet status
    """
    tweet_status = requests.get('https://twitter.com/user/status/{}'.format(tweet_id))
    tweet_url = tweet_status.url
    return tweet_url

def get_tweet_html(tweet_id, omit_script=True):
     url = 'https://api.twitter.com/1.1/statuses/oembed.json'

     params = {'id':tweet_id,
               'omit_script':omit_script}
     r = requests.get(url, params=params)
     tweet_html = r.json()[u'html']

     return tweet_html
