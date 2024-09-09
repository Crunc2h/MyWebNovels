from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from novel_scraper.native.cout_custom import COut

BROWSE_BASE_URL = "https://www.webnovelworld.org/browse/genre-all-25060123/order-new/status-all"

def webnovelpub__scrape_all_novel_links(base_url=BROWSE_BASE_URL, default_implicit_wait=1):
    header = "WEBNOVELPUB::NOVEL_LINKS_SCRAPER"
    driver = webdriver.Chrome()
    driver.get(base_url)
    max_page = "-1"
    current_page = "0"
    
    page_links = []
    novel_links = []

    COut.broadcast(message=f"Beginning scraping novel links from {base_url}...", style="init", header=header)

    while int(current_page) <= int(max_page) or max_page == "-1":
        novels_on_page = driver.find_elements(By.CSS_SELECTOR, ".novel-item a")
        all_page_numbers_on_page = driver.find_element(By.CSS_SELECTOR, "ul.pagination").find_elements(By.CSS_SELECTOR, "li a")

        for page in all_page_numbers_on_page:
            if page.text not in [">>", ">", "<", "<<"]:
                page_links.append((page.text, page.get_attribute("href")))
        
        current_page = driver.find_element(By.CSS_SELECTOR, "li.active").text
        if max_page == "-1": max_page = page_links[-1][1].get_attribute("href").split("page=")[1]

        novels_links_added = 0
        for i in range(0, len(novels_on_page)):
            href = novels_on_page[i].get_attribute("href")
            if href not in novel_links:
                novel_links.append(href)
                novels_links_added += 1

        driver.implicitly_wait(default_implicit_wait)

        COut.broadcast(message=f"Current page is {current_page}", style="progress", header=header)
        COut.broadcast(message=f"Found {novels_links_added} novels", style="progress", header=header)

        if current_page == max_page and max_page != 1:
            COut.broadcast(message=f"Scraping complete novel base links is complete.", style="success", header=header)
            COut.broadcast(message=f"Found a total of {novel_links} novels from {max_page} pages.", style="success", header=header)
            return novel_links
        
        next_page = list(filter(lambda page: int(current_page) + 1 == int(page[0]), page_links))[0][1]
        driver.get(next_page)

def webnovelpub__scrape_novel_profile(novel_base_link, default_implicit_wait=1): 
    header = "WEBNOVELPUB::NOVEL_PROFILE_SCRAPER"
    driver = webdriver.Chrome()
    driver.get(novel_base_link)

    COut.broadcast(message=f"Beginning scraping novel profile from {novel_base_link}...", style="init", header=header)

    name = driver.find_element(By.CSS_SELECTOR, ".novel-title").text
    author_name = driver.find_element(By.CSS_SELECTOR, ".author").text
    number_of_chapters = int(driver.find_element(By.CSS_SELECTOR, ".header-stats > span:nth-child(1) > strong:nth-child(1)").text) 
    try: 
        completion_status = driver.find_element(By.CSS_SELECTOR, ".completed").text
    except NoSuchElementException:
        completion_status = driver.find_element(By.CSS_SELECTOR, ".ongoing").text
    
    summary = "\n".join([p_element.text for p_element in driver.find_element(By.CSS_SELECTOR, "div.content").find_elements(By.TAG_NAME, "p")])
    categories = [category.text for category in driver.find_element(By.CSS_SELECTOR, ".categories").find_elements(By.TAG_NAME, "li")]
    tags = [tag.text for tag in driver.find_element(By.CSS_SELECTOR, ".tags").find_elements(By.TAG_NAME, "li")]

    driver.implicitly_wait(default_implicit_wait)

    COut.broadcast(message=f"Scraping the profile for novel {name} is complete.", style="success", header=header)
    
    return {
        "author_name": author_name,
        "name": name,
        "number_of_chapters": number_of_chapters,
        "completion_status": completion_status,
        "summary": summary,
        "categories": categories,
        "tags": tags
    }

def webnovelpub__scrape_novel_chapter_profiles(novel_base_link, default_implicit_wait=1): 
    header = "WEBNOVELPUB::NOVEL_CHAPTER_PROFILES_SCRAPER"
    driver = webdriver.Chrome()
    driver.get(novel_base_link)

    COut.broadcast(message=f"Beginning scraping chapter profiles from {novel_base_link}...", style="init", header=header)

    novel_chapters_button = driver.find_element(By.CSS_SELECTOR, "a.grdbtn:nth-child(1)")
    novel_chapters_button.click()

    driver.implicitly_wait(default_implicit_wait)
    
    chapter_profiles = []
    page_links = []

    max_page = "-1"
    current_page = "0"

    while int(current_page) <= int(max_page) or max_page == "-1":
        chapters_on_page = driver.find_element(By.CSS_SELECTOR, ".chapter-list").find_elements(By.TAG_NAME, "li")
        all_page_numbers_on_page = driver.find_element(By.CSS_SELECTOR, "ul.pagination").find_elements(By.CSS_SELECTOR, "li a")

        for page in all_page_numbers_on_page:
            if page.text not in [">>", ">", "<", "<<"]:
                page_links.append((page.text, page.get_attribute("href")))

        current_page = driver.find_element(By.CSS_SELECTOR, "li.active").text
        if max_page == "-1": max_page = page_links[-1][1].split("page=")[1]

        chapter_profiles_added = 0
        for i in range(0, len(chapters_on_page)):
            anchor = chapters_on_page[i].find_element(By.TAG_NAME, "a")
            href = anchor.get_attribute("href")
            if href not in [chapter["link"] for chapter in chapter_profiles]:
                chapter_name = anchor.find_element(By.CLASS_NAME, "chapter-title").text
                chapter_no = anchor.find_element(By.CLASS_NAME, "chapter-no").text
                chapter_source_update_time = anchor.find_element(By.CLASS_NAME, "chapter-update").text
                chapter = {
                    "link": href,
                    "name": chapter_name,
                    "number": chapter_no,
                    "source_update_time": chapter_source_update_time
                }
                chapter_profiles.append(chapter)
                chapter_profiles_added += 1   

        driver.implicitly_wait(default_implicit_wait)

        COut.broadcast(message=f"Current page is {current_page}", style="progress", header=header)
        COut.broadcast(message=f"Found {chapter_profiles_added} chapter profiles", style="progress", header=header)

        if current_page == max_page:
            COut.broadcast(message=f"Scraping chapter profiles from {novel_base_link} is complete.", style="success", header=header)
            COut.broadcast(message=f"Found a total of {len(chapter_profiles)} chapter profiles from {max_page} pages.", style="success", header=header)
            return chapter_profiles
        
        next_page = list(filter(lambda page: int(current_page) + 1 == int(page[0]), page_links))[0][1]
        driver.get(next_page)


def webnovelpub__scrape_novel_chapter(chapter_profile, default_implicit_wait=1):
    header = "WEBNOVELPUB::NOVEL_CHAPTERS_SCRAPER"
    driver = webdriver.Chrome()
    driver.get(chapter_profile.link)

    COut.broadcast(message=f"Scraping chapter {chapter_profile.number}, {chapter_profile.name}...", style="init", header=header)

    paragraph_elements = driver.find_element(By.ID, "chapter-container").find_elements(By.TAG_NAME, "p")
    driver.implicitly_wait(default_implicit_wait)
    
    chapter_text = "\n".join([element.text for element in paragraph_elements])

    COut.broadcast(message=f"Scraping of chapter {chapter_profile.number}-{chapter_profile.name} complete, chapter char count -- {len(chapter_text)}", style="success", header=header)

    return chapter_text

