import base64
from tempfile import TemporaryFile
from io import BytesIO
from pprint import pprint
import shelve
import os
from time import sleep

from PIL import Image # pip install --upgrade Pillow
import requests
import tweepy
import sagemaker
from sagemaker.huggingface.model import HuggingFacePredictor

API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# This works!!!
auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

data_dict = shelve.open("mentions_dict.pkl")

# AWS:
AWS_ACCESS_KEY_ID = os.getenv("aws_access_key_id")
AWS_SECRET_ACCESS_KEY = os.getenv("aws_secret_access_key")
ENDPOINT_NAME = 'huggingface-pytorch-inference-2022-09-24-14-34-53-467'
SESS = sagemaker.Session()
PREDICTOR = HuggingFacePredictor(endpoint_name=ENDPOINT_NAME, sagemaker_session=SESS)
def play(url):
    # res = api.update_status("testing 123") # This works

    fp = TemporaryFile()
    response = requests.get("https://i.insider.com/5395ae4e69bedd684c95212d?width=600&format=jpeg")
    image = Image.open(BytesIO(response.content))
    image.save(fp, "PNG")
    fp.seek(0)

    res = api.update_status_with_media("testing 1234", 'fake_name.jpg', file=fp)
    # fp.seek(0)
    # res = api.update_status_with_media("t2", 'fake_name.jpg', file=fp, in_reply_to_status_id=res.id)

def get_image_from_url(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image

def get_replies():
    tweet_id = 1573708416224198657
    name = "taltimes2"
    user_id = 1397303994612080642
    new_replies = []
    res = api.mentions_timeline()
    for t in res:
        if t.in_reply_to_status_id == tweet_id:
            reply_id = str(t.id)
            if reply_id not in data_dict: # new!
                data_dict[reply_id] = True
                if t.entities:
                    media = t.entities.get("media", [])
                    for med in media:
                        if med['type'] == 'photo': # has picture
                            media_url = med["media_url"]
                            image =  get_image_from_url(media_url)
                            new_replies.append((t.id, t.text, image))
                            break
    return new_replies

def get_im2im(an_id, text, init_image):
    with BytesIO() as out:
        init_image.save(out, format="PNG")
        png_string = out.getvalue()
    init_image = base64.b64encode(png_string).decode("utf-8")
    data = dict(inputs=text, strength=0.75, init_image=init_image)
    res = PREDICTOR.predict(data=data)
    imdata = res["image"]
    image = Image.open(BytesIO(base64.b64decode(imdata)))
    return image

def reply_to_twitter(an_id, an_image):
    fp = TemporaryFile()
    an_image.save(fp, "PNG")
    fp.seek(0)

    res = api.update_status_with_media("here you go!", 'fake_name.jpg', file=fp, in_reply_to_status_id=an_id)

def main():
    while True:
        print("Reading Twitter")
        new_replies = get_replies()
        for an_id, text, init_image in new_replies:
            res_image = get_im2im(an_id, text, init_image)
            reply_to_twitter(an_id, res_image)

if __name__ == "__main__":
    # play()
    # replies()
    main()