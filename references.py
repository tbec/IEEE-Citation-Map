import pickle
import re
from requests_html import HTMLSession


def extract_authors(s):
    """
    Extract authors from reference. Assumes authors are first,
    comma-separated, and do not contain more than 2 spaces. Returns
    the list of authors and the remaining string (title should be 
    right at the beginning of remaining string)
    """
    author_list = []
    for i, chunk in enumerate(s.split(',')):
        if len(chunk.split()) < 6:
            author_list.append(chunk)
        else: break
    remaining = ','.join(s.split(',')[i:])
    return author_list, remaining


def extract_title(s, remaining=False):
    """ 
    Get the title from the string. If the title is in quotes it's easy. 
    If the title isn't in quotes then we put it at the beginning of the
    string and take everything until the next comma. 
    """
    try:
        # search for several types of quotes -> take first -> remove whitespace -> remove quotes -> remove whitespace
        return re.search(r'(“|\")(.*)(\"|”)', ref).group(0).strip()[1:-1].strip()
    except:     # no quotes
        
        if remaining:   # title is first, just split on comma. Hope there aren't commas in the title!
            chunked = s.split(',')

            # take the first regardless of if there's anything after
            return chunked[0].strip()
            
        else:   # title is somewhere in the middle AND it didn't have quotes! Can only remove authors and try again
            _, s = extract_authors(s)
            return extract_title(s, remaining=True)
        



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
    authors, s = extract_authors(ref)
    title = extract_title(s, remaining=True)
    print('Authors:', authors)
    print('Title:', title)
    print()
    





