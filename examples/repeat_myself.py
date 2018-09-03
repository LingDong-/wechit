import sys
import time
sys.path.append("."); import wechit

def send_very_important_message_100_times(recipent="File Transfer", message="Hello World"):
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

    # start conversation with recipent
    ret_name = wechit.goto_conversation(driver, recipent)
    print("ok. now you're chatting with someone called \"%s\"."%(wechit.render_unicode(wechit.no_emoji(ret_name))))

    # send the messages
    for i in range(100):
        print("sending message:",message)
        wechit.send_message(driver,message)
        print("sent!")


if __name__ == "__main__":
    send_very_important_message_100_times()