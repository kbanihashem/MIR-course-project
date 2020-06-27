import scrapy
import threading
from scrapy.crawler import CrawlerProcess
from helper import Parser


class MySpider(scrapy.Spider):
    name = "kiarash"
    
    def __init__(self, urls, crawl_limit, verbose, *args, **kwargs):
        super().__init__(*args, **kwargs)
#        self.chosen = set(MySpider.start_urls)
        self.verbose = verbose
        self.crawl_limit = crawl_limit
        self.urls = urls
        self.lock = threading.Lock()
        self.chosen = set(self.urls)
        self.visited = set()

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page_info = Parser.get_all_info(response)
        yield page_info
        urls = set(page_info['references'])
        #logging
        self.visited.add(response.url)
        self.log(f"Finished evaluating {page_info['title']}")
        self.log(f"Length of chosen: {len(self.chosen)}")
        self.log(f"Length of visited: {len(self.visited)}")
        self.log(f"Ignoring {len(urls.intersection(self.chosen))} sites")

        for next_page in urls.difference(self.chosen):
            with self.lock:
                should_yield = len(self.chosen) < self.crawl_limit and next_page not in self.chosen
                if should_yield:
                    self.chosen.add(next_page)
            if should_yield:
                yield scrapy.Request(next_page, callback=self.parse)
        
    def log(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)

def crawl(start_urls, crawl_limit=2000, output_path='quotes.json', verbose=False):
    #clearing the file
    with open(output_path, 'w') as f:
        pass
    process = CrawlerProcess(settings={
        "FEEDS": {
            output_path: {"format": "json"},
        },
    })
    process.crawl(MySpider, urls=start_urls, crawl_limit=crawl_limit, verbose=verbose)
    process.start()

if __name__ == '__main__':
    start_urls = [
            'https://www.semanticscholar.org/paper/Attention-is-All-you-Need-Vaswani-Shazeer/204e3073870fae3d05bcbc2f6a8e263d9b72e776',
            'https://www.semanticscholar.org/paper/BERT%3A-Pre-training-of-Deep-Bidirectional-for-Devlin-Chang/df2b0e26d0599ce3e70df8a9da02e51594e0e992',
            'https://www.semanticscholar.org/paper/The-Lottery-Ticket-Hypothesis%3A-Training-Pruned-Frankle-Carbin/f90720ed12e045ac84beb94c27271d6fb8ad48cf',
            ]
    crawl_limit = 2000
    crawl(start_urls, crawl_limit, verbose=True)
