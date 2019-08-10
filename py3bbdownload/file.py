#!/usr/bin/env python3
import re
from os.path import join
from bs4 import BeautifulSoup

# Self-defined scripts
import v
from const import curls
from err import json_par, json_chk, re_chk, get_chk, weird_err


class File:
    def __init__(self, name, rel_link, mod):
        v.log_file.pvlog('-' * 4)
        v.log_file.pvlog('Start file construction')
        self._name = safe_name(name)
        id = int(rel_link.split('/')[-2])
        self._link = curls['fl'].format(mod.cour_id, id)
        self._dl_link = curls['fl_dl'].format(mod.cour_id, id)
        self._folder = mod.path
        self._cour_path = mod.cour_path

    @property
    def name(self):
        return self._name

    @property
    def link(self):
        return self._link

    @property
    def dl_link(self):
        return self._dl_link

    @property
    def folder(self):
        return self._folder

    @property
    def cour_path(self):
        return self._cour_path


class Overview(File):
    def __init__(self, cour):
        v.log_file.pvlog('-' * 4)
        v.log_file.pvlog('Start overview file construction')
        self._name = 'Overview'     # Extension from download
        self._link = self._dl_link = curls['ov_dl'].format(cour.id)
        self._folder = cour.path
        self._cour_path = cour.path


class Module:
    def __init__(self, id, name, pare_path, cour):
        v.log_file.pvlog('Start module construction')
        self._id = id
        self._cour_id = cour.id
        self._name = safe_name(name)
        self._path = join(pare_path, self._name)
        self._cour_path = cour.path
        self._get_files()
        cour.add_files(self._files)

    def _get_files(self):
        content_bytes = get_chk(
            curls['module'].format(self._cour_id), 'Mod',
            params={'mId': self._id, 'writeHistoryEntry': 1, }
            )[9:]
        payload_j = json_par(content_bytes, 'Mod load')
        payload = json_chk(('Payload', ), payload_j, name='Mod load')
        content = json_chk(('Html', ), payload, name='Mod html')
        # Parse original
        soup_content = BeautifulSoup(content, features='html.parser').ul
        soup_list = soup_content.find_all('li', recursive=False)
        # Check more
        more_ev_mat = re.search(br'ExclusiveValue\\":(\d+)\D', content_bytes)
        if more_ev_mat is not None:
            # Load more
            soup_list += self._get_more(more_ev_mat)
        # Create file objects
        self._files = []
        for element in soup_list:
            if element.find('div', {'class': 'd2l-collapsepane', }):
                # This is a module. Skip
                continue
            # This is a file
            a = element.a
            if a is None:
                # Some <li>'s are suspiciously blank
                continue
            link = a['href']
            name = a.text
            self._files.append(File(name, link, self))

    def _get_more(self, more_ev_mat):
        soup_list = []
        more_ev = int(more_ev_mat[1])
        more_url = curls['more'].format(self._cour_id)
        while True:
            content_bytes = get_chk(
                more_url, 'More',
                params={
                    'mId': self._id,
                    'si$SortField': 'SortOrder',
                    'si$IsAscending': True,
                    'si$ExclusiveValue': more_ev,
                    'itemParams$ShowAddUnit': True,
                    'itemParams$ShowStatusControl': True,
                    'itemParams$ShowRestrictions': True,
                    'itemParams$ShowCompletionSelector': True,
                    'itemParams$ShowDescriptions': True,
                    'itemParams$HasDragAndDrop': True,
                    'itemParams$ShowContextMenu': True,
                    'itemParams$ModuleViewMode': 2,
                    'itemParams$HasPaging': True,
                    'itemParams$IsPrint': False,
                    'itemParams$PublishStatusReadOnly': True,
                    'itemParams$IsSchedule': False,
                    'isInEditAllTitlesMode': False,
                    }
                )[9:]
            payload_j = json_par(content_bytes, name='More load')
            payload = json_chk(('Payload', ), payload_j, name='More load')
            content = json_chk(('Html', ), payload, name='More html')
            if not content:
                # No more data
                return soup_list
            soup_content = BeautifulSoup(content, features='html.parser')
            soup_list += soup_content.find_all('li', recursive=False)
            # Load next
            more_ev += 40

    @property
    def name(self):
        return self._name

    @property
    def files(self):
        return self._files

    @property
    def path(self):
        return self._path

    @property
    def cour_id(self):
        return self._cour_id

    @property
    def cour_path(self):
        return self._cour_path


class Course:
    def __init__(self, link):
        v.log_file.pvlog('-' * 15)
        v.log_file.pvlog('Start course construction')
        self._get_id(link)
        self._get_name(link)
        self._path = self._name
        self._files = []
        self._get_urls()

    def _get_id(self, link):
        v.log_file.pvlog('-' * 10)
        v.log_file.pvlog('Getting course ID')
        self._id = re_chk(r'com/(\d+)$', link, 'Intro link')[1]
        v.log_file.pvlog('Course ID got')

    def _get_name(self, link):
        v.log_file.pvlog('-' * 10)
        v.log_file.pvlog('Getting course name')
        info = get_chk(link, 'Course name', headers=v.auth_head)
        prop_j = json_par(info, 'Properties')
        prop = json_chk(('properties', ), prop_j, name='Properties')
        name = json_chk(('name', ), prop, name='Name')
        self._name = safe_name(name)
        v.log_file.pvlog('Course name got')

    def _get_urls(self):
        v.log_file.pvlog('-' * 10)
        v.log_file.pvlog('Getting course URLs')
        content_url = curls['content'].format(self._id)
        v.log_file.pvlog('Course home URL got')
        content = get_chk(content_url, 'Course home')
        v.log_file.pvlog('Course home got')
        # Overview
        self._get_ov(content)
        # Content
        self._get_modules(content)

    def _get_ov(self, content):
        # Overview
        v.log_file.pvlog('Getting overview')
        if b'Overview</h2>' in content:
            self._ov = Overview(self)
            v.log_file.pvlog('Overview got')
            return
        # No overview
        self._ov = None
        v.log_file.pvlog('No overview!')

    def _get_modules(self, content):
        # Content
        v.log_file.pvlog('Getting content')
        # Parse URL for all files
        soup_all = BeautifulSoup(content, features='html.parser')
        soup_main = soup_all.find('ul', {'id': 'D2L_LE_Content_TreeBrowser', })
        soup_blocks = soup_main.find_all('li', recursive=False)[1:]
        v.log_file.pvlog('Content modules list got')
        # Parse block recursively
        modules = self._parse_soup_blocks(soup_blocks, self._path)
        v.log_file.pvlog('-' * 8)
        v.log_file.pvlog('Content hierachy got')
        self._modules = modules

    def _parse_soup_blocks(self, blocks, parent_path):
        v.log_file.pvlog('-' * 8)
        v.log_file.pvlog('Start block parsing')
        content = []
        for block in blocks:
            v.log_file.pvlog('-' * 6)
            id = re_chk(r'-(\d+)$', block['data-key'], 'Mod ID')[1]
            v.log_file.pvlog('Module ID found')
            children = list(block.children)
            name = children[0].find('div', {'class': 'd2l-textblock', }).text
            v.log_file.pvlog('Module name found')
            mod = Module(id, name, parent_path, self)
            content.append(mod)
            if len(children) == 1:
                # No submodules
                v.log_file.pvlog('No submodule found')
            elif len(children) == 2:
                # With submodules
                v.log_file.pvlog('Submodules found')
                sub_blocks = children[1].find_all('li', recursive=False)
                content += self._parse_soup_blocks(sub_blocks, mod.path)
            else:
                # I dunno what happened
                weird_err(len(children)+'>2 children in content table')
        return content

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def modules(self):
        return self._modules

    @property
    def path(self):
        return self._path

    @property
    def ov(self):
        return self._ov

    @property
    def files(self):
        return self._files

    def add_files(self, files):
        self._files += files


def safe_name(name):
    return re.sub(r'[\\/\'\"[\]*:;,|=]', '', name)
