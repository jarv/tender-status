import os
from flask import Flask
from settings import BASE_URL, API_KEY, CATEGORIES
import requests
import json
from dateutil.relativedelta import relativedelta, FR
from dateutil.parser import parse
from collections import Counter
from datetime import datetime
from werkzeug.contrib.cache import SimpleCache
import pytz

DIR = os.path.dirname(__file__)
DEBUG = True
UTC = pytz.UTC
app = Flask(__name__)
app.config.from_object(__name__)

cache = SimpleCache()

if app.config['DEBUG']:
    from werkzeug import SharedDataMiddleware
    import os
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        "/": os.path.join(DIR, 'static')
    })


def time_diff(datetime_str):
    """
    datetime_str: any string that can be parsed by dateutil
    returns a string representing a delta from the current time
    """
    ret = ""
    s = (UTC.localize(datetime.now()) -
         parse(datetime_str)).total_seconds()
    (d, s) = divmod(s, 60 * 60 * 24)
    if d:
        ret += "{0:.0f}d ".format(d)
    (h, s) = divmod(s, 60 * 60)
    if h:
        ret += "{0:.0f}h ".format(h)
    (m, s) = divmod(s, 60)
    if m:
        ret += "{0:.0f}m ".format(m)
    ret += "{0:.0f}s".format(s)
    return ret

def gen_stats(discussions):

    now = datetime.now()
    f1 = (now + relativedelta(weekday=FR(-1))).date()
    f2 = (now + relativedelta(weekday=FR(-2))).date()
    f3 = (now + relativedelta(weekday=FR(-3))).date()
    stats = []
    for stat in [f1, f2, f3]:
        stats.append({
            'title': str(stat),
            'resolved': 0,
            'created': 0,
            'users': Counter()
        })

    for issue in discussions:
        updated = parse(issue['last_updated_at']).date()
        created = parse(issue['created_at']).date()
        state = issue['state']
        if f1 < created:
            stats[0]['created'] += 1
            stats[0]['users'][issue['author_name']] += 1
        elif f2 < created <= f1:
            stats[1]['created'] += 1
            stats[1]['users'][issue['author_name']] += 1
        elif f3 < created <= f2:
            stats[2]['created'] += 1
            stats[2]['users'][issue['author_name']] += 1

        if f1 < updated:
            if state == 'resolved':
                stats[0]['resolved'] += 1
        elif f2 < updated <= f1:
            if state == 'resolved':
                stats[1]['resolved'] += 1
        elif f3 < updated <= f2:
            if state == 'resolved':
                stats[2]['resolved'] += 1
    return(stats)


@app.route("/tender")
def proxy_ajax():
    """
    Proxies the get request to another
    server
    """
    discussions = tender_discussions()
    rv = {}
    rv['categories'] = []
    rv['stats'] = gen_stats(discussions)
    for category in CATEGORIES:
        by_category = tender_discussions(category['name'])
        rv['categories'].append({
            'label': category['label'],
            'total': len(by_category),
            'most_recent': [{
                'updated': time_diff(issue['last_updated_at']),
                'title': issue['title'],
                'author_name': issue['author_name']}
                for issue in by_category[::-1][0:3]]
        })
    return json.dumps(rv)


def tender_discussions(dtype='all'):
    discussions = cache.get(dtype)
    if dtype == 'all':
        url = ''
    else:
        url = dtype

    if discussions is None:
        print "refreshing cache"
        discussions = []
        page_num = 1
        seen = 0
        while (True):
            # fetch all pending discussions for summary stats
            r = requests.get(
                BASE_URL + url + '?page=' + str(page_num), headers={
                    'X-Tender-Auth': API_KEY,
                    'Accept': 'application/vnd.tender-v1+json'
                })
            page = json.loads(r.content)
            discussions.extend(page['discussions'])
            seen += page['per_page']
            print "{0}: {1}/{2}".format(page_num, seen, page['total'])
            if seen >= page['total']:
                print "total: {0}".format(page['total'])
                break
            page_num += 1
        cache.set(dtype, discussions, timeout=5 * 60)
    return discussions

if __name__ == '__main__':
    app.run()
