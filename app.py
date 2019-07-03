import json
from collections import defaultdict

import jieba
import pdfkit
from flask import Flask, request, abort, redirect, url_for, render_template, render_template_string
from flask_paginate import Pagination, get_parameter
from jinja2 import Environment, PackageLoader

from charts.salary_pie import *
from wordcloud import WordCloud

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    types = ['salary', 'job', 'analysis']
    type = request.args.get('type')
    keyword = request.args.get('keyword')
    if type not in types:
        abort(404)
    if type == 'salary':
        return redirect(url_for('salary', keyword=keyword))
    elif type == 'job':
        return redirect(url_for('job', keyword=keyword))
    elif type == 'analysis':
        return redirect(url_for('analysis', keyword=keyword))
    else:
        abort(404)


@app.route('/salary/<string:keyword>')
def salary(keyword):
    jobs = get_jobs_by_keyword(keyword)
    dist = get_salary_distribution_by_salary(jobs)
    pie_url = get_salary_pie(dist, keyword)
    dist_line = get_salary_distribution_by_exp(jobs)
    line_url = get_salary_exp_line(dist_line, keyword)
    return render_template('salary.html', pie_url=pie_url,
                           line_url=line_url,
                           keyword=keyword)


@app.route('/job/<string:keyword>')
def job(keyword):
    page = request.args.get(get_parameter(), type=int, default=1)
    per_page = 20
    start = (page - 1) * per_page
    end = page * per_page
    jobs_all = get_jobs_by_keyword(keyword)
    jobs = jobs_all[start:end]
    pagination = Pagination(
        css_framework='bootstrap4',
        page=page,
        total=len(jobs_all),
        per_page=per_page,
        record_name='jobs')
    return render_template('job_list.html',
                           jobs=jobs,
                           pagination=pagination,
                           keyword=keyword)


@app.route('/job_detail/<string:id>')
def job_detail(id):
    job = get_job_by_id(id)
    return render_template('job_detail.html',
                           job=job)


def get_word_cloud(jobs, keyword):
    jobs_all = jobs
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
    wordcloud = WordCloud(font_path='C:/Windows/Fonts/simhei.ttf', width=600, height=400).generate(cut_text)
    wordcloud.to_file('static/{}_wordcloud.jpg'.format(keyword))


@app.route('/analysis/<string:keyword>')
def analysis(keyword):
    jobs = get_jobs_by_keyword(keyword)
    if not os.path.exists('static/{}_wordcloud.jpg'.format(keyword)):
        get_word_cloud(jobs, keyword)
    wordcloud_path = '/static/{}_wordcloud.jpg'.format(keyword)

    salary_edu_dist = get_salary_distribution_by_edu(jobs)
    salary_edu_bar_url = get_salary_edu_bar(salary_edu_dist, keyword)
    salary_exp_dist = get_salary_distribution_by_exp(jobs)
    salary_exp_bar_url = get_salary_exp_bar(salary_exp_dist, keyword)
    percent_edu = get_percentage_by_edu(jobs)
    percent_edu_pie_url = get_percent_edu_pie(percent_edu, keyword)
    exp = get_exp(jobs)
    exp_bar_url = get_exp_bar(exp, keyword)

    # 绘制地图密度
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
    if len(jobs) == 0:
        multipy = 5000
    else:
        multipy = 5000 // len(jobs)
    for k, v in province_count.items():
        province_count[k] *= (v * multipy)
    return render_template('analysis.html',
                           url1=salary_edu_bar_url,
                           url2=salary_exp_bar_url,
                           url3=percent_edu_pie_url,
                           url4=exp_bar_url,
                           url5=wordcloud_path,
                           keyword=keyword,
                           province_count=province_count,
                           multipy=multipy)


@app.route('/test')
def func4(keyword='python'):
    jobs = get_jobs_by_keyword(keyword)
    if not os.path.exists('static/{}_wordcloud.jpg'.format(keyword)):
        get_word_cloud(jobs, keyword)
    wordcloud_path = '/static/{}_wordcloud.jpg'.format(keyword)

    salary_edu_dist = get_salary_distribution_by_edu(jobs)
    salary_edu_bar_url = get_salary_edu_bar(salary_edu_dist, keyword)
    salary_exp_dist = get_salary_distribution_by_exp(jobs)
    salary_exp_bar_url = get_salary_exp_bar(salary_exp_dist, keyword)
    percent_edu = get_percentage_by_edu(jobs)
    percent_edu_pie_url = get_percent_edu_pie(percent_edu, keyword)
    exp = get_exp(jobs)
    exp_bar_url = get_exp_bar(exp, keyword)

    # 绘制地图密度
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
    multipy = 5000 // len(jobs)
    for k, v in province_count.items():
        province_count[k] *= (v * multipy)

    html = render_template('analysis.html',
                           url1=salary_edu_bar_url,
                           url2=salary_exp_bar_url,
                           url3=percent_edu_pie_url,
                           url4=exp_bar_url,
                           url5=wordcloud_path,
                           keyword=keyword,
                           province_count=province_count,
                           multipy=multipy)
    print('a')
    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltoimage.exe')
    print('b')
    pdfkit.from_string(html, 'out.pdf', configuration=config)
    print('c')
    print(html)


if __name__ == '__main__':
    app.run()
