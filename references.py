import time
import pickle
import re
import json
import requests
from config import *
from requests_html import HTMLSession
from urllib.parse import quote
import difflib

IEEE_API_SEARCH_META_DATA = 'http://ieeexploreapi.ieee.org/api/v1/search/articles?apikey=' + \
                            DIRTY_LITTLE_SECRETS['IEEE_API_KEY'] + \
                            '&format=json&max_records=25&start_record=1&sort_order=asc&sort_field=article_number&meta_data={0}'


def extract_publication_info(ref_str):
    """
    Get the author, title, and year from a reference.
    This will only work if the reference ends with a year.
    That is my way of filtering out scholarly articles from
    other references, like websites. 
    """
    pub_info = {}
    
    # Get the year first (must end with a year)
    # Hopefully this will filter out a lot of the 
    # bad references
    yearex = re.search(r'\s\d+\.$|\s\d+$', ref_str)
    if not yearex:  # return empty dict. Caller figures out what to do with it
        return pub_info
    else:
        pub_info['year'] = int(yearex[0].replace('.', '').strip())

    # Get the authors next
    author_list = []
    for i, chunk in enumerate(s.split(',')):
        if len(chunk.split()) < 6:
            author_list.append(chunk)
        else: break
    remaining = ','.join(s.split(',')[i:])
    pub_info['authors'] = author_list

    # Get the title
    title = ''
    try:
        # search for several types of quotes -> take first -> remove whitespace -> remove quotes -> remove whitespace
        title = re.search(r'(“|\")(.*)(\"|”)', remaining).group(0).strip()[1:-1].strip()
    except:     # no quotes
        # take the first regardless of if there's anything after
        title = remaining.split(',')[0].strip()
    pub_info['title'] = title

    return pub_info


def get_info_from_title(title, publication="IEEE"):
    """
    Go to the Internet and get the publication info for 
    the given title. @publication defines the website to
    go to. Only IEEE is implemented right now. The other
    option will just be Google Scholar when it's in
    """
    pub_info = {}

    if publication.lower() == "ieee":
        url_title = quote(title)
        url = IEEE_API_SEARCH_META_DATA.format(url_title)
        time.sleep(.1)
        r = requests.get(url)
        results = json.dumps(r.text)
        if results['total_records'] == 0:
            print('No title found...')
            return pub_info     # return empty pub info
        elif results['total_records'] == 1:
            print('One title found...')
            result = results['articles'][0]
            pub_info['doi'] = result['doi']
            pub_info['title'] = result['title']
            pub_info['authors'] = result['authors']
            pub_info['year'] = result['publication_year']
            pub_info['citations'] = result['citing_paper_count']
            return pub_info

        else:   # multiple titles. Find the closest
            print('Multiple titles found...')
            
            # first extract the titles from the http response dict
            titles = [pub['title'] for pub in results['articles']]
            
            # sort the titles according to closeness to the given title
            closest_title = sorted(titles, key=lambda x: difflib.SequenceMatcher(None, x, title).ratio(), reverse=True)[0]

            # go through the http response dict and find the publication with the closest title
            for pub in results['articles']:
                if pub['title'] == closest_title:
                    break

            result = pub
            pub_info['doi'] = result['doi']
            pub_info['title'] = result['title']
            pub_info['authors'] = result['authors']
            pub_info['year'] = result['publication_year']
            pub_info['citations'] = result['citing_paper_count']
            return pub_info
            
    elif publication.lower() == "google scholar" or publication.lower() == "gs":
        raise ValueError('only IEEE implemented')



# # NOTE: Doesn't always work! Sometimes need to run 3-5 times before output
# _URL = 'https://ieeexplore.ieee.org/document/7560203/references#references'
# session = HTMLSession()
# r = session.get(_URL)
# r.html.render(retries=10)
# span_stuff = iter(r.html.find('span'))
# refs = []
# for html in span_stuff:
#     if re.findall(r'^\d+\.', html.text):
#         print(html.text, end=' ')
#         a = next(span_stuff).text
#         refs.append(a)
#         print(refs[-1])  
# pickle.dump(refs, open('ref_list.pkl', 'wb'))

refs = pickle.load(open('ref_list.pkl', 'rb'))
ref_set = []
for ref in refs:
    if not ref_set.__contains__(ref):
        ref_set.append(ref)

for ref in ref_set:
    print(ref)
    authors, s = extract_authors(ref)
    title = extract_title(s, remaining=True)
    # print('Title:', title)
    





