EXPIRES = '5'
HASH = '$2b$12$hOIamWxExZUk4Cdyfljw0.nTEW7.8CUloGYvq1fIe8hh8hCZDu91G'

URL = {
    'LOGIN'       = 'https://bbcsulb.desire2learn.com/d2l/lp/auth/login/login.d2l',
    'OAUTH_TOKEN' = 'https://bbcsulb.desire2learn.com/d2l/lp/auth/oauth2/token',
    'AUTHJS'      = 'https://s.brightspace.com/lib/d2lfetch-auth/0.9.0/d2lfetch-auth.js',
    'CSULB_HTML'  = 'https://bbcsulb.desire2learn.com/shared/CSULB.html',
    'ENROLL'      = 'https://eeaeba25-6163-466c-bed6-1a47b6b0cecc.enrollments.api.brightspace.com',
    'LIVEAGENT'   = ('https://d.la1-c1-yhu.salesforceliveagent.com/chat/rest/System/MultiNoun.jsonp'
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
    'NEWS'        = 'https://bbcsulb.desire2learn.com/d2l/lms/news/main.d2l?ou={}',
    'CONTENT'     = 'https://bbcsulb.desire2learn.com/d2l/le/content/{}/Home'
}

LOGIN_DATA = {
    'd2l_referrer': '',
    'loginPath'   : '/d2l/login',
    'userName'    : None,
    'password'    : None
}

COOKIES = {
    'liveagent_oref': 'https://bbcsulb.desire2learn.com/d2l/home',
    'liveagent_ptid': '',
    'liveagent_sid' : '',
    'liveagent_vc'  : '2'
}
