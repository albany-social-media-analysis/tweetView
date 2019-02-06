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

     if 'ID_' in tweet_id:
          tweet_id=tweet_id.replace('ID_','')

     params = {'id':tweet_id,
               'omit_script':omit_script}
     
     r = requests.get(url, params=params)
     try:
          r.raise_for_status()
          return r.json()[u'html']
     except Exception as e:
          return f"""<div class="card border-primary mb-3" style="max-width: 60rem;">
               <div class="card-header">Twitter Error</div>
                 <div class="card-body">
                   <p> {e} <p>
                 </div>
               </div>
              </div>
          """