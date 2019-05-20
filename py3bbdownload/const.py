#!/usr/bin/env python3
from os.path import join
from datetime import datetime

cs = 1024 * 1024    # 1 MiB
time = datetime.now().strftime('%Y%m%d%H%M%S')

base_url = 'https://bbcsulb.desire2learn.com'
cnt_url = base_url + '/d2l/le/content/'

cdirs = {
    'data_folder': 'data',
    'tmp_folder': '.tmp',
    'cont_folder': 'contents',
    'log_folder': 'logs'
    }

cfiles = {
    'data_file': join(cdirs['data_folder'], 'data.json'),
    'fail_file': join(cdirs['data_folder'], 'fail.txt'),
    'new_file': join(cdirs['data_folder'], 'new.txt'),
    'upd_file': join(cdirs['data_folder'], 'upd.txt'),
    }

curls = {
    'login': base_url + '/d2l/lp/auth/login/login.d2l',
    'token': base_url + '/d2l/lp/auth/oauth2/token',
    'bsi': ('https://s.brightspace.com/lib/bsi/20.19.4-40/es6-bundled/'
            'web-components/bsi.js'),
    'courses': ('https://eeaeba25-6163-466c-bed6-1a47b6b0cecc.enrollments.'
                'api.brightspace.com/users/'),
    'content': cnt_url + '{}/Home',
    'module': cnt_url + '{}/ModuleDetailsPartial',
    'more': cnt_url + '{}/datalist/LoadMoreModuleContents',
    'ov_dl': cnt_url + '{}/courseInfo/DownloadHomepage?displayInBrowser=0',
    'fl': cnt_url + '{0}/viewContent/{1}/View',
    'fl_dl': cnt_url + '{0}/topics/files/download/{1}/DirectFileTopicDownload',
    }


def plur(num, noun, add='s'):
    tmp = str(num) + ' ' + noun
    return tmp if num == 1 else tmp + add
