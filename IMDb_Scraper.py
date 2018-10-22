from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import time


def getTime():
    return time.time()


class IMDBScraper:
    num_pages = 100
    start_page = 1

    page_size = 100
    num_movies = num_pages * page_size
    movie_index = 0
    movie_list = []
    master_personnel_list = []
    master_role_list = []
    curr_movie = 1
    page_num = 23
    time_count = []
    pps = []
    go = True

    def simple_get(self, url):
        """
        Attempts to get the content at `url` by making an HTTP GET request.
        If the content-type of response is some kind of HTML/XML, return the
        text content, otherwise return None.
        """
        try:
            with closing(get(url, stream=True)) as resp:
                if self.is_good_response(resp):
                    return resp.content
                else:
                    return None

        except RequestException as e:
            self.log_error('Error during requests to {0} : {1}'.format(url, str(e)))
            return None

    def is_good_response(self, resp):
        """
        Returns True if the response seems to be HTML, False otherwise.
        """
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200 and content_type is not None
                and content_type.find('html') > -1)

    def log_error(self, e):
        """
        It is always a good idea to log errors.
        This function just prints them, but you can
        make it do anything.
        """
        print(e)

    # get list of movie full cast and crew list urls from movie list
    def get_cast_and_crew_urls(self, page):
        full_cc_urls = []

        while True:
            raw_html = scarper.simple_get(page)
            if raw_html is not None:
                break;
        html = BeautifulSoup(raw_html, 'html.parser')
        url_count = 0
        root_path = 'https://imdb.com/title/'
        tail_path = '/fullcredits/?ref_=tt_ov_st_sm'
        for h3 in html.select('h3'):
            for a in h3.select('a'):
                url_count += 1
                if url_count <= self.page_size:
                    path_elements = a['href'].split("/")
                    full_cc_urls.append(root_path + path_elements[2] + tail_path)
        return full_cc_urls

    def get_imdb_page(self, num):
        return 'https://www.imdb.com/list/ls057823854/?sort=list_order,asc&st_dt=&mode=detail&page=' + str(num)

    # creates Movie object with title and cast/crew list as objects using movie's full cast and crew page
    def scrape_movie(self, url):

        write = True

        if self.go:
            movie_start = getTime()
            exists = True

            print("\nraw", end="_")
            while True:
                raw_html = scarper.simple_get(url)
                if raw_html is not None:
                    break;
            print("html", end=" ")

            # probably completely unnecesary, if above loop works to ensure raw_html isn't None
            print("ht", end="")
            while True:
                html = BeautifulSoup(raw_html, 'html.parser')
                if html is not None:
                    break;
            print("ml", end=" | ")

            personnel_list = []
            role_list = []

            movie_title = html.find('div', class_='parent').h3.a.text

            year = html.find(class_="nobr").text
            if 'TV' in year or 'tv' in year:
                write = False

            try:
                spot = year.index('(')
                if year[spot + 1] == 'I':
                    spot2 = year.index(')')
                    Is = year[spot:spot2 + 1]
                    movie_title = movie_title + " " + Is

                    year = year[(spot + 1):]
                    try:
                        spot = year.index('(')
                    except:
                        exists = False
                        # movie hasn't been made, only announced
                year = year[(spot + 1):(spot + 5)]
            except:
                exists = False
            header_num = 0
            cast_table_checker = 0

            if exists:
                for header in html.find_all(class_="dataHeaderWithBorder"):
                    header_text = header.text[0:-1].rstrip()

                    if 'Cast' not in header_text or 'Casting' in header_text:  # skips cast, but picks up casting
                        if "Writing Credits" in header_text:
                            header_text = "Writing Credits"
                        if 'series' in header_text or 'Series' in header_text:
                            write = False
                        table = html.find_all(class_="simpleTable simpleCreditsTable")[header_num]
                        for a in table.find_all('a'):
                            name = a.text[1:-1]

                            indices = [p for p, x in enumerate(personnel_list) if x == name]
                            append = True
                            for k in indices:
                                if role_list[k] == header_text:
                                    append = False
                            if append:
                                personnel_list.append(name)  # add name to movie's personnel_list
                                role_list.append(header_text)  # add person's role to movie's role_list

                        header_num += 1

                    else:
                        with open("cast_headers.csv", "a", newline="") as f:
                            f.write(movie_title + ',' + header_text.rstrip())
                            f.write('\n')
                            scarper.page_num += 1

                    cast_table_checker += 1

                # gets specific number oc cast members, and adds to the personnel list
                for tr in html.find_all('tr'):
                    for td in tr.find_all('td', class_='primary_photo'):
                        name = td.a.img['title']
                        personnel_list.append(name)  # add to movie personnel list
                        role_list.append('Cast')  # add person's role to movie's role_list

                movie_title = movie_title.replace(",",
                                                  "{")  # all commas in title turned into { character to avoid messing up CSV. TODO: remember, when processing later

                if write:
                    with open("complete_movie_personnel_V2.csv", "a", newline="") as f:
                        f.write(movie_title + ',')
                        f.write(year + ',')
                        for name in personnel_list:
                            if 'ź' in name:
                                name = name[:8] + 'z' + name[10:]
                            f.write(name + ',')
                        f.write('\n')

                        f.write(movie_title + ',')
                        f.write(year + ',')
                        for role in role_list:
                            f.write(role + ',')
                        f.write('\n')

                    if 'Star Wars' in movie_title:
                        with open("Star_Wars_movie_personnel_V2.csv", "a", newline="") as f:
                            f.write(movie_title + ',')
                            f.write(year + ',')
                            for name in personnel_list:
                                if 'ź' in name:
                                    name = name[:8] + 'z' + name[10:]
                                f.write(name + ',')
                            f.write('\n')

                            f.write(movie_title + ',')
                            f.write(year + ',')
                            for role in role_list:
                                f.write(role + ',')
                            f.write('\n')

                    print(str(self.movie_index) + ": " + movie_title + "  " + str(year), end="")
                # Add to movie_list
            self.movie_index += 1

            if movie_title == "John Wick: Chapter 2":
                self.go = False
            self.curr_movie += 1
            if self.curr_movie == 101:
                self.curr_movie = 1
                with open("complete_movie_personnel_tally_V2.csv", "a",
                          newline="") as f:  # 'a' for append, 'w' to write over
                    f.write("completed page " + str(scarper.page_num) + ',')
                    scarper.page_num += 1


# Main

start = time.time()

scarper = IMDBScraper()

for i in range(scarper.start_page, scarper.start_page + scarper.num_pages):

    cast_and_crew_url_list = scarper.get_cast_and_crew_urls(scarper.get_imdb_page(i))

    # for the 100 movies on the current page
    for url in cast_and_crew_url_list:
        # get cast and crew, create movie object
        scarper.scrape_movie(url)
print('\n')

with open("complete_movie_personnel_tally.csv", "w", newline="") as f:
    f.write("done up through (including) page " + str(scarper.start_page + scarper.num_pages - 1))

end = time.time()
print("runtime: " + str(round(end - start)) + " seconds")