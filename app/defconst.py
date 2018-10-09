#!/usr/bin/env python3

expires = '5'

url = {
    'login'      :  'https://bbcsulb.desire2learn.com/d2l/lp/auth/login/login.d2l',
    'oauth_token':  'https://bbcsulb.desire2learn.com/d2l/lp/auth/oauth2/token',
    'authjs'     :  'https://s.brightspace.com/lib/d2lfetch-auth/0.9.0/d2lfetch-auth.js',
    'csulb_html' :  'https://bbcsulb.desire2learn.com/shared/CSULB.html',
    'enroll'     :  'https://eeaeba25-6163-466c-bed6-1a47b6b0cecc.enrollments.api.brightspace.com',
    'liveagent'  : ('https://d.la1-c1-yhu.salesforceliveagent.com/chat/rest/System/MultiNoun.jsonp'
                    '?nouns=VisitorId,Settings'
                    '&VisitorId.prefix=Visitor'
                    '&Settings.prefix=Visitor'
                    '&Settings.buttonIds=[{0}]'
                    '&Settings.updateBreadcrumb=1'
                    '&Settings.urlPrefix=undefined'
                    '&callback=liveagent._.handlePing'
                    '&deployment_id={1}'
                    '&org_id={2}'
                    '&version=43'),
    'news'       :  'https://bbcsulb.desire2learn.com/d2l/lms/news/main.d2l?ou={}',
    'content'    :  'https://bbcsulb.desire2learn.com/d2l/le/content/{}/Home'
}

login = {
    'd2l_referrer': '',
    'loginPath'   : '/d2l/login',
    'userName'    : None,
    'password'    : None
}

la_cookies = {
    'liveagent_oref': 'https://bbcsulb.desire2learn.com/d2l/home',
    'liveagent_ptid': '',
    'liveagent_sid' : '',
    'liveagent_vc'  : '2'
}
