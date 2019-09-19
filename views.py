# -*- coding: utf-8 -*-
from django.shortcuts import render
from .models import Post
from college.models import *
from tags.models import bookMark
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 
  
class TwitterClient(object): 

	def __init__(self): 
		consumer_key = 'tvsMCBuerTPmRjF8eXrROK8OD'
		consumer_secret = 'uut2AgIV67H1wM60CWPXvPmsvJhy93bD2T7eV3k9JpKBkRMcwY'
		access_token = '142971949-AyiGMzEH9dNgUtwBpIu5Xx5r87qfctJfE15rMMcX'
		access_token_secret = 'Dx7N6yKjoN6hpBnpzTvyaTCOguZmVD14CWM4COccf6OTV'
		negative="0"
		positive="0"
		neutral="0"
		negative_tweet="negative"
		positive_tweet="positans"
		# attempt authentication 
		try: 
			# create OAuthHandler object 
			self.auth = OAuthHandler(consumer_key, consumer_secret) 
			# set access token and secret 
			self.auth.set_access_token(access_token, access_token_secret) 
			# create tweepy API object to fetch tweets 
			self.api = tweepy.API(self.auth) 
		except: 
 		   print("Error: Authentication Failed") 

	def clean_tweet(self, tweet): 
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()) 

	def get_tweet_sentiment(self, tweet): 
		analysis = TextBlob(self.clean_tweet(tweet)) 
	# set sentiment 
		if analysis.sentiment.polarity > 0: 
			return 'positive'
		elif analysis.sentiment.polarity == 0: 
			return 'neutral'
		else: 
			return 'negative'

	def get_tweets(self, query, count = 10): 
		tweets = [] 

		try: 
	# call twitter api to fetch tweets 
			fetched_tweets = self.api.search(q = query, count = count) 

		# parsing tweets one by one 
			for tweet in fetched_tweets: 
				# empty dictionary to store required params of a tweet 
				parsed_tweet = {} 

				# saving text of tweet 
				parsed_tweet['text'] = tweet.text 
				# saving sentiment of tweet 
				parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text) 

				# appending parsed tweet to tweets list 
				if tweet.retweet_count > 0: 
					# if tweet has retweets, ensure that it is appended only once 
					if parsed_tweet not in tweets: 
						tweets.append(parsed_tweet) 
				else: 
				    tweets.append(parsed_tweet) 

			# return parsed tweets 
			return tweets 

		except tweepy.TweepError as e: 
	# print error (if any) 
			print("Error : " + str(e)) 

	def tweet(): 
		# creating object of TwitterClient Class 
		api = TwitterClient() 
		# calling function to get tweets 
		tweets = api.get_tweets(query = 'Delhi technological university', count = 200) 

		# picking positive tweets from tweets 
		ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 
		# percentage of positive tweets 
		positive="Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets)) 
		# picking negative tweets from tweets 
		ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 
		# percentage of negative tweets 
		negative="Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets))
		# percentage of neutral tweets 
		neutral="Neutral tweets percentage: {} %".format(100*(len(tweets)-len(ntweets)-len(ptweets))/len(tweets))
		# printing first 5 positive tweets 
		positive_tweet="Positive tweets:" 
		for tweet in ptweets[:10]: 
			positive_tweet=positive_tweet+tweet['text'] 

    # printing first 5 negative tweets 
		negative_tweet="Negative tweets:" 
		for tweet in ntweets[:10]: 
			negative_tweet=negative_tweet+tweet['text']

		print (positive_tweet, negative_tweet, neutral)

		return {'positive': positive, 'negative':negative,'neutral':neutral}

def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

def filter(request):
    return render(request, 'blog/filter.html', {'title': 'Select your Pathshala'})

def firstfilter(request):
	tlr=1
	rp=1
	go=1
	oi=1
	if(request.GET.get('TLR')):
		tlr=request.GET.get('TLR')
		rp=request.GET.get('RP')
		go=request.GET.get('GO')
		oi=request.GET.get('OI')

		courseList=course.objects.all()[:10]
		insList=Institute.objects.all().order_by('-rating')[:100]
	else:
		getters = dict(request.GET)

		course_dict = { key: value[0] for key, value in getters.items() if key in [ field.name for field in course._meta.fields] }
		#level=request.GET.get('level_name')
		institute_dict = { key: value[0] for key, value in getters.items() if key in [ field.name for field in Institute._meta.fields] }
		courseList = course.objects.filter(**course_dict)[:1000]
		insList = Institute.objects.filter(**institute_dict).order_by('-rating')[:100]


	current_user=request.user

	bookmark=bookMark.objects.filter(user_id=current_user)

	loc=State.objects.all()
	broadDisc=broadDiscipline.objects.all()
	mode=courseMode.objects.all()
	prog=Programme.objects.all()
	level=courseLevel.objects.all()
	course_insti = []
	for i in insList:
		for c in courseList:
			if(i.uni_id==c.approvingUniversityId):
				Tlrpart1= (((i.Phd_students)*15) + ((i.Total_students)*5))*0.30
				Tlrpart2= (i.ptr)*0.40
				Tlrpart3=((i.Phd_students)/(i.Total_students))*0.30
				Tlrfinal=(Tlrpart1 + Tlrpart2 + Tlrpart3)* int(tlr)

				rppart=(((i.publication)*0.75)+((i.patent)*0.25))*int(rp)
				GO=(i.No_graduates)* int(go)
				OI=(i.student_placed)* int(oi)
				ranking=(Tlrfinal+rppart+GO+OI)
				ans=TwitterClient.tweet()
				course_insti.append((i,c,ranking,ans))


	course_insti.sort(key = lambda x: x[2])  

	#course_insti = [ (i, c) for i in insList for c in courseList if(i.uni_id==c.approvingUniversityId)]
	paginator = Paginator(course_insti, 5) # Show 25 contacts per page
	page = request.GET.get('page')
	courses_instim = paginator.get_page(page)

	params={
		'course_insti': courses_instim,
		'location':loc,
		'broadDiscipline':broadDisc,
		'modeList':mode,
		'programme':prog,
		'levelList':level,
		'bookmarks':bookmark,

	}
	return render(request,'college/courses.html',params)

