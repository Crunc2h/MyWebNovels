import novel_scraper.native.webnovelpub as webnovelpub
import enums_configs.native.scraping_manager_cfg as sm_cfg


class ScrapingManagerConfig:
    def get_config(source_site):
        if source_site == "webnovelpub.com":
            return {
                "scrape_all_novel_links": webnovelpub.webnovelpub__scrape_all_novel_links,
                "scrape_novel_profile": webnovelpub.webnovelpub__scrape_novel_profile,
                "scrape_novel_chapter_profiles": webnovelpub.webnovelpub__scrape_novel_chapter_profiles,
                "scrape_novel_chapters": webnovelpub.webnovelpub__scrape_novel_chapter,
            }


class ScrapingManager:
    def __init__(self, source_site):
        config = ScrapingManagerConfig.get_config(source_site)
        self.progress_failure_grace_period = sm_cfg.PROGRESS_FAILURE_GRACE_PERIOD
        self.sc_all_novel_links = config["scrape_all_novel_links"]
        self.sc_novel_profile = config["scrape_novel_profile"]
        self.sc_novel_chapter_profiles = config["scrape_novel_chapter_profiles"]
        self.sc_novel_chapters = config["scrape_novel_chapters"]

    def __scrape_all_novel_links(self, loader):
        return self.sc_all_novel_links(
            progress_failure_grace_period=self.progress_failure_grace_period,
            loader=loader,
        )

    def __scrape_novel_profile(self, novel_base_link, loader):
        return self.sc_novel_profile(
            progress_failure_grace_period=self.progress_failure_grace_period,
            loader=loader,
            novel_base_link=novel_base_link,
        )

    def __scrape_novel_chapter_profiles(self, novel_base_link, loader):
        return self.sc_novel_chapter_profiles(
            progress_failure_grace_period=self.progress_failure_grace_period,
            loader=loader,
            novel_base_link=novel_base_link,
        )

    def __scrape_novel_chapters(self, chapter_profile, loader):
        return self.sc_novel_chapters(
            progress_failure_grace_period=self.progress_failure_grace_period,
            loader=loader,
            chapter_profile=chapter_profile,
        )

    def get_all_novel_links(
        self,
        loader,
    ):
        return self.__scrape_all_novel_links(loader=loader)

    def get_novel_profile(
        self,
        novel_base_link,
        loader,
    ):
        return self.__scrape_novel_profile(
            loader=loader,
            novel_base_link=novel_base_link,
        )

    def get_novel_chapter_profiles(self, novel_base_link, loader):
        return self.__scrape_novel_chapter_profiles(
            loader=loader,
            novel_base_link=novel_base_link,
        )

    def get_novel_chapter(self, chapter_profile, loader):
        return self.__scrape_novel_chapters(
            loader=loader,
            chapter_profile=chapter_profile,
        )
