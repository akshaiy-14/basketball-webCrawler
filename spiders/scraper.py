import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.request import referer_str
import re

class BbWikiSpider(CrawlSpider):
    name = "bbWiki"
    allowed_domains = ["en.wikipedia.org"]
    wiki_url2 = "https://en.wikipedia.org/wiki/"
    start_urls = [
    wiki_url2+"Portland_Trail_Blazers", wiki_url2+"New_York_Knicks", wiki_url2+"Boston_Celtics",
    wiki_url2+"Philadelphia_76ers", wiki_url2+"Toronto_Raptors", wiki_url2+"Chicago_Bulls",
    wiki_url2+"Cleveland_Cavaliers", wiki_url2+"Detroit_Pistons", wiki_url2+"Indiana_Pacers",
    wiki_url2+"Milwaukee_Bucks", wiki_url2+"Atlanta_Hawks", wiki_url2+"Charlotte_Hornets",
    wiki_url2+"Miami_Heat", wiki_url2+"Orlando_Magic", wiki_url2+"Washington_Wizards",
    wiki_url2+"Denver_Nuggets", wiki_url2+"Minnesota_Timberwolves", wiki_url2+"Oklahoma_City_Thunder",
    wiki_url2+"Utah_Jazz", wiki_url2+"Golden_State_Warriors", wiki_url2+"Los_Angeles_Clippers",
    wiki_url2+"Los_Angeles_Lakers", wiki_url2+"Phoenix_Suns", wiki_url2+"Sacramento_Kings",
    wiki_url2+"Dallas_Mavericks", wiki_url2+"Houston_Rockets", wiki_url2+"Memphis_Grizzlies",
    wiki_url2+"New_Orleans_Pelicans", wiki_url2+"San_Antonio_Spurs", wiki_url2+"Basketball", 
    wiki_url2+"National_Basketball_Association", wiki_url2+"EuroBasket", wiki_url2+"College_basketball",
    wiki_url2+"List_of_National_Basketball_Association_rivalries", wiki_url2+"NBA_draft", wiki_url2+"Basketball_positions"
]

    pattern = re.compile(r".*(category|talk|baseball|football|template|rugby|hockey).*", re.IGNORECASE)
    le1 = LinkExtractor(deny = pattern, allow=r"https://en.wikipedia.org/wiki/.*(?:NBA|basketball|coach|NCAA|FIBA|league|division|draft|WNBA).*", restrict_xpaths="//main[@class='mw-body']//a")
    rule1 = Rule(le1, callback='parse_item', follow=True)
    rules = (rule1,)
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter'
    }


    def parse_item(self, response):
        if "https://en.wikipedia.org" in response.url:

                title = response.css("h1#firstHeading span::text").get().strip()
                para = response.css("div.mw-parser-output > p:first-of-type ~ p:nth-of-type(-n+3)").get()
                if para:
                    clean_part = response.css('div.mw-parser-output > p:first-of-type ~ p:nth-of-type(-n+3) ::text').getall()
                    content = "".join(clean_part).strip()
                yield {
                    "SourceLink": referer_str(response.request),
                    "Link": response.url,
                    "Title": str(title),
                    "Content": str(content)
                }


class BbSpider(scrapy.Spider):

    name = "bb"
    allowed_domains = ["en.wikipedia.org", "theringer.com", "global.nba.com", "basketball.realgm.com"]
    wiki_url = "https://en.wikipedia.org/wiki/List_of_National_Basketball_Association_players_"
    start_urls = ["https://www.theringer.com/nba/archives", "http://global.nba.com/news/", wiki_url+"(A)", wiki_url+"(B)", wiki_url+"(C)", wiki_url+"(D)", wiki_url+"(E-F)", wiki_url+"(G)", wiki_url+"(H)", wiki_url+"(I-J)", wiki_url+"(K)", wiki_url+"(K)", wiki_url+"(L)", wiki_url+"(M)", wiki_url+"(N-O)", wiki_url+"(P-Q)", wiki_url+"(R)", wiki_url+"(S)", wiki_url+"(T-V)", wiki_url+"(W-Z)"]
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter'
    }

    def parse(self, response):
        if "https://basketball.realgm.com" in response.url:
            older_wiretaps = response.css(".fs-close-button-sticky , .news-column a+ a::attr(href)").get()

            content_pages = response.css("div.main-container div.article.clearfix a::attr(href)").extract()
            for page in content_pages:
                yield response.follow(page, self.parse_content)
            
            # Follow the link to the next page only if it exists
            if older_wiretaps is not None:
                yield response.follow(older_wiretaps, callback=self.parse)
            
        
        elif "https://www.theringer.com" in response.url:
            # Extract the link to the next page
            next_page = response.css("nav.c-pagination a:last-of-type::attr(href)").get()

            content_pages = response.css("div.l-col__main a::attr(href)").extract()
            for page in content_pages:
                yield response.follow(page, self.parse_content2)

            # Follow the link to the next page only if it exists
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)
        
        
        elif "http://global.nba.com" in response.url:
            next_link = response.css("div.nav-links a:last-of-type::attr(href)").get()

            content_pages = response.css("article.entry.archive-entry.entry__type_news h1 a::attr(href)").extract()
            for page in content_pages:
                yield response.follow(page, self.parse_content3)
            
            # Follow the link to the next page only if it exists
            if next_link is not None:
                yield response.follow(next_link, callback=self.parse)

        elif "https://en.wikipedia.org" in response.url:

            content_pages = response.css(".div-col a::attr(href)").extract()
            for page in content_pages:
                yield response.follow(page, self.parse_content4)




    def parse_content(self, response):
        title = response.css("div.article-title::text").get().strip()
        content = response.css("div.article-body p::text").getall()
        yield {
            "SourceLink": referer_str(response.request),
    		"Link": response.url,
            "Title": str(title),
            "Content": str(content)
        }

    def parse_content2(self, response):
        title = response.css("h1.c-page-title::text").get().strip()
        content = response.css("main#content p:first-of-type::text").getall()
        yield {
            "SourceLink": referer_str(response.request),
    		"Link": response.url,
            "Title": str(title),
            "Content": str(content)
        }

    def parse_content3(self, response):
        title = response.css("h1 a::text").get().strip()
        content = response.css("div.entry__content.entry-content p::text").getall()
        yield {
            "SourceLink": referer_str(response.request),
    		"Link": response.url,
            "Title": str(title),
            "Content": str(content)
        }

    def parse_content4(self, response):
        title = response.css("h1#firstHeading span::text").get().strip()
        para = response.css("div.mw-parser-output > p:first-of-type ~ p:nth-of-type(-n+3)").get()
        if para:
            clean_part = response.css('div.mw-parser-output > p:first-of-type ~ p:nth-of-type(-n+3) ::text').getall()
            content = "".join(clean_part).strip()
        yield {
            "SourceLink": referer_str(response.request),
    		"Link": response.url,
            "Title": str(title),
            "Content": str(content)
        }


class BbForeverSpider(scrapy.Spider):

    name = "bbForever"
    allowed_domains = ["basketballforever.com"]
    start_urls = ["https://basketballforever.com/latest-news"]
    
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter'
    }

    def parse(self, response):
        if "https://basketballforever.com/latest-news" in response.url:

            next_page = response.css(".nav-previous a::attr(href)").get()
            content_pages = response.css(".entry-title a::attr(href)").extract()
            for page in content_pages:
                yield response.follow(page, self.parse_content)

            # Follow the link to the next page only if it exists
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)


    def parse_content(self, response):
        title = response.css(".entry-title::text").get().strip()
        content = response.css(".mailmunch-forms-before-post+ p::text").getall()
        yield {
            "SourceLink": referer_str(response.request),
    		"Link": response.url,
            "Title": str(title),
            "Content": str(content)
        }
                

class BbLifeSpider(scrapy.Spider):

    name = "bbLife"
    allowed_domains = ["ballislife.com"]
    start_urls = ["https://ballislife.com/news/"]
    
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter'
    }

    def parse(self, response):
        if "https://ballislife.com/news/" in response.url:

            next_page = response.css("a.next::attr(href)").get()
            content_pages = response.css(".entry-title a::attr(href)").extract()
            for page in content_pages:
                yield response.follow(page, self.parse_content)

            # Follow the link to the next page only if it exists
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)


    def parse_content(self, response):
        title = response.css(".entry-title::text").get().strip()
        content = response.css(".entry-content > p:nth-of-type(-n+2)::text").getall()
        yield {
            "SourceLink": referer_str(response.request),
    		"Link": response.url,
            "Title": str(title),
            "Content": str(content)
        }



class BbEspnSpider(CrawlSpider):
    name = "bbEspn"
    allowed_domains = ["espn.com"]
    start_urls = ["https://www.espn.com/nba/story/_/id/36191140/heat-rally-stun-bulls-face-bucks-first-round", "https://www.espn.com/nba/story/_/id/36127955/with-lebron-front-row-bronny-james-leads-us-nike-hoop-summit"]
    le = LinkExtractor(allow=r"https://www.espn.com/nba/story/.*")
    rule1 = Rule(le, callback='parse_item', follow=True)
    rules = (rule1,)
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter'
    }

    def parse_item(self, response): 
        title = response.css("h1:first-of-type::text").get().strip()
        content = response.css("article:first-of-type .article-body > p:nth-of-type(-n+2)::text").getall()
        yield {
            "SourceLink": referer_str(response.request),
    		"Link": response.url,
            "Title": str(title),
            "Content": str(content)
        }

        


class BbSportingSpider(scrapy.Spider):
    name = "bbSporting"
    allowed_domains = ["sportingnews.com"]
    start_urls = ["https://www.sportingnews.com/us/nba/news"]
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter'
    }

    def parse(self, response):
        if "https://www.sportingnews.com/us/nba/news" in response.url:

            next_page = response.css("li a.button::attr(href)").get()
            content_pages = response.css(".list-item__title a::attr(href)").extract()
            for page in content_pages:
                yield response.follow(page, self.parse_content)

            # Follow the link to the next page only if it exists
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    def parse_content(self, response): 
        title = response.css(".field--type-string::text").get().strip()
        content = response.css("p:nth-child(2), p:nth-child(1)::text").getall()[:2]
        yield {
            "SourceLink": referer_str(response.request),
    		"Link": response.url,
            "Title": str(title),
            "Content": str(content)
        }


class BbNewsSpider(CrawlSpider):
    name = "bbNews"
    allowed_domains = ["basketballnews.com"]
    start_urls = ["https://www.basketballnews.com/"]
    le = LinkExtractor(allow=r"https://www.basketballnews.com/stories/.*")
    rule1 = Rule(le, callback='parse_item', follow=True)
    rules = (rule1,)
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter'
    }

    def parse_item(self, response): 
        title = response.css(".r-1w50u8q.r-1xnzce8 ::text").get().strip()
        content = response.css("p::text").getall()[:2]
        yield {
            "SourceLink": referer_str(response.request),
    		"Link": response.url,
            "Title": str(title),
            "Content": str(content)
        }


class BbNcaaSpider(CrawlSpider):
    name = "bbNcaa"
    allowed_domains = ["ncaa.com"]
    start_urls = ["https://www.ncaa.com/news/basketball-men/article/2022-12-05/college-basketballs-net-rankings-explained?utm_campaign=mbk-rr-links"]
    le = LinkExtractor(allow=r"https://www.ncaa.com/news/basketball-men/article/.*")
    rule1 = Rule(le, callback='parse_item', follow=True)
    rules = (rule1,)
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter'
    }

    def parse_item(self, response): 
        title = response.css(".headline ::text").get().strip()
        content = response.css(".node__content div p ::text").getall()[:2]
        yield {
            "SourceLink": referer_str(response.request),
    		"Link": response.url,
            "Title": str(title),
            "Content": str(content)
        }

