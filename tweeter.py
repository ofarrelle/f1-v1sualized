import tweepy
from account import twitter_tokens

class Tweeter:
    api = tweepy.API(auth=tweepy.OAuth1UserHandler(
        consumer_key=twitter_tokens.API_KEY,
        consumer_secret=twitter_tokens.API_SECRET_KEY,
        access_token=twitter_tokens.ACCESS_TOKEN,
        access_token_secret=twitter_tokens.ACCESS_TOKEN_SECRET
    ))
    client = tweepy.Client(
        bearer_token=twitter_tokens.BEARER_TOKEN,
        consumer_key=twitter_tokens.API_KEY,
        consumer_secret=twitter_tokens.API_SECRET_KEY,
        access_token=twitter_tokens.ACCESS_TOKEN,
        access_token_secret=twitter_tokens.ACCESS_TOKEN_SECRET
    )

    def __init__(self):
        pass

    def tweet(self, post_content):
        media_ids = []
        for image_path in post_content['image_paths']:
            media_upload_response = self.api.media_upload(image_path)
            media_ids.append(media_upload_response.media_id)
        
        tweet_response = self.client.create_tweet(text=post_content['text'], media_ids=media_ids)
        return tweet_response
