from tempfile import TemporaryFile
from io import BytesIO
from pprint import pprint
import shelve

from PIL import Image # pip install --upgrade Pillow
import requests
import tweepy

api_key = "mGb1fp84NPAPKO17Ge1HJQZQw"
api_key_secret = "TUmRDEuNxVxu5KLNZdSbQaODsFGQpmA8kFgdw0cBp7hnJZVZkd"
access_token = "1397303994612080642-jx78Ja5KkuUma3GCbEcl7QMtJpYpKR"
access_token_secret = "F8fCN0ZKk8psgiHYYv6TjyfJp5TQKMlvhdaeVmBVIkrGn"

data_dict = shelve.open("mentions_dict.pkl")

# This works!!!
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def play():
    # res = api.update_status("testing 123") # This works

    fp = TemporaryFile()
    response = requests.get("https://i.insider.com/5395ae4e69bedd684c95212d?width=600&format=jpeg")
    image = Image.open(BytesIO(response.content))
    image.save(fp, "PNG")
    fp.seek(0)

    res = api.update_status_with_media("testing 1234", 'fake_name.jpg', file=fp)
    # fp.seek(0)
    # res = api.update_status_with_media("t2", 'fake_name.jpg', file=fp, in_reply_to_status_id=res.id)

def replies():
    tweet_id = 1573708416224198657
    name = "taltimes2"
    user_id = 1397303994612080642
    res = api.mentions_timeline()
    for t in res:
        if t.in_reply_to_status_id == tweet_id:
            reply_id = str(t.id)
            if reply_id not in data_dict:
                print("new!")
                data_dict[reply_id] = True
            else:
                print("old")
            print(t.text)
            print(t.id)
            # pprint(t.entities)
            if t.entities:
                media = t.entities.get("media", [])
                for med in media:
                     if med['type'] == 'photo':
                        print(med["media_url"])
            print("\n")
        # break
    return


if __name__ == "__main__":
    # play()
    replies()