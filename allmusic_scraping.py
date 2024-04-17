# https://github.com/jack-arms/allmusic-python/blob/master/allmusic.py
from pyquery import PyQuery as pq
import requests
import json
import re
import time
import datetime
import sys
# import pymysql.cursors
import difflib
from fuzzywuzzy import fuzz

allmusic_song_search_base = 'http://www.allmusic.com/search/songs/'
SONG_QUERY_TITLE = ''
SONG_QUERY_ARTIST = ''
SONG_QUERY = SONG_QUERY_ARTIST + ' ' + SONG_QUERY_TITLE
NUM_SONG_SEARCH_RESULTS = 3
featuring_regex = r'\s(ft\.?|feat\.?|[fF]eaturing|\/|[xX]|[aA]nd|&|[wW]ith)\s'
date_format = "%Y-%m-%d"
start_date = datetime.datetime.strptime('1980-01-01', date_format).date()
week_ago = datetime.timedelta(days=-7)
next_week = datetime.timedelta(days=7)
end_date = datetime.datetime.strptime('1959-01-01', date_format).date()
songs_considered = {}
song_to_album_dict = {}
albums_considered = {}
REQUEST_DELAY = 1
TOP_N = 100
MODE = ''

def song_search(song, num_results):
    url = allmusic_song_search_base + song
    req = requests.get(url, headers={
        'Host': 'www.allmusic.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8'
    })
    if req.status_code != 200:
        return {'error': req.text}

    d = pq(req.text)
    print("inside scraper", song)
    songs = d('div#resultsContainer div.song')
    num_to_get = min(num_results, len(songs))
    song_list = []
    for song in songs[:num_to_get]:
        song_list.append(song_to_dict(song))

    return song_list

def song_search_matching(chart_song, query):
    """
    Search for all songs matching the given chart song, with the given query
    and artist from the query
    """
    song_searches = song_search(query, NUM_SONG_SEARCH_RESULTS)
    if 'error' in song_searches:
        print('>>> error:', song_searches['error'])
        return

    songs = []
    # print(song_searches)
    for s in song_searches['songs']:
        # print('test song:', s)
        performers = ' '.join(x['name'] for x in s['performers']).lower()

        print('checking performers:', performers, 'vs.', chart_song.artist.lower())
        print('checking titles:', '"' + s['title']['name'] + '"', 'vs.', '"' + chart_song.title + '"')
        diff1 = fuzz.token_set_ratio(chart_song.artist.lower(), performers)
        diff2 = difflib.SequenceMatcher(
            None,
            a=s['title']['name'].lower(),
            b=chart_song.title.lower()
        ).ratio()
        print('performer score:', diff1, 'and title score:', diff2)
        if diff1 >= 65 and diff2 > 0.75:
            songs.append(s)
            print('song passed with diff performers of', diff1, 'and diff title of', diff2)
            if diff1 <= 75 or diff2 < 0.85:
                print('NOTE impartial match?', s, 'for', chart_song)

    return songs

def song_to_dict(song):
    '''Converts a song in HTML (an <li> element from allmusic.com)
    into json.'''
    d = pq(song)

    song_dict = {}

    # get title
    title_anchor = d('div.title a').eq(0)
    title_url = title_anchor.attr('href')
    title_text = title_anchor.text().strip('"')
    song_dict['title'] = {'name': title_text, 'url': title_url}

    # get performer
    performer_list = []
    performer_anchors = d('div.performers a')
    for i in range(len(performer_anchors)):
        performer_anchor = performer_anchors.eq(i)
        performer_name = performer_anchor.text()
        performer_url = performer_anchor.attr('href')
        performer_list.append({'name': performer_name, 'url': performer_url})

    song_dict['performers'] = performer_list

    # get composer
    composer_list = []
    composer_anchors = d('div.composers a')
    for i in range(len(composer_anchors)):
        composer_anchor = composer_anchors.eq(i)
        composer_list.append({
            'name': composer_anchor.text(),
            'url': composer_anchor.attr('href')
        })

    song_dict['composers'] = composer_list
    
    return song_dict