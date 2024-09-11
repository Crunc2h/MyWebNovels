import novel_scraper.native.cout_custom as cout
import novel_scraper.native.ns_exceptions as ns_exc
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


BROWSE_BASE_URL = (
    "https://www.webnovelworld.org/browse/genre-all-25060123/order-new/status-all"
)


def webnovelpub__scrape_all_novel_links(
    progress_failure_grace_period,
    loader,
    base_url=BROWSE_BASE_URL,
    default_implicit_wait=1,
):
    header = "WEBNOVELPUB::NOVEL_LINKS_SCRAPER"
    loader = cout.COutLoading()
    GRACE_PERIOD_CURRENT = 0

    cout.COut.broadcast(
        message=f"Beginning scraping novel links from {base_url}...",
        style="init",
        header=header,
    )

    while True:
        try:
            pages_traversed = 0
            novel_links = []

            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            driver.get(base_url)

            while True:
                novels_on_page = driver.find_elements(By.CSS_SELECTOR, ".novel-item a")
                novels_links_added = 0
                for i in range(0, len(novels_on_page)):
                    href = novels_on_page[i].get_attribute("href")
                    if href not in novel_links:
                        novel_links.append(href)
                        novels_links_added += 1

                driver.implicitly_wait(default_implicit_wait)

                cout.COut.broadcast(
                    message=f"{pages_traversed} pages traversed, found {novels_links_added} novels",
                    style="progress",
                    header=header,
                    loader=loader,
                )

                try:
                    next_page = (
                        driver.find_element(By.CSS_SELECTOR, ".PagedList-skipToNext")
                        .find_element(By.TAG_NAME, "a")
                        .get_attribute("href")
                    )
                    pages_traversed += 1
                    driver.get(next_page)
                except NoSuchElementException:
                    cout.COut.broadcast(
                        message=f"Scraping complete novel base links is complete.",
                        style="success",
                        header=header,
                    )
                    cout.COut.broadcast(
                        message=f"Found a total of {len(novel_links)} novels from {pages_traversed} pages.",
                        style="success",
                        header=header,
                    )
                    return novel_links
        except Exception as ex:
            GRACE_PERIOD_CURRENT += 1
            if GRACE_PERIOD_CURRENT >= progress_failure_grace_period:
                cout.COut.broadcast(
                    message=ns_exc.SCRAPER_PROCESS_FAILURE_COMPLETE_BROADCAST,
                    style="warning",
                    header=header,
                )
                raise ns_exc.ScraperProcessFailureException(
                    ex, driver.current_url, header
                )
            cout.COut.broadcast(
                message=ns_exc.SCRAPER_PROCESS_FAILURE_RETRY_BROADCAST.format(
                    current_grace_period=GRACE_PERIOD_CURRENT,
                    max_grace_period=progress_failure_grace_period,
                ),
                style="warning",
                header=header,
            )


def webnovelpub__scrape_novel_profile(
    progress_failure_grace_period,
    loader,
    novel_base_link,
    default_implicit_wait=1,
):
    header = "WEBNOVELPUB::NOVEL_PROFILE_SCRAPER"
    GRACE_PERIOD_CURRENT = 0

    cout.COut.broadcast(
        message=f"Scraping novel profiles...",
        style="progress",
        header=header,
        loader=loader,
    )

    while True:
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            driver.get(novel_base_link)
            name = driver.find_element(By.CSS_SELECTOR, ".novel-title").text
            author_name = driver.find_element(By.CSS_SELECTOR, ".author").text
            number_of_chapters = int(
                driver.find_element(
                    By.CSS_SELECTOR,
                    ".header-stats > span:nth-child(1) > strong:nth-child(1)",
                ).text
            )

            try:
                completion_status = driver.find_element(
                    By.CSS_SELECTOR, ".completed"
                ).text
            except NoSuchElementException:
                completion_status = driver.find_element(
                    By.CSS_SELECTOR, ".ongoing"
                ).text

            summary = "\n".join(
                [
                    p_element.text
                    for p_element in driver.find_element(
                        By.CSS_SELECTOR, "div.content"
                    ).find_elements(By.TAG_NAME, "p")
                ]
            )
            categories = [
                category.text
                for category in driver.find_element(
                    By.CSS_SELECTOR, ".categories"
                ).find_elements(By.TAG_NAME, "li")
            ]
            tags = [
                tag.text
                for tag in driver.find_element(By.CSS_SELECTOR, ".tags").find_elements(
                    By.TAG_NAME, "li"
                )
            ]

            driver.implicitly_wait(default_implicit_wait)

            return {
                "author_name": author_name,
                "name": name,
                "number_of_chapters": number_of_chapters,
                "completion_status": completion_status,
                "summary": summary,
                "categories": categories,
                "tags": tags,
            }
        except Exception as ex:
            GRACE_PERIOD_CURRENT += 1
            if GRACE_PERIOD_CURRENT >= progress_failure_grace_period:
                cout.COut.broadcast(
                    message=ns_exc.SCRAPER_PROCESS_FAILURE_COMPLETE_BROADCAST,
                    style="warning",
                )
                raise ns_exc.ScraperProcessFailureException(
                    ex, driver.current_url, header
                )
            cout.COut.broadcast(
                message=ns_exc.SCRAPER_PROCESS_FAILURE_RETRY_BROADCAST.format(
                    current_grace_period=GRACE_PERIOD_CURRENT
                ),
                style="warning",
                header=header,
            )


def webnovelpub__scrape_novel_chapter_profiles(
    progress_failure_grace_period, loader, novel_base_link, default_implicit_wait=1
):
    header = "WEBNOVELPUB::NOVEL_CHAPTER_PROFILES_SCRAPER"
    GRACE_PERIOD_CURRENT = 0

    cout.COut.broadcast(
        message=f"Beginning scraping chapter profiles from {novel_base_link}...",
        style="init",
        header=header,
    )

    while True:
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            driver.get(novel_base_link)
            novel_chapters_button = driver.find_element(
                By.CSS_SELECTOR, "a.grdbtn:nth-child(1)"
            )
            novel_chapters_button.click()
            driver.implicitly_wait(default_implicit_wait)

            chapter_profiles = []
            pages_traversed = 0

            while True:
                chapters_on_page = driver.find_element(
                    By.CSS_SELECTOR, ".chapter-list"
                ).find_elements(By.TAG_NAME, "li")

                chapter_profiles_added = 0
                for i in range(0, len(chapters_on_page)):
                    anchor = chapters_on_page[i].find_element(By.TAG_NAME, "a")
                    href = anchor.get_attribute("href")
                    if href not in [chapter["link"] for chapter in chapter_profiles]:
                        chapter_name = anchor.find_element(
                            By.CLASS_NAME, "chapter-title"
                        ).text
                        chapter_no = anchor.find_element(
                            By.CLASS_NAME, "chapter-no"
                        ).text
                        chapter_source_update_time = anchor.find_element(
                            By.CLASS_NAME, "chapter-update"
                        ).text
                        chapter = {
                            "link": href,
                            "name": chapter_name,
                            "number": chapter_no,
                            "source_update_time": chapter_source_update_time,
                        }
                        chapter_profiles.append(chapter)
                        chapter_profiles_added += 1

                driver.implicitly_wait(default_implicit_wait)

                cout.COut.broadcast(
                    message=f"{pages_traversed} pages traversed, found {chapter_profiles_added} chapter profiles",
                    style="progress",
                    header=header,
                    loader=loader,
                )

                try:
                    next_page = (
                        driver.find_element(By.CSS_SELECTOR, ".PagedList-skipToNext")
                        .find_element(By.TAG_NAME, "a")
                        .get_attribute("href")
                    )
                    pages_traversed += 1
                    driver.get(next_page)
                except NoSuchElementException:
                    cout.COut.broadcast(
                        message=f"Scraping chapter profiles from {novel_base_link} is complete.",
                        style="success",
                        header=header,
                    )
                    cout.COut.broadcast(
                        message=f"Found a total of {len(chapter_profiles)} chapter profiles from {pages_traversed} pages.",
                        style="success",
                        header=header,
                    )
                    return chapter_profiles
        except Exception as ex:
            GRACE_PERIOD_CURRENT += 1
            if GRACE_PERIOD_CURRENT >= progress_failure_grace_period:
                cout.COut.broadcast(
                    message=ns_exc.SCRAPER_PROCESS_FAILURE_COMPLETE_BROADCAST,
                    style="warning",
                    header=header,
                )
                raise ns_exc.ScraperProcessFailureException(
                    ex, driver.current_url, header
                )
            cout.COut.broadcast(
                message=ns_exc.SCRAPER_PROCESS_FAILURE_RETRY_BROADCAST.format(
                    current_grace_period=GRACE_PERIOD_CURRENT
                ),
                style="warning",
                header=header,
            )


def webnovelpub__scrape_novel_chapter(
    progress_failure_grace_period, loader, chapter_profile, default_implicit_wait=1
):
    header = "WEBNOVELPUB::NOVEL_CHAPTERS_SCRAPER"
    GRACE_PERIOD_CURRENT = 0

    cout.COut.broadcast(
        message=f"Scraping chapter {chapter_profile.name}...",
        style="progress",
        header=header,
        loader=loader,
    )
    while True:
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            driver.get(chapter_profile.link)
            paragraph_elements = driver.find_element(
                By.ID, "chapter-container"
            ).find_elements(By.TAG_NAME, "p")
            driver.implicitly_wait(default_implicit_wait)

            chapter_text = "\n".join([element.text for element in paragraph_elements])
            return chapter_text
        except Exception as ex:
            GRACE_PERIOD_CURRENT += 1
            if GRACE_PERIOD_CURRENT >= progress_failure_grace_period:
                cout.COut.broadcast(
                    message=ns_exc.SCRAPER_PROCESS_FAILURE_COMPLETE_BROADCAST,
                    style="warning",
                    header=header,
                )
                raise ns_exc.ScraperProcessFailureException(
                    ex, driver.current_url, header
                )
            cout.COut.broadcast(
                message=ns_exc.SCRAPER_PROCESS_FAILURE_RETRY_BROADCAST.format(
                    current_grace_period=GRACE_PERIOD_CURRENT
                ),
                style="warning",
                header=header,
            )
