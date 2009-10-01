start_url = 'http://127.0.0.1:5040/test/esener/'

from BeautifulSoup import BeautifulSoup
from multiprocessing import Pool, Queue
from zc.testbrowser.browser import Browser
import time

link_queue = Queue()

def followLink():
    try:
        while True:
            url, country = link_queue.get(False, 1)
            browser = Browser()
            browser.open(url)
            browser.getLink('Company Size').click()
            browser.getLink('Sector Type').click()
            if not country:
                for i in range(60):
                    link_queue.put((url + '/%03i' % i, True))

    except Queue.Empty:
        pass
    
if __name__ == '__main__':
    browser = Browser()
    browser.open(start_url)
    soup = BeautifulSoup(browser.contents.decode('utf-8').encode('ascii', 'replace'))
    all_links = soup.find('div', {'class' : 'surveyanswers'}).findAll('a')
    for link in all_links:
        link_queue.put((link['href'], False))

    processes = 4
    pool = Pool(processes=processes)
    for i in range(processes):
        pool.apply_async(followLink)
    performance = range(10)
    while not link_queue.empty():
        time.sleep(1)
        size = link_queue.qsize()
        performance.append(size)
        performance = performance[-10:]
        diff = performance[0] - size
        if diff > 0:
            speed = diff / 10.0
            seconds = int(size / speed)
            minutes = seconds / 60
            hours = minutes / 60
            days = hours / 24
            seconds = seconds % 60
            minutes = minutes % 60
            hours = hours % 24
            print "Missing %i days, %i hours, %i minutes, %i seconds" % \
                (days, hours, minutes, seconds)
        else:
            print "Still growing by %.2f urls per second" % (diff / -10.0)

