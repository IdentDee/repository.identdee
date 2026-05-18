'''
    Cumination
    Copyright (C) 2019 Cumination

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re

from resources.lib import utils
from resources.lib.adultsite import AdultSite
from urllib.parse import unquote
import html

site = AdultSite('eroprofile', "[COLOR hotpink]Eroprofile[/COLOR]", 'https://www.eroprofile.com', 'eroprofile.png', 'eroprofile')
BASE_URL = 'https://www.eroprofile.com'


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', BASE_URL + '/m/videos/home', 'Cat', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', '{0}?text='.format(BASE_URL + '/m/videos/home'), 'Search', site.img_search)
    List(BASE_URL + '/m/videos/search?niche=all-sf')
    utils.eod()


@site.register()
def List(url):
    try:
        listhtml = utils.getHtml(url, '')
    except:
        return None

    pattern = re.compile(
    r'<div\s+class="grid-tile-video".?>.?<a\s?href="(?P<url>[^"]+)"\s.*?'
    r'<img\s+src="(?P<thumb>[^"]+)".+?'
    r'<div\sclass="duration">(?P<duration>\d{2}:*\d{2}:*\d*)</div>.*?'
    r'<div\sclass="title.*?>(?P<title>[^<]+)',
    re.DOTALL | re.IGNORECASE
    )

    for match in pattern.finditer(listhtml):
        title = unquote(match.group('title')).title()
        thumb = html.unescape(unquote(match.group('thumb')))
        site.add_download_link(title, BASE_URL + match.group('url'), 'Playvid', thumb, duration=match.group('duration'))

    nav = re.compile(
        r'\s+class="page-nav"\s*>.*?class="active"\s*>(?P<active>[^>]).?</a>.*<a\s+href="(?P<next_slug>.*\?pnum=(?P<next>\d+))"\s+class="m-n">.*?</a>.*?pnum=(?P<last>\d+)',
        re.DOTALL | re.IGNORECASE
    ).search(listhtml)

    if nav:
        label = f'Next Page ({nav.group("next")}/{nav.group("last")})'
        url = html.unescape(nav.group('next_slug'))
        site.add_dir(label, BASE_URL + url, 'List', site.img_next)
    utils.eod()

@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        title = keyword.replace(' ', '+')
        searchUrl = searchUrl + title
        List(searchUrl)

@site.register()
def Cat(url):
    listhtml = utils.getHtml(url, '')

    pattern = re.compile(
        r'<a\s+href="(?P<slug>[^"]+)"\s+class="val-m">(?P<label>[^<]+)</a>',
        re.IGNORECASE)

    for match in pattern.finditer(listhtml):
        site.add_dir(match.group('label'), BASE_URL + match.group('slug'), 'List', '')

    utils.eod()

@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(18, "[CR]Loading video page[CR]")
    videopage = utils.getHtml(url, '')
    videolink = re.compile(r'<source\s*src="([^"]+)"', re.DOTALL | re.IGNORECASE).findall(videopage)[0]
    vp.play_from_direct_link(videolink.replace('https', 'http').replace('&amp;', '&'))
