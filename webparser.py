import requests
import re
from urllib.parse import urljoin, urlparse


class WebParser:

    def __init__(self, source=None, same_site=False, main_tag='main'):
        self.source = source  # the original url to start from
        self.same_site = same_site
        self.main_tag = main_tag
        self.graph = {}  # an adjacence matrix to represents the graph
    
    def walk(self, n, parent=None):
        if parent is None:
            parent = self.source
        self.graph[parent] = []
        parent_parsed = urlparse(parent)
        # get the html content from parent url
        print(f"Retrieving {parent}")
        page_response = requests.get(parent)
        page_content = page_response.text
        # get the 'main' tag
        main_match = re.search(rf'(<{self.main_tag}.*>.*</{self.main_tag}>)', page_content, flags=re.DOTALL)
        if main_match is None:
            return
        main_content = main_match.group(0)
        # get the urls inside the main tag
        urls_match = re.findall(r'<a[^>]*href="([^"\?#]+)(?:\?[^"]+)?(?:#[^"]+)?"[^>]*>', main_content)
        # save them in the graph, and call recursively
        for url in urls_match:
            url_str: str = urljoin(parent, url.strip())
            url_parsed = urlparse(url_str)
            if not url_parsed.scheme in ['http', 'https']:
                # skip if not http link (mailto for example)
                continue
            if self.same_site and url_parsed.netloc != parent_parsed.netloc:
                continue
            self.graph[parent].append(url_str)
            if url_str not in self.graph and n > 0:
                self.walk(n-1, url_str)
