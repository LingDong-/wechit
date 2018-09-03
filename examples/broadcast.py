import sys
import time
sys.path.append("."); import wechit

def tell_everyone_about_it(recipents=["Bob","Mary","John","Steve"], message="Hello World"):
    print("initializing...")
    
    # initialize driver
    driver = wechit.init_driver()

    # wait for page to load
    time.sleep(1)

    # fetch the qr code
    im = wechit.get_qr_code(driver)

    # display qr code
    print(wechit.print_qr_code(im))

    # wait for chat window to load
    wechit.wait_for_chat_window(driver)
    print("logged in as \""+wechit.get_username(driver)+"\"! loading chats...")


    for recipent in recipents:
        # start conversation with recipent
        ret_name = wechit.goto_conversation(driver, recipent)
        print("now sending message \"%s\" to \"%s\"..."%(message, wechit.render_unicode(wechit.no_emoji(ret_name))))

        # send the message
        wechit.send_message(driver,message)
        print("sent!")
        time.sleep(0.5)


if __name__ == "__main__":
    tell_everyone_about_it(["File Transfer", "Angeline"], "testing")