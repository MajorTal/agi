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

# Twitter auth:
API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth) # API version 1
TWITTER_CLIENT = tweepy.Client(bearer_token=BEARER_TOKEN, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET,consumer_key=API_KEY,
                               consumer_secret=API_KEY_SECRET) # API version 2

data_dict = shelve.open("mentions_dict.pkl")

# AWS auth:
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

def get_im2im(text, init_image, strength=0.75):
    with BytesIO() as out:
        init_image.save(out, format="PNG")
        png_string = out.getvalue()
    init_image = base64.b64encode(png_string).decode("utf-8")
    data = dict(inputs=text, strength=strength, init_image=init_image)
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

def reply_to_twitter(screen_name, in_reply_to_status_id, an_image, text=None):
    fp = TemporaryFile()
    an_image.save(fp, "PNG")
    fp.seek(0)
    text = text or f"@{screen_name} here you are:"
    print("reply to twitter with", text)
    res = api.update_status_with_media(text, 'fake_name.jpg', file=fp, in_reply_to_status_id=in_reply_to_status_id)
    return res

def main():
    while True:
        print("Reading Twitter")
        new_replies = get_replies()
        for screen_name, an_id, text, init_image in new_replies:
            print("calling AWS")
            res_image = get_im2im(text, init_image)
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

def clean_twitter_profile_image_url(url):
    """ Example url = "https://pbs.twimg.com/profile_images/1331709417130233861/Ip3RQ-Mr_normal.jpg" """
    beginning, end = url[:url.rfind(".")], url[url.rfind("."):]
    beginning = beginning[:beginning.rfind("_")] # https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/user-profile-images-and-banners
    url = beginning + end
    return url

LIKE_ME_TWIT_ID = 1574716421308747776

def get_new_likers(twit_id=LIKE_ME_TWIT_ID):
    pagination_token = None
    new_likers = []
    while True:
        res = TWITTER_CLIENT.get_liking_users(twit_id, max_results=3, pagination_token=pagination_token, user_fields="profile_image_url,description")
        if not res.data:
            break
        pprint(res.data)
        for user in res.data:
            # print(user.id, user.name, user.username, user.description, user.profile_image_url)
            user_id_str = f"a_like_{twit_id}_{user.id}"
            if user_id_str not in data_dict:
                print("new liker", user.id, user.name, user.username, user.description, user.profile_image_url)    
                new_likers.append(user)
                data_dict[user_id_str] = True
        pagination_token = res.meta.get("next_token")
        if not pagination_token:
            break
    return new_likers

def get_current_image(user):
    profile_image_url = user.profile_image_url
    profile_image_url = clean_twitter_profile_image_url(profile_image_url)
    image =  get_image_from_url(profile_image_url).convert("RGB")
    image = image.resize((512, 512))
    image.show()
    return image

def reply_to_liker(reply_to_user, original_twit_id=LIKE_ME_TWIT_ID):
    print("replying to", reply_to_user.name)
    text = f"Hey {reply_to_user.name}: thanks for liking!\nThis is your current profile image, which I will try to improvise on:"
    current_image = get_current_image(reply_to_user)
    screen_name = getattr(reply_to_user, "screen_name", reply_to_user.name) # sometimes it is not there
    print(screen_name)
    print(original_twit_id)
    current_image.show()
    print(text)
    res = reply_to_twitter(screen_name, in_reply_to_status_id=original_twit_id, an_image=current_image, text=text)
    new_image = get_im2im("Beautiful, amazing, modern art", current_image, 0.7)
    # new_image.show()
    text = "Improvised image:"
    res = reply_to_twitter(screen_name, in_reply_to_status_id=res.id, an_image=new_image, text=text)
    return res

def main_likers():
    new_likers = get_new_likers()
    for user in new_likers:
        reply_to_liker(user)
        

if __name__ == "__main__":
    # del data_dict["1573940857669042181"]
    # main()
    main_likers()
