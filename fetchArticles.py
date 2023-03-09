import requests
import threading
import pickle

urls = set()

def thread_target():
    try: urls.add(requests.get('https://fr.wikipedia.org/wiki/Sp%C3%A9cial:Page_au_hasard').url)
    except: pass

def fetchUrlBatch(batchSize = 100):
    threads = []
    for _ in range(batchSize): threads.append(threading.Thread(target=thread_target))
    for t in threads: t.start()
    for t in threads: t.join()

def loadUrls():
    global urls
    with open('data/articleUrls.pk', 'rb') as f:
        urls = pickle.load(f)

def saveUrls():
    with open('data/articleUrls.pk', 'wb') as f:
        pickle.dump(urls, f)