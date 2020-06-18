import scrapy
import threading
import json
from helper import Parser

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chosen = set(QuotesSpider.start_urls)
        self.verbose = True
        self.crawl_limit = 2000
        self.lock = threading.Lock()

    start_urls = [
            'https://www.semanticscholar.org/paper/Attention-is-All-you-Need-Vaswani-Shazeer/204e3073870fae3d05bcbc2f6a8e263d9b72e776',
            'https://www.semanticscholar.org/paper/BERT%3A-Pre-training-of-Deep-Bidirectional-for-Devlin-Chang/df2b0e26d0599ce3e70df8a9da02e51594e0e992',
            'https://www.semanticscholar.org/paper/The-Lottery-Ticket-Hypothesis%3A-Training-Pruned-Frankle-Carbin/f90720ed12e045ac84beb94c27271d6fb8ad48cf',
            ]
    
    def parse(self, response):
        page_info = Parser.get_all_info(response)
        self.log('started') 
        yield page_info
        urls = set(page_info['references'])
        self.log(f"Finished evaluating {page_info['title']}")
        self.log(f"length of chosen: {len(self.chosen)}")
        self.log(f"Ignoring {len(urls.intersection(self.chosen))} sites")
        for next_page in urls.difference(self.chosen):
            with self.lock:
                should_yield = len(self.chosen) < self.crawl_limit
                if should_yield:
                    self.chosen.add(next_page)
            if should_yield:
                yield scrapy.Request(next_page, callback=self.parse)
            else:
                break
        
    def log(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)

