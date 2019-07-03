from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import jieba

import json

from flask import render_template_string
import pdfkit
from app import get_word_cloud
from charts.salary_pie import *


def func():
    keyword = 'python'
    jobs = get_jobs_by_keyword(keyword)
    with open('static/data/a.json', encoding='utf8') as f:
        d = json.load(f)

    dd = {}
    provinces = d.get('provinces')

    for province in provinces:
        province_name = province.get('provinceName')
        city_list = []
        for city in province.get('citys'):
            city_list.append(city.get('citysName'))
        dd[province_name] = city_list


def func2():
    keyword = ''
    jobs = get_jobs_by_keyword(keyword)
    with open('static/data/cities.json', encoding='utf8') as f:
        d = json.load(f)

    province_count = defaultdict(lambda: 0)
    for job in jobs:
        found = False
        job_city = job.get('city').split('-')[0]
        for province, cities in d.items():
            if job_city in cities or job_city + '市' in cities:
                found = True
                province_ = province.strip('省市自治区回族维吾尔壮')
                province_count[province_] += 1
                break
        if not found:
            print('province not found', job_city)

    dd = dict(province_count)
    for k, v in dd.items():
        print(k, v)


def func3():
    keyword = 'python'
    jobs_all = get_jobs_by_keyword(keyword)
    full_text = ''
    for job in jobs_all:
        info = [
            job.get('jobType'),
            job.get('jobName'),
            job.get('eduLevel'),
            job.get('city')
        ]
        text = ' '.join(info)
        welfare = job.get('welfare')
        text += ' '.join(welfare)
        skills = job.get('extractSkillTag')
        text += ' '.join(skills)
        full_text += text

    cut_text = ' '.join(jieba.cut(full_text))
    from wordcloud import WordCloud
    wordcloud = WordCloud(font_path='C:/Windows/Fonts/simhei.ttf').generate(cut_text)
    wordcloud.to_file('/static/{}_wordcloud.jpg'.format(keyword))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()


def func4():
    'http://127.0.0.1:5000/analysis/python'
    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')

    pdfkit.from_url('http://127.0.0.1:5000/salary/python', 'out.pdf', configuration=config)

if __name__ == '__main__':
    func4()
