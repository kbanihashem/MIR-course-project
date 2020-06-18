class Parser:

    @staticmethod
    def get_abstract(response):
        return response.css("meta[name='description']::attr(content)").get()

    @staticmethod
    def get_title(response):
        return response.css("meta[name='citation_title']::attr(content)").get()

    @staticmethod
    def get_date(response):
        return response.css("meta[name='citation_publication_date']::attr(content)").get()

    @staticmethod
    def get_authors(response):
        return response.css("meta[name='citation_author']::attr(content)").getall()

    @staticmethod
    def get_citations(response):
        return response.css("response.css('h2.citation__title a::attr(href)').getall()").getall()

    @staticmethod
    def get_references(response):
        raw_urls = response.css("div#references h2.citation__title a::attr(href)").getall()
        full_urls = list(map(lambda url: response.urljoin(url), raw_urls))
        return full_urls

    @staticmethod
    def get_id(response):
        return response.url.split('/')[-1] 

    @staticmethod
    def get_all_info(response):
        funcs = {
                'id': Parser.get_id,
                'title': Parser.get_title,
                'authors': Parser.get_authors,
                'date': Parser.get_date,
                'abstract': Parser.get_abstract,
                'references': Parser.get_references,
                }
        
        return {name:func(response) for name, func in funcs.items()}

