import requests
import re
from urllib.parse import urljoin

class WebParser:

    def __init__(self, source=None):
        self.source = source  # the original url to start from
        self.graph = {}  # an adjacence matrix to represents the graph
    
    def walk(self, n, parent=None):
        if parent is None:
            parent = self.source
        print(f"Retrieving {parent}")
        self.graph[parent] = []
        # get the html content from parent url
        page_response = requests.get(parent)
        page_content = page_response.text
        # get the 'main' tag
        main_match = re.search(r'(<main.*>.*</main>)', page_content, flags=re.DOTALL)
        if main_match is None:
            return
        main_content = main_match.group(0)
        # get the urls inside the main tag
        urls_match = re.findall(r'<a[^>]*href="([^"\?]+)(?:\?[^"]+)?"[^>]*>', main_content)
        # save them in the graph, and call recursively
        for url in urls_match:
            url_key: str = urljoin(parent, url.strip())
            if not url_key.startswith('http'):
                # skip if not http link (mailto for example)
                continue
            self.graph[parent].append(url_key)
            if url_key not in self.graph and n > 0:
                self.walk(n-1, url_key)
