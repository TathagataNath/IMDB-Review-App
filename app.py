from flask import Flask, render_template, request
import requests
from beautifulscraper import BeautifulSoup
import re
import pickle
import preprocessing as ppr
import pandas as pd
import nltk

app = Flask(__name__)
p=None
l=None

model=pickle.load(open('model.pkl', 'rb'))
features=pickle.load(open('features.pkl', 'rb'))


@app.route('/')
def home():
    global p
    global l
    p=0
    l=[]
    return render_template("SentimentAnalyser.html")

def find_results(keyword):
    global l

    response = requests.get('https://www.imdb.com/find?q={}&s=tt&ref_=fn_al_tt_mr'.format(keyword)).text

    soup = BeautifulSoup(response, 'lxml')

    n = 1

    for i in soup.find_all('tr'):

        x = i.find_all('td')[1]

        j = x.text

        if re.search(keyword, j, re.IGNORECASE) and not re.search('\([A-Za-z]+\)', j):
            id_num = x.find('a').get('href').split('/')[2]

            l.append(("https://www.imdb.com/title/{}/?ref_=fn_tt_tt_{}".format(id_num, n),"https://www.imdb.com/title/{}/reviews?ref_=tt_urv".format(id_num)))

        n += 1

def get_count(review_list) :

    count_list=[]

    for i in review_list :

        temp=[]

        for j in features :

            temp.append(i.count(j))

        count_list.append(temp)

    return count_list

@app.route('/search/<index>/', methods=["POST", "GET"])
def search(index):

    global l
    length=0
    sentiment=""

    if l == [] and index == 'stay':
        keyword = request.form.get('keyword')
        if keyword :
            find_results(keyword)

    if l!=[] :

        s=''
        length=len(l)
        if length>1 :
            s='S'

        msg='{} RESULT{} FOUND'.format(length,s)

        global p
        info_list=[]

        if index=='previous' :
            if p!=0 :
                p-=1

        elif index=='next' :
            if p!=len(l)-1 :
                p+=1

        if p==0 :
            button_previous='disabled'
        else :
            button_previous='active'

        if p==len(l)-1 :
            button_next='disabled'
        else :
            button_next='active'
        response = requests.get(l[p][0]).text
        soup = BeautifulSoup(response, 'lxml')
        try:
            src = soup.find('div', class_='poster').find('a').find('img').get('src')
        except:
            src = ""

        info = soup.find('div', class_='title_wrapper')

        try :
            title = info.find('h1').text.strip()
        except :
            title=""
        try :
            subinfo = info.find('div', class_='subtext').text.strip()
        except :
            subinfo=""

        try :
            rating=soup.find('div', class_='ratingValue').text.strip()
        except :
            rating=""

        reviews=requests.get(l[p][1]).text
        soup=BeautifulSoup(reviews, 'lxml')

        reviews=soup.find_all('div', class_='lister-item-content')
        review_process=[]

        for i in reviews :
            temp=[]
            try :
                rate=i.find('div', class_='ipl-ratings-bar').text.strip()
            except :
                rate=""
            temp.append(rate)
            try :
                heading=i.find('a').text.strip()
            except :
                heading=""
            temp.append(heading)
            try :
                name_date=i.find('div', class_='display-name-date')
                for j in name_date.find_all('span') :
                    temp.append(j.text.strip())
            except :
                temp.append("")
            try :
                content=i.find('div', class_='text show-more__control').text.strip()
            except :
                content=""
            temp.append(content)
            review_process.append(content)


            info_list.append(temp)


        data=pd.DataFrame(info_list, columns=["rate", "heading", "name", "date", "content"])

        review_list=ppr.preprocess(review_process)

        if review_list != [] :

            count_list=get_count(review_list)
            prediction=model.predict(count_list)
            data['prediction'] = prediction
            sentiment = round(((data[data['prediction'] == 1].shape[0] / data.shape[0]) * 10), 1)

        rows=data.shape[0]

    return render_template("result.html", **locals())

if __name__ == "__main__":
    app.jinja_env.auto_reload=True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(debug=True)
