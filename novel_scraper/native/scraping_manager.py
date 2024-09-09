from source_site import SourceSite
from webnovelpub import *

class ScrapingManagerConfig:
    def get_config(source_site):
        if source_site == SourceSite.WEBNOVELPUB:
            return {
                "scrape_all_novel_links": webnovelpub__scrape_all_novel_links,
                "scrape_novel_profile": webnovelpub__scrape_novel_profile,
                "scrape_novel_chapter_profiles": webnovelpub__scrape_novel_chapter_profiles,
                "scrape_novel_chapters": webnovelpub__scrape_novel_chapter
            }

class ScrapingManager:
    def __init__(self, source_site=SourceSite.WEBNOVELPUB):
        config = ScrapingManagerConfig.get_config(source_site)
        self.sc_all_novel_links = config["scrape_all_novel_links"]
        self.sc_novel_profile = config["scrape_novel_profile"]
        self.sc_novel_chapter_profiles = config["scrape_novel_chapter_profiles"]
        self.sc_novel_chapters = config["scrape_novel_chapters"]
    
    def __scrape_all_novel_links(self): return self.sc_all_novel_links()
    def __scrape_novel_profile(self, novel_base_link): return self.sc_novel_profile(novel_base_link)   
    def __scrape_novel_chapter_profiles(self, novel_base_link): return self.sc_novel_chapter_profiles(novel_base_link)    
    def __scrape_novel_chapters(self, chapter_profile): return self.sc_novel_chapters(chapter_profile)
    
    def get_all_novel_links(self): return self.__scrape_all_novel_links()
    def get_novel_profile(self, novel_base_link): return self.__scrape_novel_profile(novel_base_link)
    def get_novel_chapter_profiles(self, novel_base_link): return self.__scrape_novel_chapter_profiles(novel_base_link)
    def get_novel_chapter(self, chapter_profile): return self.__scrape_novel_chapters(chapter_profile)