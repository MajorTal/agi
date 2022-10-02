from tempfile import NamedTemporaryFile
import os
import io

from PIL import Image, ImageDraw, ImageFont
from twitter_bot import get_im2im, LIKE_ME_TWIT_ID, get_liker_string_for_db, data_dict, api, reply_to_liker, get_current_image, get_new_likers
import replicate
import boto3


BUCKET_ZOMBIES = "tal-private-zombie"

AWS_SESSION = boto3.Session(aws_access_key_id=os.getenv("THE_BOT_AWS_ACCESS_KEY_ID"),
                            aws_secret_access_key=os.getenv("THE_BOT_AWS_SECRET_ACCESS_KEY"),
                            region_name=os.getenv("AWS_DEFAULT_REGION"))
S3_CLIENT = AWS_SESSION.client('s3')

ZOMBIE_TEXT = "hyper realistic portrait zombie cinematic, 7 days to die zombie, horror, blood, dirt, expression,"\
              " award winning, intricate, sharp focus, cinematic lighting, rimlight, 8 k concept art, art by z. w. gu, brom, michael hussar,"\
              " redshift, vray, octane render"
ZOMBIE_STRENTH = 0.75



def main1():
    print("hei")
    img = Image.new("RGB", (512, 512), (255, 255, 255))
    image = get_im2im("beautiful sexy woman", img, 0.9)
    if sum(image.convert("L").getextrema()) in (0, 2): # All black or all white
        print("all black or all white")
    else:
        print("all good")
    image.show()

def del_user(user_id):
    user_id_str = get_liker_string_for_db(LIKE_ME_TWIT_ID, user_id)
    del data_dict[user_id_str]

def redo_image_for(user):
    res = api.get_user(screen_name=user)
    reply_to_liker(res, verbose=True)

def clip_interrogate(image):
    model = replicate.models.get("facebookresearch/ic_gan") # replicate.models.get("methexis-inc/img2prompt")
    fp = NamedTemporaryFile()
    image.save(fp, "PNG")
    fp.seek(0)
    output = model.predict(image=image.tobytes().decode("ascii"))
    return output

def play_w_user(user):
    res = api.get_user(screen_name=user)
    current_image = get_current_image(res)
    # current_image.show()
    prompt = clip_interrogate(current_image)
    print(prompt)

def upload_image_to_s3(image, bucket=BUCKET_ZOMBIES, prefix="zombies-"):
    # Save the image to an in-memory file
    in_mem_file = io.BytesIO()
    image.save(in_mem_file, format=image.format)
    in_mem_file.seek(0)

    # Upload image to s3
    res = S3_CLIENT.upload_fileobj(
        in_mem_file, # This is what i am trying to upload
        bucket,
        # "hi.png",
        prefix+image.filename,
        # ExtraArgs={'ACL': 'public-read'}
    )
    return res



def zombie_user(screen_name):
    user = api.get_user(screen_name=screen_name)
    current_image = get_current_image(user)
    current_image.show()
    username = getattr(user, "username", getattr(user, "screen_name", None))
    current_image.filename = f"{username}.png"
    current_image.format = "png"
    res = upload_image_to_s3(current_image)
    new_image = get_im2im(ZOMBIE_TEXT, current_image, ZOMBIE_STRENTH)
    new_image.filename = f"{username}-zombie.png"
    res = upload_image_to_s3(new_image)
    print(res)
    new_image.show()




WIDTH = 3
HEIGHT = 3
OPTIMAL_WIDTH = 1600 # 900 # 1600
OPTIMAL_HEIGHT = 1600
NSFW_TRIES = 10 # Number of tries to fight the NSFW filter
def zombie_users():
    """
    I can variable size the text using https://stackoverflow.com/a/4902713
    """
    # Custom font style and font size
    my_font = ImageFont.truetype('FreeMono.ttf', 65)
    new_likers = get_new_likers(how_many_to_Get=WIDTH*HEIGHT)
    user_index = 0
    new_dim = min((OPTIMAL_WIDTH // WIDTH), (OPTIMAL_HEIGHT // HEIGHT))
    dst = Image.new('RGB', (new_dim*WIDTH*2, new_dim*HEIGHT))
    for height in range(HEIGHT):
        for width in range(WIDTH):
            user = new_likers[user_index]
            image = get_current_image(user).resize((new_dim, new_dim))
            image.filename = f"{user.username}.png"
            for nsfw_try in range(NSFW_TRIES):
                new_image = get_im2im(ZOMBIE_TEXT, image, ZOMBIE_STRENTH).resize((new_dim, new_dim))
                if new_image and sum(new_image.convert("L").getextrema()) not in (0, 2): # All black or all white
                    new_image.filename = f"{user.username}-zombie.png"
                    break
            draw = ImageDraw.Draw(image) # Call draw Method to add 2D graphics in an image
            text = f"{user.name}\n@{user.username}"
            draw.text((28, 36), text, font=my_font, fill=(10, 10, 10))
            dst.paste(image, (new_dim*2*width, new_dim*height))
            if new_image:
                dst.paste(new_image, (new_dim*(2*width+1), new_dim*height))
            user_index = user_index + 1
    dst.show()



if __name__ == "__main__":
    zombie_user("@MeytalinkaVan")
    # zombie_users()
    # @GSKenigsfield")
    # create_bucket(BUCKET_ZOMBIES)
