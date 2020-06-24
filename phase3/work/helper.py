class Parser:

    @staticmethod
    def get_abstract(response):
        ans =  response.css("meta[name='description']::attr(content)").get()
        return ans if ans is not None else ""

    @staticmethod
    def get_title(response):
        ans =  response.css("meta[name='citation_title']::attr(content)").get()
        return ans if ans is not None else ""

    @staticmethod
    def get_date(response):
        ans =  response.css("meta[name='citation_publication_date']::attr(content)").get()
        return ans if ans is not None else ""

    @staticmethod
    def get_authors(response):
        ans =  response.css("meta[name='citation_author']::attr(content)").getall()
        return ans if ans is not None else []

    @staticmethod
    def get_references(response):
        raw_urls = response.css("div#references h2.citation__title a::attr(href)").getall()
        full_urls = list(map(lambda url: response.urljoin(url), raw_urls))
        ans =  full_urls
        return ans if ans is not None else []

    @staticmethod
    def get_id(response):
        ans =  response.url.split('/')[-1] 
        return ans

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

#    @staticmethod
#    def get_citations(response):
#        ans =  response.css("response.css('h2.citation__title a::attr(href)').getall()").getall()
#        return ans if ans is not None else []
