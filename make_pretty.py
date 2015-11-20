#!/usr/bin/env python
# coding:utf-8

import sys
import os
import re


def make_code_prettify(article):
    # 用于替换code区域中的'''对
    # 为<pre class="prettyprint" style="border: 0"></pre>
    index = [0]  # 开始标签和关闭标签交替

    def repl(obj):
        if index[0] % 2:
            string = '</pre>'
        else:
            string = '<pre class="prettyprint" style="border: 0">'
        index[0] += 1
        return string

    return re.sub(r'```', repl, article)

def deal_one_article(ffile, tofile):
    with open(ffile, 'r') as f:
        article = make_code_prettify(f.read())
    with open(tofile, 'w') as f:
        f.write(article)


if __name__ == "__main__":
    todir = '_posts/'
    fromdir = '_blog/'
    if len(sys.argv) == 1:
        file_names = os.walk(fromdir).next()[2]
        for one in file_names:
            deal_one_article(fromdir + one, todir + one)
            print 'done',one

    if len(sys.argv) == 2:
        deal_one_article(fromdir + sys.argv[1], todir + sys.argv[1])
        print 'done', sys.argv[1]
