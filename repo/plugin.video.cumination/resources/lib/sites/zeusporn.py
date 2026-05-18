'''
    Cumination
    Copyright (C) 2023 Cumination

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
import xbmc
import xbmcgui
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite('zeusporn', "[COLOR hotpink]ZeusPorn[/COLOR]", 'https://zeusporn.com/', 'zeusporn.png', 'zeusporn')
sort_orders = {'Most recent': 'most-recent/', 'Most discussed': 'most-discussed/', 'Most viewed': 'most-viewed/', 'Top rated': 'top-rated/', 'Longest': 'longest/'}

@site.register(default_mode=True)
def Main():
    order = utils.addon.getSetting('zeuspornsortorder') if utils.addon.getSetting('zeuspornsortorder') else 'most-recent/'
    ordername = list(sort_orders.keys())[list(sort_orders.values()).index(order)]
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'search/videos/', 'Search', site.img_search)
    site.add_dir('[COLOR hotpink]Sort Order: [/COLOR] [COLOR orange]{}[/COLOR]'.format(ordername), site.url, 'Sortorder', site.img_cat)
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url, 'ShowCategories', site.img_cat)
    List(site.url + order)
    utils.eod()

@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    if 'the requested search cannot be found' in html:
        utils.notify(msg='Nothing found')
        utils.eod()
        return

    delimiter = '<div class="content '
    re_videopage = '<a href="([^"]+)"'
    re_name = 'title="([^"]+)"'
    re_img = '<img.+?src="([^"]+)"'
    re_duration = '<div class="text">.*?<span class="left">.*?([0-9,:]+).*?<'

    utils.videos_list(site, 'zeusporn.Play', html, delimiter, re_videopage, re_name, re_img, re_duration=re_duration, contextm='zeusporn.Related')

    re_npurl = r'<a href=\'([^\']+)\' class="next" allowpop="false">N'
    re_npnr = r'<a href=\'page(\d+)\.html\' class="next" allowpop="false">N'
    
    current_url = url
    if url.endswith(".html"):
        current_url = url[:url.rfind('/')]
    else:
        current_url = url[:-1]
    
    match = re.compile(re_npurl, re.DOTALL | re.IGNORECASE).findall(html)     
    if match:       
        npurl = (current_url + '/' + match[0]).replace('&amp;', '&')
        np = ''
        npnr = 0
        if re_npnr:
            match = re.compile(re_npnr, re.DOTALL | re.IGNORECASE).findall(html)
            if match:
                npnr = match[0]
                np = npnr
        if np:
            np = '(' + np + ')'

        site.add_dir('Next Page {}'.format(np), npurl, 'zeusporn.List')

    utils.eod()

@site.register()
def ShowCategories(url):
    html = utils.getHtml(url)
    
    pattern = re.compile(r'<div class="header">Channels<\/div>(.*?)</div>', re.DOTALL | re.IGNORECASE)
    menu = re.search(pattern, html)
    pattern = re.compile(r'<li>.*?<a href=.([^\']+).>([^<]+)<.a>', re.DOTALL | re.IGNORECASE)
    for (categoryUrl, categoryName) in re.findall(pattern, menu.group(1)):
        site.add_dir(categoryName, categoryUrl, 'List',  '', '')
    utils.eod()

@site.register()
def Play(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videopage = utils.getHtml(url, site.url)
    videolink = re.compile(r'<source.+?src="([^"]+)', re.DOTALL | re.IGNORECASE).findall(videopage)[0]
    vp.progress.update(75, "[CR]Loading video page[CR]")
    vp.play_from_direct_link(videolink)

@site.register()
def Related(url):
    contexturl = (utils.addon_sys + "?mode=" + str('zeusporn.List') + "&url=" + urllib_parse.quote_plus(url))
    xbmc.executebuiltin('Container.Update(' + contexturl + ')')

@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        url = "{0}{1}/".format(url, keyword.replace(' ', '-'))
        List(url)

@site.register()
def Sortorder(url):
    order = utils.selector('Select category', sort_orders.keys())
    if order:
        utils.addon.setSetting('zeuspornsortorder', sort_orders[order])
        Main()