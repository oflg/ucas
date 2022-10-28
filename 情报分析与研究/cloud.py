from playwright.sync_api import sync_playwright
import re
from snownlp import SnowNLP
import sys
from wordcloud import WordCloud
from PIL import Image
import numpy as np

with sync_playwright() as p:
    def cancel_request(route, request):
        route.abort()

    def analyze(text):
        textNLP = SnowNLP(text)
        words = textNLP.words()
        keywords = textNLP.keywords(10)
        summary = textNLP.summary(1)
        return words, keywords, summary

    browser = p.chromium.launch(headless=True)
    context = browser.new_context()

    page = browser.new_page()
    page.route(re.compile(r"(\.png)|(\.jpg)|(\.jpeg)|(\.mp4)"), cancel_request)
    page.goto('http://www.cnenergynews.cn/fangtan/list_84_1.html')
    page.wait_for_load_state('networkidle')

    elements = []

    while len(elements) < 100:
        page.get_by_text("查看更多").click()
        page.wait_for_load_state('networkidle')
        elements = page.query_selector_all(
            'a.article-item-title.weight-bold')
        # break

    print(len(elements))

    allwords = []

    for index, element in enumerate(elements):
        if index >= 100:
            break
        title = element.text_content()
        url = element.get_attribute('href')
        print(index, title, url)
        # print(url)
        page1 = context.new_page()
        page1.goto(url)
        # page.click("text="+title)
        page1.wait_for_load_state('networkidle')
        content = page1.query_selector(
            'div.common-width.content.articleDetailContent.en-rich-text-wrapper').text_content()
        # print(content)
        allwords += SnowNLP(content).words
        page1.close()

        # break
    # print(allwords)

    text = ' '.join(allwords)

    stopwords = []
    with open('hit_stopwords.txt', 'r', encoding='utf-8') as f:
        for line in f:
            stopwords += line.strip('\n').split(',')

    mask = np.array(Image.open("china.png"))

    wc = WordCloud(font_path="msyh.ttc",
                             mask=mask,
                             background_color='white',
                             stopwords=stopwords).generate(text)

    wc.to_file("cloud.png")

    context.close()
    browser.close()
