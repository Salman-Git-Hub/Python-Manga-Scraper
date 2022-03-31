import json
import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper(browser='chrome', delay=7)

class MangaNato():
    
    def __init__(self):
        self.genres = {}
        self.__load_genres()
        return


    def get_genre_link(self, genre: str, state = None, type = None) -> str:
        """Get the genre link for a given genre!

        Args:
            genre (str): Genre name.
            state (str, optional): Genre Link state for genre="ALL" only. Defaults to None.
            type (str, optional): Genre Link type, for genre="ALL" Only. Defaults to None.

        Raises:
            ValueError: If invalid name is give or if the genre does not exists.

        Returns:
            str: Returns the genre link.
        """
        if state != None:
            # Ongoing and completed
            link = self.genres.get("ALL").get("STATE")
        elif type != None:
            # Neweset and topview
            link = self.genres.get("ALL").get("TYPE")
        else:
            try:
                link = self.genres[genre.upper()]
            except KeyError:
                raise ValueError("Invalid genre")
        return link
            


    def get_recent_updates(self, page_limit: int = 1) -> dict:
        """Get the recently added manga.

        Args:
            page_limit (int, optional): No. of pages to get results from. Defaults to 1.

        Returns:
            dict: Returns a dict containing multiple dicts.
        """
        recent_data = {}
        i = 1
        for n in range(1, page_limit + 1):
            url = f"https://manganato.com/genre-all/{str(n)}"
            response = scraper.get(url).text
            soup = BeautifulSoup(response, 'lxml')
            div_lst = soup.find("div", attrs={"class":"panel-content-genres"}).find_all("div", attrs={"class":"content-genres-item"})
            for div in div_lst:
                nsoup = BeautifulSoup(str(div), 'lxml')
                img = nsoup.find("img")['src']
                title, url = nsoup.find("h3").find("a").text, nsoup.find("h3").find("a")['href']
                lch = nsoup.find_all("a")[2].text
                recent_data[str(i)] = {
                    "Title": title,
                    "Cover": img,
                    "Url": url,
                    "Latest_Chapter": lch
                }
                i += 1
        return recent_data
        
        
    def get_mange_info(self, url) -> dict:
        """Gets the manga info from a url.

        Args:
            url (str): URL of the manga.

        Returns:
            dict: Returns a dict containing the manga's info.
        """
        info_data = {}
        rsp = scraper.get(url).text
        soup = BeautifulSoup(rsp, 'lxml')
        cover = soup.find("div", attrs={"class":"story-info-left"}).find("img")['src']
        plot = soup.find('div', attrs={"class":"panel-story-info-description"}).text[15:].replace("<br>", "").replace("Summary:", "")
        info_block = soup.find("div", attrs={"class":"story-info-right"})
        title = info_block.find("h1").text
        
        main_table = info_block.find("table", attrs={'class':'variations-tableInfo'}).find_all("tr")
        info_data = {
            "Title": title,
            "Plot": plot if "MangaNato.com" not in plot else "",
            "Cover": cover
        }
        info_data['Genre'] = [gen.text for gen in main_table[-1].find("td", attrs={"class":"table-value"}).find_all("a", attrs={"class":"a-h"})]
        # for only chapter (with name) no. ------> li.find("a").text[8:]
        # [['chapeter no. with name', 'link','date'], .......]
        
        info_data['Chapters'] = [[li.find("a").text, li.find("a")['href'], li.find("span", attrs={"class":"chapter-time text-nowrap"}).text] for li in soup.find("div", attrs={"class":'panel-story-chapter-list'}).find("ul", attrs={"class":"row-content-chapter"}).find_all("li", attrs={"class":"a-h"})]
        z = main_table.pop(-1)
        try:
            alternative_name = main_table[0].find("h2").text.split(" ; ")
            info_data["Alternative_names"] = alternative_name
        except (AttributeError, IndexError):
            pass
        try:
            authors = main_table[1].find("a", attrs={"class":"a-h"}).text.split(", ")
            info_data['Authors'] = authors
        except (AttributeError, IndexError):
            pass
        try:
            status = main_table[2].find("td", attrs={"class":"table-value"}).text
            info_data['Status'] = status
        except (AttributeError, IndexError):
            pass
        return info_data


    def get_genre_list(self, url, page_limit: int = 1) -> dict:
        """Gets a list of manga from a genre url.

        Args:
            url (str): Genre URL.
            page_limit (int, optional): No. of pages to get results from. Defaults to 1.

        Returns:
            dict: Returns a dict containing multiple dicts
        """
        genre_data = {}
        n = 1
        for i in range(1, page_limit + 1):
            res = scraper.get(f"{url}/{str(i)}").text
            soup = BeautifulSoup(res, 'lxml')
            cont = soup.find("div", attrs={"class": "panel-content-genres"}).find_all("div", attrs={'class':"content-genres-item"})
            for div in cont:
                nsoup = BeautifulSoup(str(div), 'lxml')
                img = nsoup.find("a", attrs={"class": "genres-item-img"}).find("img")['src']
                nsoup = nsoup.find("div", attrs={"class": "genres-item-info"})
                title = nsoup.find("h3").find("a").text
                url = nsoup.find("h3").find('a')['href']
                chapter = nsoup.find_all("a")[1].text
                genre_data[str(n)] = {
                    "Title": title,
                    "Cover": img,
                    "Url": url,
                    "Latest_Chapter": chapter
                }
                n += 1
        return genre_data


    def get_chapter_images(self, url) -> list:
        """Gets the list of all images for a particular manga chapter.

        Args:
            url (str): URL of the manga's chapter.

        Returns:
            list: Returns a list of url of the images.
        """
        rs = scraper.get(url).text
        soup = BeautifulSoup(rs, 'lxml')
        img_cont = soup.find("div", attrs={"class": "container-chapter-reader"}).find_all("img")
        img_links = [img['src'] for img in img_cont]
        return img_links
    
    def __load_genres(self):
        with open("genre.json", 'r') as file:
            self.genres = json.load(file).get("Manganato")