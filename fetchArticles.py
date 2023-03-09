import requests
import threading
import pickle

class RandomArticleFetcher():
    def __init__(self):
        self.urls = set()

    def thread_target(self):
        try: self.urls.add(requests.get('https://fr.wikipedia.org/wiki/Sp%C3%A9cial:Page_au_hasard').url)
        except: pass

    def fetchUrlBatch(self, batchSize = 100):
        threads = []
        for _ in range(batchSize): threads.append(threading.Thread(target=self.thread_target))
        for t in threads: t.start()
        for t in threads: t.join()

    def loadUrls(self):
        with open('data/articleUrls.pk', 'rb') as f:
            self.urls = pickle.load(f)

    def saveUrls(self):
        with open('data/articleUrls.pk', 'wb') as f:
            pickle.dump(self.urls, f)