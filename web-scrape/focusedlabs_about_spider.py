import scrapy
import w3lib.html


class FocusedLabsAboutSpider(scrapy.Spider):
    name = "focusedlabs"
    start_urls = [
        "https://focusedlabs.io/about",
    ]

    def parse(self, response):

        body = response.xpath("//body")

        for h1 in body.xpath('.//h1'):
            h1_text = h1.get()
            h1_text = w3lib.html.remove_tags(h1_text).strip()
            yield {
                "h1": h1_text
            }
        for h2 in body.xpath('.//h2'):
            h2_text = h2.get()
            h2_text = w3lib.html.remove_tags(h2_text).strip()
            yield {
                "h2": h2_text
            }
        for h3 in body.xpath('.//h3'):
            text = h3.get()
            text = w3lib.html.remove_tags(text).strip()
            yield {
                "h3": text
            }
        for p in body.xpath(".//p"):
            text = p.get()
            text = w3lib.html.remove_tags(text).strip()
            yield {
                "p": text
            }

        # next_page = response.css("li.hs-menu-item a::attr(href)").get()
        # if next_page is not None:
        #     next_page = response.urljoin(next_page)
        #     yield scrapy.Request(next_page, callback=self.parse)


