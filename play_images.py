from tempfile import NamedTemporaryFile

from PIL import Image
from twitter_bot import get_im2im, LIKE_ME_TWIT_ID, get_liker_string_for_db, data_dict, api, reply_to_liker, get_current_image
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



if __name__ == "__main__":
    play_w_user("@me0123455")
