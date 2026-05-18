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
from resources.lib import utils
from resources.lib.adultsite import AdultSite
import xbmc

BASE_URL = 'https://www.sickjunk.com/'

site = AdultSite('sickjunk', '[COLOR hotpink]SickJunk[/COLOR]', BASE_URL, 'sickjunk.png', 'sickjunk')

@site.register(default_mode=True)
def Main():
    
#    site.add_dir('[COLOR hotpink]Sort Order: [/COLOR] [COLOR orange]{}[/COLOR]'.format(ordername), site.url, 'Sortorder', site.img_cat)
#    site.add_dir('[COLOR hotpink]Categories[/COLOR]', BASE_URL + '/categories/', 'ShowCategories')
    site.add_dir('[COLOR hotpink]Search[/COLOR]', '{0}?s='.format(site.url), 'Search', site.img_search)
    List(BASE_URL)

@site.register()
def List(url):
    html = utils.getHtml(url)
    
    pattern = re.compile(r'<article.+?<figure.+?<a.+?href="([^"]+).+?title="([^"]+).+?<img.+?src="([^"]+)', re.DOTALL | re.IGNORECASE)

    for (pageurl, videoname, iconimage) in re.findall(pattern, html):
        site.add_download_link(videoname, pageurl, 'Play', iconimage, desc=videoname)

    re_npurl = r'<a\sclass="next.+?href="([^"]+).+Next'
    re_npnr = r'<a\sclass="next.+?href="[^"]+?(\d+)/.+Next'
    re_lpnr = r'page-numbers\sdots.+?href=".+?>(\d+)'
    utils.next_page(site, 'sickjunk.List', html, re_npurl, re_npnr=re_npnr, re_lpnr=re_lpnr)
    utils.eod()
    
@site.register()
def Play(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(18, "[CR]Loading video page[CR]")
    videopage = utils.getHtml(url, '')
    videolink = re.compile(r'<video.+?src="([^"]+)', re.DOTALL | re.IGNORECASE).findall(videopage)[0]
    vp.play_from_direct_link(videolink)

@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        url = "{0}{1}".format(url, keyword.replace(' ', '+'))
        utils.kodilog(url)
        List(url)
#@site.register()
#def ShowCategories(url):
#    html = utils.getHtml(url)
#    pattern = re.compile(r'category">.+?<a href="([^"]+).+?>.+?src="([^"]+).+?alt="([^"]+)', re.DOTALL | re.IGNORECASE)

#    for (categoryUrl, categoryIcon, categoryName) in re.findall(pattern, html):
#        site.add_dir(categoryName, BASE_URL + categoryUrl, 'List',  BASE_URL + categoryIcon, '')
#    utils.eod()

#@site.register()
#def Sortorder(url):
#    sort_orders = {'Recent Uploads': 'recent/', 'Most Viewed': 'most_viewed/', 'Top Rated': 'top_rated/'}
#    order = utils.selector('Select category', sort_orders.keys())
#    if order:
#        utils.addon.setSetting('heavyrsortorder', sort_orders[order])
#        Main()

#@site.register()
#def Search(url, keyword=None):
#    if not keyword:
#        site.search_dir(url, 'Search')
#    else:
#        formdata = {'keyword': keyword, 'handler': 'search', 'action': 'do_search'}
#        html = utils.postHtml(url, form_data=formdata)
#        
#        pattern = re.compile(r'<div class="row">.*?<div.+?>.*?<a href="([^"]+)".class="image">.+?<img.+?src="([^"]+).+?alt="([^"]+)".+?>.+?<i class=".*?fa-clock-o"><\/i>.*?([0-9,:]+)<\/span>', re.DOTALL | re.IGNORECASE)
#
#        for (pageurl, iconimage, videoname, duration) in re.findall(pattern, html):
#            site.add_download_link(videoname, BASE_URL + pageurl, 'Play', iconimage, desc=videoname, duration=duration)
#
#        re_npurl = r'href="([^"]+)">Next<\/a>'
#        re_npnr = r'_(\d+)\.html">Next<\/a>'
#        re_lpnr = r'_(\d+)\.html">Last<\/a>'
#        utils.next_page(site, 'heavy-r.ListResults', html, re_npurl, re_npnr=re_npnr, re_lpnr=re_lpnr)
#        utils.eod()

#@site.register()
#def ListResults(url):
#    html = utils.getHtml(url)
    
#    pattern = re.compile(r'<div class="row">.*?<div.+?>.*?<a href="([^"]+)".class="image">.+?<img.+?src="([^"]+).+?alt="([^"]+)".+?>.+?<i class=".*?fa-clock-o"><\/i>.*?([0-9,:]+)<\/span>', re.DOTALL | re.IGNORECASE)

#    for (pageurl, iconimage, videoname, duration) in re.findall(pattern, html):
#        site.add_download_link(videoname, BASE_URL + pageurl, 'Play', iconimage, desc=videoname, duration=duration)

#    re_npurl = r'href="([^"]+)">Next<\/a>'
#    re_npnr = r'_(\d+)\.html">Next<\/a>'
#    re_lpnr = r'_(\d+)\.html">Last<\/a>'
#    utils.next_page(site, 'heavy-r.ListResults', html, re_npurl, re_npnr=re_npnr, re_lpnr=re_lpnr)
#    utils.eod()