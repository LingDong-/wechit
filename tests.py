# -*- coding: utf-8 -*-
from wechit import *
from glob import glob

def print_format_table():
    for style in range(8):
        for fg in range(30,38):
            s1 = ''
            for bg in range(40,48):
                format = ';'.join([str(style), str(fg), str(bg)])
                s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
            print(s1)
        print('\n')


def test_image_print():
    for f in glob("/Library/Desktop Pictures/*.jpg"):
        print f
        print print_thumbnail(Image.open(f).convert("RGB"))


def test_message_print():
    print(print_messages([
    	("秦王","你好"),
        ("秦王","公亦尝闻天子之怒乎"),
        ("唐雎","臣未尝闻也"),
        ("秦王","天子之怒，伏尸百万，流血千里"),
        ("唐雎","大王尝闻布衣之怒乎"),
        ("秦王","布衣之怒，亦免冠徒跣，以头抢地耳"),
        ("唐雎","此庸夫之怒也，非士之怒也。夫专诸之刺王僚也，彗星袭月；聂政之刺韩傀也，白虹贯日；要离之刺庆忌也，仓鹰击于殿上。此三子者，皆布衣之士也，怀怒未发，休祲降于天，与臣而将四矣。若士必怒，伏尸二人，流血五步，天下缟素，今日是也。"),
        ("秦王","先生坐！何至于此！寡人谕矣：夫韩、魏灭亡，而安陵以五十里之地存者，徒以有先生也。"),
    ],my_name="唐雎"))

    print(print_messages([
        ("Yvonne","Where were you last night?"),
        ("Rick","That's so long ago, I don't remember."),
        ("Yvonne","Will I see you tonight?"),
        ("Rick","I never make plans that far ahead."),
        ("Yvone",Image.open("/Library/Desktop Pictures/Poppies.jpg").convert("RGB"))
    ],my_name="Rick"))


if __name__ == "__main__":
    