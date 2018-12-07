import requests

def get_final_url(tweet_id):
    """
    :param tweet_id: tweet_id should be the id_str of the tweet. It should have any non-numerical characters
     (such as "ID_") removed before being passed to this function. 
    :return: tweet_url is the full url for the tweet status
    """
    tweet_status = requests.get('https://twitter.com/user/status/{}'.format(tweet_id))
    tweet_url = tweet_status.url
    return tweet_url
