import requests
import subprocess
from functools import partial
import json
import datetime
from config import *

subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")
import execjs


def decode_js(t):
    """t: 密文"""
    with open('bays4.js', 'r', encoding='utf-8') as f:
        shell = f.read()
    return execjs.compile(shell).call('kmno4_decode', t)


def parse_words(data):
    """data: 请求接口所返回的加密数据"""
    word_dict = {}
    data = json.loads(decode_js(data['data']))
    for obj in data['objects']:
        word = obj['vocab_with_senses']['word']
        zh = obj['vocab_with_senses']['senses'][0]['definition_cn']
        word_dict[word] = zh
    return word_dict


def get_words(new_page_num, review_page_num):
    """
    :param new_page_num: 今日新单词的总页数
    :param review_page_num: 今日复习单词的总页数
    """
    new_word_dict = {}
    review_word_dict = {}
    headers = {
        'Cookie': COOKIE,
        'Origin': 'https://web.shanbay.com',
        'Referer': 'https://web.shanbay.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'X-Csrftoken': 'd86328f526f64d3f382cc651cc9a4ef5'
    }
    # 新单词
    for page in range(1, new_page_num + 1):
        url = f'https://apiv3.shanbay.com/wordsapp/user_material_books/buqwfz/learning/words/today_learning_items?ipp=10&page={page}&type_of=NEW'
        response = requests.get(url=url, headers=headers)
        json_data = response.json()
        new_word_dict.update(parse_words(json_data))
    # 复习单词
    for page in range(1, review_page_num + 1):
        url = f'https://apiv3.shanbay.com/wordsapp/user_material_books/buqwfz/learning/words/today_learning_items?ipp=10&page={page}&type_of=REVIEW'
        response = requests.get(url=url, headers=headers)
        json_data = response.json()
        review_word_dict.update(parse_words(json_data))
    return new_word_dict, review_word_dict


def save_words(new, review):
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    words = ''
    txt = '今日新学单词\n\n'
    for key, values in new.items():
        txt += f'{key}: {values} \n'
        words += f'{key}, '
    txt += '\n今日复习单词\n\n'
    for key, values in review.items():
        txt += f'{key}: {values} \n'
        # words += f'{key}, '
    txt += f'\n今日全部新学英文单词\n\n {words}'
    txt += f'\n\n\n今日prompt\n\n'
    txt += f"""你现在是一位《经济学人》的杂志编辑，我需要要你用一些单词来写一篇英文的文章，大概200词左右，内容丰富。单词列表会被三个反引号括起来。
        必须用上所有的单词，单词列表中的单词，在文章中需要用粗体，斜体来表示。文章的末尾要有中文翻译。
        需要用markdown的形式输出
        以下是单词'''{words}'''
    """
    with open(f'{today}.txt', mode='w', encoding='utf-8') as f:
        f.write(txt)


if __name__ == '__main__':
    save_words(*get_words(NEW_PAGE_NUM, REIVEW_PAGE_NUM))
