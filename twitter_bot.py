import base64
from tempfile import TemporaryFile
from io import BytesIO
from pprint import pprint
import shelve
import os
from time import sleep
from tkinter import N

from PIL import Image # pip install --upgrade Pillow
import requests
import tweepy
import sagemaker
from sagemaker.huggingface.model import HuggingFacePredictor
import botocore

API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# This works!!!
auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
TWITTER_CLIENT = tweepy.Client(bearer_token = "AAAAAAAAAAAAAAAAAAAAAPi2gwEAAAAACxUT%2B6fCyr3z8jAzDM0thADjfog%3D4M97crBo5Y5Yu9S3PHBiwL6VvYysJIdwaSueODAIlEL9WluY64"
,access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET,consumer_key=API_KEY, consumer_secret=API_KEY_SECRET)
data_dict = shelve.open("mentions_dict.pkl")

# AWS:
AWS_ACCESS_KEY_ID = os.getenv("aws_access_key_id")
AWS_SECRET_ACCESS_KEY = os.getenv("aws_secret_access_key")
ENDPOINT_NAME = 'huggingface-pytorch-inference-2022-09-24-14-34-53-467'
SESS = sagemaker.Session()
PREDICTOR = HuggingFacePredictor(endpoint_name=ENDPOINT_NAME, sagemaker_session=SESS)

MY_TWEET_ID = 1573796680666841088
MY_USER_ID = 1397303994612080642

def get_image_from_url(url):
    print("getting image")
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image


SINCE_ID = None

def get_replies():
    # name = "taltimes2"
    global SINCE_ID
    new_replies = []
    res = api.mentions_timeline(count=20, since_id=SINCE_ID)
    for t in reversed(res):
        SINCE_ID = t.id
        name = t.user.name
        # print("follows me?", friendship)
        # print(t.text)
        # print()
        if t.in_reply_to_status_id == MY_TWEET_ID:
            print(f"replied by {name}")
            reply_id = str(t.id)
            if reply_id not in data_dict:
                print("New!")
                friendship = api.get_friendship(source_id=t.user.id, target_id=MY_USER_ID)[0]
                following = friendship.following
                if not following:
                    print("not following", t.user.screen_name)
                    continue
                data_dict[reply_id] = True
                if t.entities:
                    media = t.entities.get("media", [])
                    for med in media:
                        if med['type'] == 'photo': # has picture
                            media_url = med["media_url"]
                            print(f"{t.id=}  {media_url=}")
                            image =  get_image_from_url(media_url).convert("RGB")
                            new_replies.append((t.user.screen_name, t.id, t.text, image))
                            break
    return new_replies

def get_im2im(an_id, text, init_image):
    with BytesIO() as out:
        init_image.save(out, format="PNG")
        png_string = out.getvalue()
    init_image = base64.b64encode(png_string).decode("utf-8")
    data = dict(inputs=text, strength=0.75, init_image=init_image)
    try:
        res = PREDICTOR.predict(data=data)
    except PREDICTOR.sagemaker_session.sagemaker_runtime_client.exceptions.ModelError as error:
    #  botocore.errorfactory.ModelError as error:
        print(error)
        res = None
    else:
        imdata = res["image"]
        image = Image.open(BytesIO(base64.b64decode(imdata)))
        return image

def reply_to_twitter(screen_name, an_id, an_image):
    fp = TemporaryFile()
    an_image.save(fp, "PNG")
    fp.seek(0)
    res = api.update_status_with_media(f"@{screen_name} here you are:", 'fake_name.jpg', file=fp, in_reply_to_status_id=an_id)
    # print(res)

def main():
    while True:
        print("Reading Twitter")
        new_replies = get_replies()
        for screen_name, an_id, text, init_image in new_replies:
            print("calling AWS")
            res_image = get_im2im(an_id, text, init_image)
            if res_image:
                print("replying")
                reply_to_twitter(screen_name, an_id, res_image)
            else:
                print("error from model")
        sleep(15)

def play2():
    image =  get_image_from_url('http://pbs.twimg.com/media/FdcsegwWAAYcnas.jpg')
    # res_image = get_im2im(3, "the moon", image)
    # res_image.show()
    reply_to_twitter(1573778431187292163, image)


def get_likes():
    LIKE_ME = 1574731347234390017
    pagination_token = None
    while True:
        res = TWITTER_CLIENT.get_liking_users(LIKE_ME, max_results=3, pagination_token=pagination_token, user_fields="profile_image_url,description")
        if not res.data:
            break
        pprint(res.data)
        for user in res.data:
            print(user.id, user.name, user.username, user.description, user.profile_image_url)
        # print(res.meta)
        pagination_token = res.meta.get("next_token")
        if not pagination_token:
            break

if __name__ == "__main__":
    # del data_dict["1573940857669042181"]
    # main()
    get_likes()
