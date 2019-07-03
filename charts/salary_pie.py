import os

import pymongo
import numpy as np
import matplotlib.pyplot as plt

from collections import OrderedDict
from bson.objectid import ObjectId


plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

client = pymongo.MongoClient()
items = client.JobInfo.zhilian


#
def get_job_by_id(id):
    pattern = {
        '_id': ObjectId(id)
    }
    return items.find_one(pattern)


# 通过关键字获取职位列表
def get_jobs_by_keyword(keyword):
    pattern = {'$or': [
        {'jobName': {'$regex': '.*{}.*'.format(keyword), '$options': 'i'}},
        {'jobType': {'$regex': '.*{}.*'.format(keyword), '$options': 'i'}},
    ]}
    # 获取职位
    r = items.find(pattern)
    return list(r)


# 获取工资分布
def get_salary_distribution_by_salary(jobs):
    labels = ['4.5k以下', '4.5k-6k', '6k-8k', '8k-10k', '10k-15k', '15k以上']
    distr_dict = OrderedDict()
    for label in labels:
        distr_dict[label] = 0
    for job in jobs:
        salary = job.get('salary')
        if len(salary) != 2:
            continue
        if salary[0] == 0:
            salary[0] = salary[1] * 0.7
        avg_salary = (salary[0] + salary[1]) / 2
        if avg_salary < 4500:
            distr_dict['4.5k以下'] += 1
        elif 4500 <= avg_salary < 6000:
            distr_dict['4.5k-6k'] += 1

        elif 6000 <= avg_salary < 8000:
            distr_dict['6k-8k'] += 1

        elif 8000 <= avg_salary < 10000:
            distr_dict['8k-10k'] += 1

        elif 10000 <= avg_salary < 15000:
            distr_dict['10k-15k'] += 1

        elif avg_salary > 15000:
            distr_dict['15k以上'] += 1

    return distr_dict


# 绘制工资分布饼图
def get_salary_pie(distr_dict, keyword):
    figure_path = 'static/{}_pie.png'.format(keyword)
    image_url = '/' + figure_path
    if os.path.exists(figure_path):
        return image_url
    labels = list(distr_dict.keys())
    values = list(distr_dict.values())
    fig, ax = plt.subplots(figsize=(7, 5), subplot_kw=dict(aspect="equal"))

    def func(pct, allvals):
        absolute = int(pct / 100. * np.sum(allvals))
        return "{:.1f}%\n".format(pct, absolute)

    wedges, texts, autotexts = ax.pie(values, autopct=lambda pct: func(pct, values),
                                      textprops=dict(color="w"))
    ax.legend(wedges, labels,
              title="工资区间",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))
    plt.setp(autotexts, size=8, weight="bold")
    ax.set_title('含有关键字"{}"的职位的工资分布图'.format(keyword))
    plt.savefig(figure_path)
    return image_url


# 按照工作经验获取工资分布
def get_salary_distribution_by_exp(jobs):
    distr_dict = OrderedDict()
    labels = ['无经验', '1年以下', '1-3年', '3-5年', '5-10年', '10年以上', '不限']
    for label in labels:
        distr_dict[label] = [0, 0]

    exps = ['无经验', '不限', '1年以下', '10年以上']
    exps2 = [[1, 3], [3, 5], [5, 10]]
    for job in jobs:
        exp = job.get('workingExp')
        salary = job.get('salary')
        if len(salary) != 2:
            print('salary format unknown:', salary)
            continue
        if salary[0] == 0:
            salary[0] = salary[1] * 0.7
        avg_salary = (salary[0] + salary[1]) / 2

        if isinstance(exp, str):
            if exp not in exps:
                print('not in exps:', exp)
                continue
            distr_dict[exp][0] += 1
            distr_dict[exp][1] += avg_salary

        elif isinstance(exp, list) and len(exp) == 2:
            if exp not in exps2:
                print('not in exps2:', exp)
                continue
            if exp == [1, 3]:
                distr_dict['1-3年'][0] += 1
                distr_dict['1-3年'][1] += avg_salary

            elif exp == [3, 5]:
                distr_dict['3-5年'][0] += 1
                distr_dict['3-5年'][1] += avg_salary

            elif exp == [5, 10]:
                distr_dict['5-10年'][0] += 1
                distr_dict['5-10年'][1] += avg_salary

        else:
            print('格式不符:', type(exp), exp, len(exp))

    del_list = []
    for k, v in distr_dict.items():
        if v[1] == 0:
            del_list.append(k)
        else:
            distr_dict[k] = int(v[1] / v[0])
    for k in del_list:
        del distr_dict[k]
    return distr_dict


def get_salary_exp_line(distr_dict, keyword):
    figure_path = 'static/{}_line.png'.format(keyword)
    image_url = '/' + figure_path
    if os.path.exists(figure_path):
        return image_url
    names = list(distr_dict.keys())
    values = list(distr_dict.values())
    plt.figure()
    plt.plot(names, values)
    plt.xlabel('工作经验')
    plt.ylabel('平均薪资')
    plt.title('含有关键字"{}“的职位的薪资水平和工作年限的关系折线图'.format(keyword))
    plt.savefig(figure_path)
    return image_url

def get_salary_exp_bar(distr_dict, keyword):
    figure_path = 'static/{}_salary_exp_bar.png'.format(keyword)
    image_url = '/' + figure_path
    if os.path.exists(figure_path):
        return image_url
    names = list(distr_dict.keys())
    values = list(distr_dict.values())
    plt.figure()
    plt.bar(names, values)
    plt.xlabel('工作经验')
    plt.ylabel('平均薪资')
    plt.title('含有关键字"{}“的职位的薪资水平和工作年限的关系折线图'.format(keyword))
    plt.savefig(figure_path)
    return image_url


def get_salary_distribution_by_edu(jobs):
    edus = ['中技', '中专', '高中', '大专', '本科', '硕士', '博士', '不限']
    distr_dict = OrderedDict()
    for edu in edus:
        distr_dict[edu] = [0, 0]
    for job in jobs:
        edu_level = job.get('eduLevel')
        if edu_level not in edus:
            print('unkown edu_level:', edu_level)
            continue
        salary = job.get('salary')
        if len(salary) != 2:
            print('salary format unknown:', salary)
            continue
        if salary[0] == 0:
            salary[0] = salary[1] * 0.7
        avg_salary = (salary[0] + salary[1]) / 2

        distr_dict[edu_level][0] += 1
        distr_dict[edu_level][1] += avg_salary

    del_list = []
    for k, v in distr_dict.items():
        if v[0] == 0:
            del_list.append(k)
            continue
        distr_dict[k] = int(v[1] / v[0])
    # 删除职位为0的学历
    for k in del_list:
        del distr_dict[k]
    return distr_dict


def get_salary_edu_bar(distr_dict, keyword):
    figure_path = 'static/{}_salary_edu_bar.png'.format(keyword)
    image_url = '/' + figure_path
    if os.path.exists(figure_path):
        return image_url
    names = list(distr_dict.keys())
    values = list(distr_dict.values())
    plt.figure()
    plt.bar(names, values)
    plt.xlabel('学历')
    plt.ylabel('平均薪资')
    plt.title('含有关键字"{}“的职位的薪资水平和学历的关系柱状图'.format(keyword))
    plt.savefig(figure_path)
    return image_url


def get_percentage_by_edu(jobs):
    edus = ['中技', '中专', '高中', '大专', '本科', '硕士', '博士', '不限']
    distr_dict = OrderedDict()
    for edu in edus:
        distr_dict[edu] = 0
    for job in jobs:
        edu_level = job.get('eduLevel')
        if edu_level not in edus:
            print('unkown edu_level:', edu_level)
            continue
        distr_dict[edu_level] += 1
    del_list  = []
    for k, v in distr_dict.items():
        if v == 0:
            del_list.append(k)
    for k in del_list:
        del distr_dict[k]
    return distr_dict


def get_percent_edu_pie(distr_dict, keyword):
    figure_path = 'static/{}_percent_edu_pie.png'.format(keyword)
    image_url = '/' + figure_path
    if os.path.exists(figure_path):
        return image_url
    labels = list(distr_dict.keys())
    values = list(distr_dict.values())
    fig, ax = plt.subplots(figsize=(7, 5), subplot_kw=dict(aspect="equal"))

    def func(pct, allvals):
        absolute = int(pct / 100. * np.sum(allvals))
        return "{:.1f}%\n".format(pct, absolute)

    wedges, texts, autotexts = ax.pie(values, autopct=lambda pct: func(pct, values),
                                      textprops=dict(color="w"))
    ax.legend(wedges, labels,
              title="学历",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))
    plt.setp(autotexts, size=8, weight="bold")
    ax.set_title('含有关键字"{}"的职位的学历要求'.format(keyword))
    plt.savefig(figure_path)
    return image_url


def get_exp(jobs):
    distr_dict = OrderedDict()
    labels = ['无经验', '1年以下', '1-3年', '3-5年', '5-10年', '10年以上', '不限']
    for label in labels:
        distr_dict[label] = 0

    exps = ['无经验', '不限', '1年以下', '10年以上']
    exps2 = [[1, 3], [3, 5], [5, 10]]
    for job in jobs:
        exp = job.get('workingExp')

        if isinstance(exp, str):
            if exp not in exps:
                print('not in exps:', exp)
                continue
            distr_dict[exp] += 1

        elif isinstance(exp, list) and len(exp) == 2:
            if exp not in exps2:
                print('not in exps2:', exp)
                continue
            if exp == [1, 3]:
                distr_dict['1-3年'] += 1

            elif exp == [3, 5]:
                distr_dict['3-5年'] += 1

            elif exp == [5, 10]:
                distr_dict['5-10年'] += 1

        else:
            print('格式不符:', type(exp), exp, len(exp))

    del_list = []
    for k, v in distr_dict.items():
        if v == 0:
            del_list.append(k)
    for k in del_list:
        del distr_dict[k]
    return distr_dict

def get_exp_bar(distr_dict, keyword):
    figure_path = 'static/{}_exp_bar.png'.format(keyword)
    image_url = '/' + figure_path
    if os.path.exists(figure_path):
        return image_url
    names = list(distr_dict.keys())
    values = list(distr_dict.values())
    plt.figure()
    plt.bar(names, values)
    plt.xlabel('工作经验')
    plt.ylabel('岗位数目')
    plt.title('含有关键字"{}“的职位的工作经验要求'.format(keyword))
    plt.savefig(figure_path)
    return image_url


if __name__ == '__main__':
    os.chdir('../')
    keyword = 'java'
    jobs = get_jobs_by_keyword(keyword)
    dist = get_exp(jobs)
    get_exp_bar(dist, keyword)