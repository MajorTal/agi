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
LIKE_ME_TWIT_ID = 1575107533832089600

def get_image_from_url(url):
    # print("getting image")
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
            if res_image and sum(res_image.convert("L").getextrema()) not in (0, 2): # All black or all white
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


def get_liker_string_for_db(twit_id, user_id):
    return f"alike_{twit_id}_{user_id}"

def get_new_likers(twit_id=LIKE_ME_TWIT_ID, how_many_to_Get=10):
    pagination_token = None
    new_likers = []
    while len(new_likers) < how_many_to_Get:
        try:
            res = TWITTER_CLIENT.get_liking_users(twit_id, max_results=100, pagination_token=pagination_token, user_fields="profile_image_url,description")
        except tweepy.errors.TooManyRequests:
            sleep(100)
        if not res.data:
            break
        pprint(res.data)
        for user in res.data:
            # print(user.id, user.name, user.username, user.description, user.profile_image_url)
            user_id_str = get_liker_string_for_db(twit_id, user.id)
            if user_id_str not in data_dict or data_dict[user_id_str] == True:
                print("new liker", user.id, user.name, user.username) #, user.description, user.profile_image_url)    
                new_likers.append(user)
                data_dict[user_id_str] = True
                if len(new_likers) >= how_many_to_Get:
                    break
        pagination_token = res.meta.get("next_token")
        if not pagination_token:
            break
    return new_likers

def get_current_image(user):
    profile_image_url = user.profile_image_url
    profile_image_url = clean_twitter_profile_image_url(profile_image_url)
    image =  get_image_from_url(profile_image_url).convert("RGB")
    image = image.resize((512, 512))
    # image.show()
    return image

def reply_to_liker(reply_to_user, original_twit_id=LIKE_ME_TWIT_ID, verbose=False):
    if verbose:
        print("replying to", reply_to_user.name)
    current_image = get_current_image(reply_to_user)
    if verbose:
        current_image.show()
    new_image = get_im2im("Beautiful, amazing, modern art", current_image, 0.7)
    if sum(new_image.convert("L").getextrema()) not in (0, 2): # All black or all white
        if verbose:
            new_image.show()
        media_list = upload_images((current_image, new_image))
        text = f"Hey {reply_to_user.name}: thanks for liking!\nThis is your current profile image, and my improvisation:"
        print(text)
        res = api.update_status(text, media_ids=[media.media_id for media in media_list], in_reply_to_status_id=original_twit_id)  
        user_id_str = get_liker_string_for_db(original_twit_id, reply_to_user.id)
        data_dict[user_id_str] = False  
        return res

def main_likers():
    while True:
        new_likers = get_new_likers()
        for user in new_likers:
            reply_to_liker(user)
            # sleep(36) # Very slow...


def upload_images(list_of_images):
    media_list = []
    for image in list_of_images:
        fp = TemporaryFile()
        image.save(fp, "PNG")
        fp.seek(0)
        media = api.simple_upload("ignore.png", file=fp)
        media_list.append(media)
    return media_list

def play_w_media_list():
    image1 = get_image_from_url("https://st3.depositphotos.com/3047333/12924/i/600/depositphotos_129246006-stock-photo-kitten-sitting-in-flowers.jpg")
    image2 = get_image_from_url("https://st2.depositphotos.com/4341251/6620/i/600/depositphotos_66205515-stock-photo-beautiful-flowers-background.jpg")
    media_list = upload_images((image1, image2))
    res = api.update_status("testing 123", media_ids=[media.media_id for media in media_list])
    print(res)

if __name__ == "__main__":
    # del data_dict["1573940857669042181"]
    # main()
    main_likers()
    # print(os.getenv("HELLO"))
