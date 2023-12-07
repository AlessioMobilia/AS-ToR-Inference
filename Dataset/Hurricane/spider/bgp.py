import scrapy
from pathlib import Path
visited_peer = []
visited_up = []
save_peer ='peer.txt'
save_up ='up.txt'

class BgpSpider(scrapy.Spider):
    name = "bgp"
    
    allowed_domains = ["bgp.he.net"]

    def make_request(self, asn):
        self.log(f"make_request")
       
    
    def start_requests(self):
        with open(save_peer, 'r') as file:
            for line in file:
                visited_peer.append(line.strip())
        with open(save_up, 'r') as file:
            for line in file:
                visited_up.append(line.strip())

        asn = 59850
        listed = [59850,202156,206179,60186,203504,204827,35119,51283,41187,206515,202344,59530,47819]
        url = f"https://bgp.he.net/AS{asn}#_peers"
        url_upstream = f"https://bgp.he.net/AS{asn}#_asinfo"

        for a in visited_peer:
            if a not in visited_up:
                yield scrapy.Request(url=url_upstream, callback=self.parse_upstream)
        for a in visited_up:
            if a not in visited_peer:
                yield scrapy.Request(url=url, callback=self.parse)
        for a in listed:
            if a not in visited_peer:
                yield scrapy.Request(url=url, callback=self.parse)
            if a not in visited_up:
                yield scrapy.Request(url=url_upstream, callback=self.parse_upstream)
        
            

    def parse(self, response):
        filename = "peer.csv"
        if response.status!=200:
            return
        asn = response.url.split("/")[-1]
        asn = asn.split('#')[0].replace("AS", "")
        peers = response.css("#peers td a::attr(title)").re('AS\d+')
        text=''
        for pr in peers:
            pr=pr.replace("AS", "")
            if(pr not in visited_peer):             
                text += f"{asn}|{pr}|0\n"
        with open(filename, 'a') as file:
            file.write(text)
        self.log(f"Saved file {filename}")

        with open(save_peer, 'a') as file:
            file.write(asn+'\n')
        visited_peer.append(asn)
        self.log(f"Saved file {save_peer}")


        for pr in peers:
            pr=pr.replace("AS", "")
            url = f"https://bgp.he.net/AS{pr}#_peers"
            url_upstream = f"https://bgp.he.net/AS{pr}#_asinfo"
            if pr not in visited_up:
                yield scrapy.Request(url=url_upstream, callback=self.parse_upstream)
            if pr not in visited_peer:
                yield scrapy.Request(url=url, callback=self.parse)
            


    def parse_upstream(self, response):
        if response.status!=200:
            return
        filename = "upstream.csv"
        asn = response.url.split("/")[-1]
        asn = asn.split('#')[0].replace("AS", "")
        upstream = response.css("#asinfo table")[0].css('td a::text').re('AS\d+')

        text=''
        for up in upstream:
            up=up.replace("AS", "")  
            text += f"{up}|{asn}|1\n"
        with open(filename, 'a') as file:
            file.write(text)
        self.log(f"Saved file {filename}")

        with open(save_up, 'a') as file:
            file.write(asn+'\n')
        visited_up.append(asn)
        self.log(f"Saved file {save_up}")

        for up in upstream:
            up=up.replace("AS", "")
            url = f"https://bgp.he.net/AS{up}#_peers"
            url_upstream = f"https://bgp.he.net/AS{up}#_asinfo"
            if up not in visited_up:
                yield scrapy.Request(url=url_upstream, callback=self.parse_upstream)
            if up not in visited_peer:
                yield scrapy.Request(url=url, callback=self.parse)
            

    

