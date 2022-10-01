from tempfile import NamedTemporaryFile

from PIL import Image, ImageDraw, ImageFont

from twitter_bot import get_im2im, LIKE_ME_TWIT_ID, get_liker_string_for_db, data_dict, api, reply_to_liker, get_current_image, get_new_likers
import replicate

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


    res = model.predict(image=fp.name)
    print(res)
    # new_image = get_im2im("Beautiful, amazing, modern art", current_image, 0.7)
    # if sum(new_image.convert("L").getextrema()) not in (0, 2): # All black or all white
    #     new_image.show()

def zombie_user(user):
    res = api.get_user(screen_name=user)
    current_image = get_current_image(res)
    current_image.show()
    new_image = get_im2im("hyper realistic portrait zombie cinematic, 7 days to die zombie, blood, dirt, expression,"\
                          " award winning, intricate, sharp focus, cinematic lighting, rimlight, 8 k concept art, art by z. w. gu, brom, michael hussar,"\
                          " redshift, vray, octane render", current_image, 0.7)
    new_image.show()

# ZOMBIE_TEXT = "hyper realistic portrait zombie cinematic, 7 days to die zombie, blood, dirt, expression,"\
#                           " award winning, intricate, sharp focus, cinematic lighting, rimlight, 8 k concept art, art by z. w. gu, brom, michael hussar,"\
#                           " redshift, vray, octane render"

ZOMBIE_TEXT = "hyper realistic portrait zombie cinematic, 7 days to die zombie, horror, blood, dirt, expression,"\
              " award winning, intricate, sharp focus, cinematic lighting, rimlight, 8 k concept art, art by z. w. gu, brom, michael hussar,"\
              " redshift, vray, octane render"

# ZOMBIE_TEXT = "hyper realistic portrait vampire cinematic, 7 days to die vampire, horror, blood, dirt, expression,"\
#               " award winning, intricate, sharp focus, cinematic lighting, rimlight, 8 k concept art, art by z. w. gu, brom, michael hussar,"\
#               " redshift, vray, octane render"


ZOMBIE_STRENTH = 0.75

WIDTH = 3
HEIGHT = 3
OPTIMAL_WIDTH = 1600 # 900 # 1600
OPTIMAL_HEIGHT = 1600
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
    for width in range(WIDTH):
        for height in range(HEIGHT):
            user = new_likers[user_index]
            image = get_current_image(user).resize((new_dim, new_dim))
            new_image = get_im2im(ZOMBIE_TEXT, image, ZOMBIE_STRENTH).resize((new_dim, new_dim))
            draw = ImageDraw.Draw(image) # Call draw Method to add 2D graphics in an image
            text = f"{user.name}\n@{user.username}"
            draw.text((28, 36), text, font=my_font, fill=(10, 10, 10))
            dst.paste(image, (new_dim*2*width, new_dim*height))
            dst.paste(new_image, (new_dim*(2*width+1), new_dim*height))
            user_index = user_index + 1
    dst.show()

if __name__ == "__main__":
    # zombie_user("@MeytalinkaVan")
    zombie_users()
    # @GSKenigsfield")
