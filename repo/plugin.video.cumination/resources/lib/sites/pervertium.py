'''
    Cumination
    Copyright (C) 2026 Cumination

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
import urllib.parse
from resources.lib import utils
from resources.lib.decrypters.kvsplayer import kvs_decode
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse
from random import randint
from time import time


site = AdultSite('pervertium', "[COLOR hotpink]Pervertium[/COLOR]", 'https://pervertium.com/', 'pervertium.png', 'pervertium')
sort_orders = {'Latest': 'last-updates/', 'Top rated': 'top-rated/', 'Most viewed': 'most-popular/'}
vn = None

@site.register(default_mode=True)
def Main():
    global vn
    ordername = utils.addon.getSetting('pervertiumsortorder') or 'Latest'
    order = sort_orders.get(ordername, 'last-updates/')
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'search/', 'Search', site.img_search)
    site.add_dir('[COLOR hotpink]Sort Order: [/COLOR] [COLOR orange]{}[/COLOR]'.format(ordername), site.url, 'Sortorder', site.img_cat)
    #site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url, 'ShowCategories', site.img_cat)
    List(site.url + order)
    if vn is None:
        vn = int(time())
    utils.eod()

@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    if 'the requested search cannot be found' in html:
        utils.notify(msg='Nothing found')
        utils.eod()
        return
    global vn
    if vn is None:
        vn = int(time())
        
    delimiter = '<div\sclass="item\spop-thumb\s+"'
    re_videopage = '<a href="([^"]+)"'
    re_name = 'title="([^"]+)"'
    re_img = '<img.+?data-original="([^"]+)"'
    re_duration = '<div\sclass="duration">([0-9,:]+)<'

    utils.videos_list(site, 'pervertium.Play', html, delimiter, re_videopage, re_name, re_img, re_duration=re_duration)
    
    match = re.search(r'<li\sclass="next">\s*<a\s.+data-block-id="([^"]+)"\s+data-parameters="([^"]+)"', html, re.DOTALL | re.IGNORECASE)
    if match:
        block_id = match.group(1)
        params = ""
        parameters = re.split(";", match.group(2))
        for parameter in parameters:
            if "+" in parameter:
                keys, value = re.split(":", parameter,1)
                keys = re.split(r"\+", keys)
                for key in keys:
                    params += key + "=" + value + "&"
            else:
                params += parameter.replace(';', '&').replace(':', '=') + "&"
        params = params[:-1]
        vn += 1
        next_url = url.split('?')[0] + '?mode=async&function=get_block&block_id={0}&{1}&_={2}'.format(block_id, params, str(vn))
        utils.kodilog(f'Next url: {next_url}', xbmc.LOGINFO)

        # look for last page
        last_nr = re.findall(r'<li\sclass="last">\s*<a\s.+data-parameters=".+from:(\d+)">L', html, re.DOTALL | re.IGNORECASE)[0]
        utils.kodilog(f'Last PAGE: {last_nr}', xbmc.LOGINFO)
        last_page = ' / ' + str(last_nr) if last_nr else ''

        # look for next page numbers
        # get the next page number
        next_nr = re.findall(r'.+from=(\d+)', params, re.DOTALL | re.IGNORECASE)[0]

        next_page = "( " + str(int(next_nr)) + last_page + " )"
        site.add_dir("Next {}".format(next_page), next_url, "List", site.img_next)

    utils.eod()

@site.register()
def Play(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    hdr = utils.base_hdrs
    utils.kodilog(f'Original header: {hdr}', xbmc.LOGINFO)
    hdr['Cookie'] = 'kt_tcookie=1; kt_is_visited=1'
    utils.kodilog(f'Patched header: {hdr}', xbmc.LOGINFO)
    html = utils.getHtml(url, headers=hdr)
    surl = re.search(r"video_url:\s*'([^']+)'", html)
    if surl:
        surl = surl.group(1)
        if surl.startswith('function/'):
            license = re.findall(r"license_code:\s*'([^']+)", html)[0]
            utils.kodilog("Obfuscated URL: " + surl, xbmc.LOGINFO)
            surl = kvs_decode(surl, license)
            utils.kodilog("Decoded URL:" + surl, xbmc.LOGINFO)
    else:
        vp.progress.close()
        return
    vp.progress.update(75, "[CR]Video found[CR]")
    vp.play_from_direct_link(surl)

@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        url = "{0}{1}/".format(url, keyword.replace(' ', '+'))
        List(url)

@site.register()
def Sortorder(url):
    order = utils.selector('Select category', sort_orders.keys())
    if order:
        utils.addon.setSetting('pervertiumsortorder', order)
        Main()