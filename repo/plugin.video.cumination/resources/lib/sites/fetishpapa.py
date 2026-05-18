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

site = AdultSite('fetishpapa', "[COLOR hotpink]FetishPapa[/COLOR]", 'https://fetishpapa.com/', 'fetishpapa.png', 'fetishpapa')
cookiehdr = {'Cookie': 'rta_terms_accepted=true'}
#sort_orders = {'Most recent': 'most-recent/', 'Most discussed': 'most-discussed/', 'Most viewed': 'most-viewed/', 'Top rated': 'top-rated/', 'Longest': 'longest/'}

@site.register(default_mode=True)
def Main():
#    order = utils.addon.getSetting('zeuspornsortorder') if utils.addon.getSetting('zeuspornsortorder') else 'most-recent/'
#    ordername = list(sort_orders.keys())[list(sort_orders.values()).index(order)]
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'search/', 'Search', site.img_search)
#    site.add_dir('[COLOR hotpink]Sort Order: [/COLOR] [COLOR orange]{}[/COLOR]'.format(ordername), site.url, 'Sortorder', site.img_cat)
    site.add_dir('[COLOR hotpink]Tubes[/COLOR]', site.url, 'ShowCategories', site.img_cat)
    List(site.url + 'videos/newest/?s=')
    utils.eod()

@site.register()
def List(url):
    html = utils.getHtml(url, site.url, cookiehdr)
    if 'the requested search cannot be found' in html:
        utils.notify(msg='Nothing found')
        utils.eod()
        return

    delimiter = '<!-- START:ALL-->'
    pagelist = re.split(delimiter, html, maxsplit=2)
    html = pagelist[1]

    delimiter = '<div class="pagination"'
    sections = re.split(delimiter, html, maxsplit=1)
    videosection = sections[0]
    paginationsection = sections[1]
    
    delimiter = '<li class="js-pop media-item ">'
    re_videopage = '<a href="([^"]+)"'
    re_name = 'alt="([^"]+)'
    re_img = '<img.+?src="([^"]+)"'
    re_duration = '<span class="media-item__info-item">.*?([0-9,:]+)'
    utils.videos_list(site, 'fetishpapa.Play', videosection, delimiter, re_videopage, re_name, re_img, re_duration=re_duration)
    
    re_npurl = '<a class="rightKey" href="([^"]+)">Next'
    re_npnr = '<a class="rightKey" href=".*?(\d+)/">N'
    re_lpnr = '<a class="rightKey" href=".*?(\d+)/">>'
    
    utils.next_page(site, 'fetishpapa.List', paginationsection, re_npurl, re_npnr, re_lpnr, videos_per_page=None, contextm=None, baseurl=None)

    utils.eod()

@site.register()
def ShowCategories(url):
    html = utils.getHtml(url, headers=cookiehdr)
    
    pattern = re.compile(r'<div class="left-menu-box-title">Tags</div>.*?<ul class="left-menu-box">(.*?)</ul>', re.DOTALL | re.IGNORECASE)
    menu = re.search(pattern, html)
    pattern = re.compile(r'<li>.*?<a href="([^"]+).+?title="([^"]+)', re.DOTALL | re.IGNORECASE)
    categorylist = re.findall(pattern, menu.group(1))
    categorylist.pop(0)
    categorylist.pop()
    for (categoryUrl, categoryName) in categorylist:
        site.add_dir(categoryName, site.url[:-1] + categoryUrl, 'List',  '', '')
    utils.eod()

@site.register()
def Play(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videopage = utils.getHtml(url, site.url, cookiehdr)
    videolink = re.compile(r'<source.+?src="([^"]+)', re.DOTALL | re.IGNORECASE).findall(videopage)[0]
    vp.progress.update(75, "[CR]Loading video page[CR]")
    vp.play_from_direct_link(videolink)

#@site.register()
#def Related(url):
#    contexturl = (utils.addon_sys + "?mode=" + str('fetishpapa.List') + "&url=" + urllib_parse.quote_plus(url))
#    xbmc.executebuiltin('Container.Update(' + contexturl + ')')

@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        url = "{0}{1}/".format(url, keyword.replace(' ', '+'))
        utils.kodilog(url)
        List(url)

#@site.register()
#def Sortorder(url):
#    order = utils.selector('Select category', sort_orders.keys())
#    if order:
#        utils.addon.setSetting('zeuspornsortorder', sort_orders[order])
#        Main()