import requests
import re
from urllib.parse import urljoin, urlparse
import threading
import queue
import os


class WebParser:

    def __init__(self, source=None, same_site=False, main_tag='main'):
        self.source = source  # the original url to start from
        self.same_site = same_site
        self.main_tag = main_tag

        self.known_urls = set() # urls whose page has already been visited
        self.next_urls = {source} # urls whose page must be visited

        self.graph_buffer = {}  # a sub-matrix of adjacency matrix to represent a part of the graph

        self.graph_path = './graph.txt' # a file to store the whole graph
        if os.path.isfile(self.graph_path): os.remove(self.graph_path)
    

    def fetch_process_next_url_batch(self, batch_size=100):
        threads = []
        threads_result = queue.Queue()

        for _ in range(min(len(self.next_urls), batch_size)):
            url = self.next_urls.pop() # url to process
            self.known_urls.add(url) # we indicate that we process this url

            thread_args = (threads_result, url, self.main_tag, self.same_site)
            threads.append(threading.Thread(target=lambda q, *args: q.put(_thread_target_fetch_url(*args)), args=thread_args))

        for thread in threads: thread.start()
        for thread in threads: thread.join()


        next_urls_batch = set() 
        while not threads_result.empty():
            result = threads_result.get()
            if result is not None:
                next_urls, graph_buffer = result
                self.graph_buffer.update(graph_buffer)
                next_urls_batch.update(next_urls)

        new_urls = next_urls_batch.difference(self.known_urls)
        self.next_urls.update(new_urls)
        

    def flush_graph_buffer(self):
        with open(self.graph_path, 'a') as graph_file:
            graph_file.writelines(list(map(lambda kv: kv[0] + ' ' + ' '.join(kv[1]) + '\n', self.graph_buffer.items())))
        
        self.graph_buffer = {}


def _thread_target_fetch_url(url, main_tag, same_site):
    next_urls = []
    graph_buffer = {}

    graph_buffer[url] = []

    url_parsed = urlparse(url)
    # get the html content from parent url
    page_response = requests.get(url)
    page_content = page_response.text
    # get the 'main' tag
    main_match = re.search(rf'(<{main_tag}.*>.*</{main_tag}>)', page_content, flags=re.DOTALL)
    if main_match is None:
        return
    main_content = main_match.group(0)
    # get the urls inside the main tag
    next_urls_match = re.findall(r'<a[^>]*href="([^"\?#]+)(?:\?[^"]+)?(?:#[^"]+)?"[^>]*>', main_content)
    # save them in the graph and return them
    for next_url in next_urls_match:
        next_url_str: str = urljoin(url, next_url.strip())
        next_url_parsed = urlparse(next_url_str)
        if not next_url_parsed.scheme in ['http', 'https']:
            # skip if not http link (mailto for example)
            continue
        if same_site and next_url_parsed.netloc != url_parsed.netloc:
            continue
        graph_buffer[url].append(next_url_str)
        next_urls.append(next_url_str)
    
    return next_urls, graph_buffer