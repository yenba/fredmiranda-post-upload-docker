import html
import re
import requests
from bs4 import BeautifulSoup


def parse_page(i):
    """A dummy docstring."""
    r = requests.get(f'https://www.fredmiranda.com/forum/board/10/{i}')
    soup = BeautifulSoup(r.text, 'html.parser')
    main = soup.find_all('table')[15]
    result = main.find_all('tr')

    def parse_tr(tr):
        """A dummy docstring."""
        try:
            anchor = tr.select_one('a')
            seller, posts, views, time_ago = tr.find_all('td')[-4:]
            content = ''.join(anchor.contents)
            try:
                if content.index(':'):
                    status = content.split(':', maxsplit=1)[0]
            except: # pylint: disable=bare-except
                status = None
            data = {
                'post_id': re.findall("[0-9]+", str(anchor.attrs['href']))[0],
                'status': status,
                'content': content,
                'url': str(anchor.attrs['href']),
                # 'time_ago': str(time_ago.span.contents[0]),
                'seller': html.unescape(str(seller.a.contents[0])),
                'posts': html.unescape(str(posts.contents[0])),
                'views': html.unescape(str(views.contents[0]))
            }

            return data
        except Exception as e:
            print(e)
            return {}
    parsed = list(map(parse_tr, result))
    return parsed
