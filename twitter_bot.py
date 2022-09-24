from tempfile import TemporaryFile
from io import BytesIO

from PIL import Image # pip install --upgrade Pillow
import requests


import tweepy

api_key = "mGb1fp84NPAPKO17Ge1HJQZQw"
api_key_secret = "TUmRDEuNxVxu5KLNZdSbQaODsFGQpmA8kFgdw0cBp7hnJZVZkd"
access_token = "1397303994612080642-jx78Ja5KkuUma3GCbEcl7QMtJpYpKR"
access_token_secret = "F8fCN0ZKk8psgiHYYv6TjyfJp5TQKMlvhdaeVmBVIkrGn"


# This works!!!
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


# fp.seek(0)
# res = api.update_status_with_media("t1", 'fake_name.jpg', file=fp)
# fp.seek(0)
# res = api.update_status_with_media("t2", 'fake_name.jpg', file=fp, in_reply_to_status_id=res.id)



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

if __name__ == "__main__":
    play()
