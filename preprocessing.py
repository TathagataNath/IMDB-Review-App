from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

def remove_special_characters(review_list) :

    new_review_list=[]

    for i in review_list :

        temp=''

        for j in i :
            if j.isalnum() or j==' ' :
                temp+=j

        new_review_list.append(temp)

    return new_review_list

def convert_to_lower(review_list) :

    review_list_lower=[i.lower() for i in review_list]

    return review_list_lower

def remove_stopwords(review_list) :

    new_review_list=[]

    for i in review_list :

        temp=[]

        for j in i.split() :

            if j not in stopwords.words('english') :
                temp.append(j)

        new_review_list.append(temp)

    return new_review_list

def stemming(review_list) :

    ps=PorterStemmer()

    new_review_list=[]

    for i in review_list :

        temp=[]

        for j in i :

            temp.append(ps.stem(j))

        new_review_list.append(temp)

    return new_review_list

def join_back(review_list) :

    review_list_joined=[" ".join(i) for i in review_list]

    return review_list_joined

def preprocess(review_list) :

    review_list=remove_special_characters(review_list)
    review_list=convert_to_lower(review_list)
    review_list=remove_stopwords(review_list)
    review_list=stemming(review_list)
    review_list=join_back(review_list)

    return review_list