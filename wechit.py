# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image, ImageOps, ImageStat, ImageEnhance
import os
import sys
from glob import glob
import re
import json
import random
import shutil

IS_PYTHON3 = sys.version_info > (3, 0)        # supports python 2 and 3

LOGIN_SCREEN_FILE = "./temp/login-screen.png" # temp file for qr code
MSG_IMG_FILE = "./temp/msg-img.png"           # temp file for in-chat images
IS_RETINA = True                              # mac with a retina display?

# terminal window dimensions
TERM_ROWS = 24
TERM_COLUMNS = 80

# chrome driver settings
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("safebrowsing-disable-extension-blacklist")
chrome_options.add_argument("--safebrowsing-disable-download-protection")
chrome_options.add_experimental_option("prefs", {'safebrowsing.enabled': 'false'})

if IS_PYTHON3:
    unicode = str # in python 3, unicode and str are unified

# welcome!
def print_splash_screen():
    icon = """
---------------------------------------------------------------------
 _________                                                           
| ___     |                                                          
|( oo)___ |   WECHIT - WECHat In Terminal                            
| v-/oo  )|                                                          
|   '--\| |   Powered by python + selenium, (c) Lingdong Huang 2018  
'---------'                                                          
---------------------------------------------------------------------
"""
    iconcolor = """
?????????????????????????????????????????????????????????????????????
?????????????????????????????????????????????????????????????????????
?#########???????????????????????????????????????????????????????????
?#########????@@@@@@@????????????????????????????????????????????????
?#########???????????????????????????????????????????????????????????
?#########??????????????????????????????????????&&&&&&&&&&&&&&&&&&&??
?????????????????????????????????????????????????????????????????????
?????????????????????????????????????????????????????????????????????
"""
    g = lambda s: color_text(s,37,42)
    w = lambda s: color_text(s,32,40)
    b = lambda s: color_text(s,30,47)
    p = lambda s: s
    result=""
    for t0,t1 in zip(icon.split("\n"),iconcolor.split("\n")):
        for c0,c1 in zip(list(t0),list(t1)):
            result += g(c0) if c1 == "#" else (w(c0) if c1 == "@" else (b(c0) if c1 == "&" else p(c0)))
        result += "\n"
    return result

# initialize chrome driver and navigate to "WeChat for Web"
def init_driver(path=os.path.join(os.getcwd(),"chromedriver")):
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=path)
    driver.get("https://web.wechat.com")
    return driver

# observe and update terminal dimensions
def get_term_shape():
    global TERM_ROWS, TERM_COLUMNS
    if IS_PYTHON3:
        result = tuple(reversed(list(shutil.get_terminal_size((TERM_COLUMNS, TERM_ROWS)))))
    else:
        result = tuple([int(x) for x in os.popen('stty size', 'r').read().split()])
    TERM_ROWS,TERM_COLUMNS = result
    return result

# retrieve a function for mapping RGB values to ANSI color escape codes
def get_color_mapper(file):
    dat = json.loads(open(file,'r').read())
    color_map = {tuple([int(y) for y in x.split(" ")]):dat[x] for x in dat}
    def nearest(r,g,b):
        d0 = None
        k0 = None
        for k in color_map:
            d = (k[0]-r)**2+(k[1]-g)**2+(k[2]-b)**2
            if k0 is None or d <= d0:
                k0 = k
                d0 = d
        return color_map[k0]
    return nearest
color_mapper = get_color_mapper("colormap.json")

# apply ANSI color escape codes
def color_text(s,fg,bg,bold=True):
    format = ';'.join([str(int(bold)), str(fg), str(bg)])
    return '\x1b[%sm%s\x1b[0m' % (format,s)

# remove ANSI color escape codes
def uncolor_text(s):
    s = re.sub(r"\x1b\[.*?;.*?;.*?m", "", s)
    s = re.sub(r"\x1b\[0m","",s)
    return s

# num of characters in width when given string is printed in terminal
# chinese characters are typically 2, ascii characters are 1
def rendered_len(s):
    while True:
        try:
            return sum([(1 if ord(x) < 256 else 2) for x in unrender_unicode(uncolor_text(s))])
        except:
            try:
                return sum([(1 if ord(x) < 256 else 2) for x in uncolor_text(s)])
            except:
                return rendered_len(s[:-1])

# draw a box made of ASCII characters around some text (auto wraps)
def box_text(s,caption="",w=40,fg=30,bg=42):
    iw = w-4
    lines = s.split("\n")
    result = ".-"+caption[:w-4]+("-"*(iw-rendered_len(caption)))+"-."+"\n"

    def strslice(s,n):
        for i in range(len(s)*2):
            if rendered_len(s[:i]) >= n:
                return s[:i], s[i:]
        return s,''

    def renderline(l):
        a,b = strslice(l,iw)
        return "|"+color_text(" "+a+(" "*max(0,iw-rendered_len(a)))+" ",fg,bg)+"|" \
            + ("\n"+renderline(b) if b != "" else "")

    result += "\n".join([renderline(l) for l in lines])

    result += "\n'-"+("-"*iw)+"-'"
    return result

# draw a box around some ASCII art
def box_image(im,w=40,caption=""):
    iw = w-4
    s = print_thumbnail(im,width=iw)
    lines = [l for l in s.split("\n") if len(l) > 0]
    result = ".-"+caption+("-"*(iw-rendered_len(caption)))+"-."+"\n"
    def renderline(l):
        return "| "+l+" |"
    result += "\n".join([renderline(l) for l in lines])
    result += "\n'-"+("-"*iw)+"-'"
    return result

# align block of text 'left' or 'right' or 'center' by padding whitespaces
def align_text(s,w=80,align="left"):
    lines = s.split("\n")
    result = ""
    for l in lines:
        n = (w-rendered_len(l))
        sp = " "
        if align == "left":
            result += l+sp*n
        elif align == "center":
            result += (sp*(n//2))+l+(sp*(n-n//2))
        elif align == "right":
            result += (sp*n)+l
        result += "\n"
    return result

# convert a PIL image to ASCII art
def print_image(im, x_step=12, y_step=24, calc_average=False):
    W,H = im.size
    result = ""
    for i in range(0,H,y_step):
        for j in range(0,W,x_step):
            if calc_average:
                roi = im.crop((j,i,min(W-1,j+x_step),min(H-1,i+y_step)))
                col = ImageStat.Stat(roi).mean
            else:
                col = im.getpixel((min(W-1,j+x_step//2),min(H-1,i+y_step//2)))
            conf = color_mapper(*(col[:3]))
            result += color_text(*conf)
        result += "\n"
    return result

# convert a PIL image to ASCII art given output width in characters
def print_thumbnail(im,width=64):
    W,H = im.size
    x_step = int(float(W)/width)
    y_step = x_step * 2
    converter = ImageEnhance.Color(im)
    im = converter.enhance(2)
    return print_image(im,x_step=x_step,y_step=y_step,calc_average=False)

# get bounding box of html element on screen
def get_rect(elem):
    s = 1+IS_RETINA
    rect = elem.location['x']*s, elem.location['y']*s, (elem.location['x']+elem.size['width'])*s, (elem.location['y']+elem.size['height'])*s
    return rect

# fetch login QR code as PIL image
def get_qr_code(driver):
    os.system("rm "+LOGIN_SCREEN_FILE)
    print("retrieving qr code...")
    driver.get_screenshot_as_file(LOGIN_SCREEN_FILE)

    qrelem = driver.find_element_by_class_name("qrcode").find_element_by_class_name("img")

    rect = get_rect(qrelem)

    while len(glob(LOGIN_SCREEN_FILE)) == 0:
        time.sleep(0.5)

    im = Image.open(LOGIN_SCREEN_FILE).crop(rect)
    if abs(im.getpixel((1, 1))[0] - 204) < 10:
        print("qr code is still loading, trying again...")
        time.sleep(1)
        return get_qr_code(driver)
    print("qr code retrieved!")
    return im

# convert QR code to ASCII art
def print_qr_code(im):
    black_token = color_text("  ",37,40)
    white_token = color_text("  ",30,47)
    im = im.resize((540,540))
    uw = 12
    icnt = 38
    W,H = im.size
    pad = (W-uw*icnt)//2
    result = ""
    for i in range(icnt):
        result += white_token
        for j in range(icnt):
            x,y = pad+uw*j, pad+uw*i
            b = im.getpixel((x+uw//2,y+uw//2))[0] < 128
            if b:
                result += black_token
            else:
                result += white_token
        result += white_token+"\n"
    whiterow = white_token*(icnt+2)
    return whiterow+"\n"+result+whiterow+"\nscan to log in to wechat"

# universal method for querying user for string input
def ask_for(q):
    if IS_PYTHON3:
        return input(q)
    else:
        return raw_input(q)

# wait for chat window to load (right after logging in)
def wait_for_chat_window(driver):
    while True:
        try:
            if len(get_username(driver)) > 0:
                return
        except:
            pass
        time.sleep(0.5)

# convert formatted unicode entry points to unicode characters
def render_unicode(s):
    return re.sub(r"\\u.{4}", lambda x: chr(int(x.group(0)[2:],16)), s)

# decode unicode
def unrender_unicode(s):
    if IS_PYTHON3:
        return s
    return s.decode("utf-8")

# remove wechat-specific emoji's
def no_emoji(s):
    return re.sub(r"<img.*>", "*", s)

# sends both 'enter' and 'return' key multiple times to make sure wechat get it
def send_enter(elem):
    for i in range(5):
        time.sleep(0.1)
        elem.send_keys(Keys.ENTER)
        elem.send_keys(Keys.RETURN)

# get my own username
def get_username(driver):
    return render_unicode(no_emoji(
        driver.find_element_by_class_name("give_me").find_element_by_class_name("display_name").get_attribute("innerHTML")
        ))

# get a list of recent conversation partners
def list_conversations(driver):
    names = []
    while len(names) == 0:
        try:
            names = driver.find_element_by_id("J_NavChatScrollBody").find_elements_by_class_name("nickname_text")
        except:
            pass
    names = [x.get_attribute("innerHTML") for x in names]
    names = [render_unicode(no_emoji(name)) for name in names]
    
    return names

# start a conversation with someone
# (immplementation: search their name in the search bar and press enter)
def goto_conversation(driver, name="File Transfer"):
    search = driver.find_element_by_id("search_bar").find_element_by_class_name("frm_search")
    search.send_keys(name)
    send_enter(search)

    return driver.find_element_by_id("chatArea").find_element_by_class_name("title_name").get_attribute("innerHTML")

# get a list of recent messages with current friend
def list_messages(driver):
    elems = driver.find_element_by_id("chatArea").find_element_by_class_name("chat_bd").find_elements_by_class_name("message")
    msgs = []
    for e in elems:
        try:
            author = render_unicode(no_emoji(e.find_element_by_class_name("avatar").get_attribute("title")))
            content = e.find_elements_by_class_name("content")[-1]
        except:
            continue

        message = ""
        txts = content.find_elements_by_class_name("js_message_plain")
        pics = content.find_elements_by_class_name("msg-img")

        if len(txts) > 0:
            message = txts[0].get_attribute("innerHTML")

        elif len(pics) > 0:
            driver.get_screenshot_as_file(MSG_IMG_FILE)
            rect = get_rect(pics[0])
            im = Image.open(MSG_IMG_FILE).crop(rect)
            message = im

        else:
            message = "<!> message type not supported. please view it on your phone."

        msgs.append((author,message))
    return msgs

# render message history as ASCII art
def print_messages(msgs, my_name="", cols=80):
    result = ""
    for i in range(len(msgs)):
        author = msgs[i][0]
        message = msgs[i][1]
        if author == my_name:
            align,fg,bg = "right",30,42
        else:
            align,fg,bg = "left", 30,47
        if type(message) in [str, unicode]:
            result += align_text(box_text(message,w=min(cols,64,rendered_len(message)+4),caption=" "+author+" ",fg=fg,bg=bg),w=cols,align=align)+"\n"
        elif type(message) is Image.Image:
            result += align_text(box_image(message,w=min(cols,64),caption=" "+author+" "),w=cols,align=align)+"\n"
    return result

# send plain text message to current friend
def send_message(driver, msg="Hello there!"):
    field = driver.find_element_by_class_name("box_ft").find_element_by_id("editArea")
    field.send_keys(unrender_unicode(msg))
    send_enter(field)

# send file to current friend by full path
def upload_file(driver,file_path):
    btn = driver.find_element_by_class_name("box_ft").find_element_by_class_name("js_fileupload")
    try:
        inp = btn.find_element_by_class_name("webuploader-element-invisible")
        inp.send_keys(file_path)
        return True
    except:
        return False

# download all the recent files
# chromedriver seems to bug out in this when in headless mode
def download_files(driver):
    elems = driver.find_element_by_id("chatArea").find_element_by_class_name("chat_bd").find_elements_by_class_name("message")
    for e in elems:
        try:
            content = e.find_elements_by_class_name("content")[-1]
        except:
            continue
        pics = content.find_elements_by_class_name("msg-img")
        atts = content.find_elements_by_class_name("attach")

        while True:
            try:
                if len(pics) > 0:
                    pics[0].click()
                    down_clicked = False
                    while True:
                        try:
                            time.sleep(0.1)
                            close_btn = driver.find_element_by_class_name("J_Preview").find_element_by_class_name("img_preview_close")
                            down_btn = driver.find_element_by_class_name("J_Preview").find_elements_by_class_name("img_opr_item")[1]
                            if not down_clicked:
                                down_btn.click()
                                down_clicked = True
                            time.sleep(0.1)
                            close_btn.click()
                            print("image download initiated.")
                            break
                        except:
                            pass

                if len(atts) > 0:
                    while True:
                        try:
                            atts[0].find_element_by_class_name("opr").find_element_by_class_name("ng-scope").click()
                            print("generic attachment download initiated.")
                            break
                        except:
                            pass
                break
            except:
                pass
    return True


# main app
def main():

    get_term_shape()
    print(print_splash_screen())

    get_term_shape()
    if TERM_ROWS < 50 or TERM_COLUMNS < 80:
        print("your terminal window ("+str(TERM_COLUMNS)+"x"+str(TERM_ROWS)+") is too small. please resize it to 80x50 or larger.")
        ask_for("press enter to continue...")

    print("initializing driver...")
    driver = init_driver()

    time.sleep(1)
    im = get_qr_code(driver)

    get_term_shape()

    print(align_text(print_qr_code(im),w=TERM_COLUMNS,align="center"))
    wait_for_chat_window(driver)
    print("logged in as \""+get_username(driver)+"\"! loading chats...")

    sugs = list_conversations(driver)
    print("welcome!")
    print("who would you like to harass today? here are some suggestions: ")
    print("\n".join([" - "+x for x in sugs]))

    while True:
        ret_name = ""

        while len(ret_name) == 0:
            req_name = ask_for("enter contact's name: (`:q` to quit) <")
            if req_name == ":q":
                driver.close()
                return
            ret_name = goto_conversation(driver, req_name)
            if len(ret_name) == 0:
                print("sorry. you don't have a contact of that name. please try again. ")

        print("ok. now you're chatting with someone called \""+render_unicode(no_emoji(ret_name))+"\"")
        
        while True:
            get_term_shape()
            print("retrieving messages...")
            msgs = list_messages(driver)
            print("rendering messages...")
            print("\n"*TERM_ROWS+print_messages(msgs, my_name=get_username(driver),cols=TERM_COLUMNS))

            print("type your message below: (`:ls` to list recent messages, `:up /path/to/file` to upload, `:down` to download all attachments, `:q` to exit chat)")
            print("-"*TERM_COLUMNS)
            ent = ask_for("to "+color_text("["+render_unicode(no_emoji(ret_name)+"]"),30,47)+" <")

            if ent == ":q":
                break
            elif ent.startswith(":up"):
                pth = " ".join(ent.split(" ")[1:])
                print(["upload failed! check you file path", "upload success!"][int(upload_file(driver, pth))])

            elif ent.startswith(":down"):
                download_files(driver)

            elif ent != "" and ent != ":ls":
                print("sending message...")
                send_message(driver,ent)


if __name__ == "__main__":
    main()
    print("good day.")


