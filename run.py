from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import *
from lxml import html
from KnessetVote import KnessetVote
from datetime import date
import time
import DBManager

KNESSET_VOTE_SEARCH_PAGE = "https://www.knesset.gov.il/vote/heb/vote_search.asp"
FAIL_URLS = []
MAIN_DRIVER = None
MKS20 = DBManager.create_mk_party_dict()

def main_driver():
    if not MAIN_DRIVER:
        MAIN_DRIVER = webdriver.Chrome()
    return MAIN_DRIVER

def get_html_by_url(web_url=""):
    """
    return html page from url
    :param web_url: the url to return from
    :type web_url: str
    :return: string of html page
    :rtype: str (HTML)
    """
    # TODO: validate exceptions of INTENRT connection....
    if web_url != "":
        main_driver().get(web_url)
    return html.fromstring(main_driver().page_source)

def vote_parse(vote_str):
    """
    return string of parse vote from real string in web
    :param vote_str: the string in the web
    :type vote_str: str
    :return: string of the vote
    :rtype: str
    """
    if vote_str == "רשימת ח\"כ שהצביעו בעד":
        return "בעד"
    elif vote_str == "רשימת ח\"כ שהצביעו נגד":
        return "נגד"
    elif vote_str == "רשימת ח\"כ שלא הצביע":
        return "לא הצביע"
    elif vote_str == "רשימת ח\"כ שנמנעו":
        return "נמנע"
    return vote_str

def parse_page(url_and_date):
    """
    parse a page and return list of KnessetVote objects
    :param url_and_date: tuple of (url, date)
    :type vote_str: tuple
    :return: list of KnessetVote objects from the page
    :rtype: list
    """
    vote_date = url_and_date[1]
    web_url = url_and_date[0]
    
    body = get_html_by_url(web_url)
    # parse headers of the vote:
    headers_elements = body.xpath("//td[@class='DataText6']")
    if len(headers_elements) < 5:
        print("ERROR in: parameter not enough in headers of the page. noly {0} params got, and 5 is expected\nURL:{1}".format(len(headers_elements), web_url))
        return
    try: 
        meeting_num = headers_elements[0].text
        vote_num = headers_elements[1].text
        # vote_date = headers_elements[2].text
        rule_name = headers_elements[3].text
        yor_name = headers_elements[4].text
    except Exception as err:
        print("ERROR details: {0}".format(err))
        return
    # this if, fix the bug from the Knesset Website that make new line there...
    splited_name = str(rule_name).splitlines()
    rule_name = "".join(splited_name)

    # parse the votes:
    mks_elements = body.xpath("//a[@class='DataText4'] | //p[@class='DataText4']")
    k_votes = []
    for mk_elem in mks_elements:
        vote_str = mk_elem.getparent().getparent().getparent().getparent().getparent().getparent().getparent()[0][1].text
        vote_to = vote_parse(vote_str)

        mk_name = mk_elem.text
        mk_name = str(mk_name).replace(u'\xa0', u' ')
        party = "none"
        #if mk_name in MKS20:
        if mk_name in MKS20:
            party = MKS20[mk_name]
        # creating new vote object
        new_vote = KnessetVote(web_url, vote_date, meeting_num, vote_num, rule_name, yor_name, mk_name, party, vote_to)
        k_votes.append(new_vote)
    return k_votes

def find_vote_pages_urls(start_date, end_date):
    """
    search for vote pages url between the dates start_date and end_date
    :param start_date: the first date
    :type: start_date: date
    :param end_date: the last date
    :type: end_date: date
    :return: list of urls
    :rtype: list (of tuple (url, date))
    """
    # TODO: what if I have exceptions...
    main_driver().get(KNESSET_VOTE_SEARCH_PAGE)
    # get the select elements:
    from_year_elem = Select(main_driver().find_element_by_name("dtFmYY"))
    from_month_elem = Select(main_driver().find_element_by_name("dtFmMM"))
    from_day_elem = Select(main_driver().find_element_by_name("dtFmDD"))
    to_year_elem = Select(main_driver().find_element_by_name("dtToYY"))
    to_month_elem = Select(main_driver().find_element_by_name("dtToMM"))
    to_day_elem = Select(main_driver().find_element_by_name("dtToDD"))
    # set values:
    from_year_elem.select_by_value(str(start_date.year))
    from_month_elem.select_by_value(str(start_date.month))
    from_day_elem.select_by_value(str(start_date.day))
    to_year_elem.select_by_value(str(end_date.year))
    to_month_elem.select_by_value(str(end_date.month))
    to_day_elem.select_by_value(str(end_date.day))
    #enter search:
    main_driver().find_element_by_id("Image3").click() #send_keys(Keys.ENTER)
    
    urls_list = []
    while True:
        body = get_html_by_url()
        #DUBUG:
        # page_problem = body.find_element_by_name("center")
        if str(main_driver().page_source).find("תקלה בהעברת המשתנים.") != -1:
            raise Exception("תקלה בהעברת המשתנים...")

        urls_elements = body.xpath("//a[@class='DataText6']")
        for url_elem in urls_elements:
            url = "https://www.knesset.gov.il/vote/heb/"+url_elem.get("href")
            date = str(url_elem.getparent().getparent().text_content().splitlines()[5]).strip()

            urls_list.append((url, date))
        
        try:
            main_driver().find_element_by_id("Image2").click()
        except:
            print("Finish the urls...")
            print("Total {0} pages found.".format(len(urls_list)))
            break
    
    return urls_list
    
def get_party_by_mk(mk_name):
    """
    return the party of mk_name
    :param mk_name: name of the mk
    :type mk_name: str
    :return: name of the party
    :rtype: str
    """
    return MKS20[mk_name]

def parse_all_between(start_date, end_date):
    """
    The main function to insert all the urls for the selected dates.
    :param start_date: the first date
    :type: start_date: date
    :param end_date: the last date
    :type: end_date: date
    :return: true if all success, else return false
    :rtype: bool
    """
    urls = []
    while True:
        try:
            print("Start finding pages between: {0} AND {1}".format(start_date, end_date))
            urls = find_vote_pages_urls(start_date, end_date)
            break
        except Exception as err:
            print("ERROR!!! Detials:\n{0}".format(err))
            if type(err) is NoSuchWindowException:
                return False
            urls.clear()
    success = 0
    for url in urls:
        new_data = parse_page(url)
        ok = DBManager.insert_list_of_knesset_votes(new_data)
        if ok != 1:
            print("Something not good in inserting the data...\n URL: {0}".format(url))
            FAIL_URLS.append(url)
        else:
            success += 1
    print("Total {0}/{1} pages inserted!".format(success, len(urls)))
    return success == len(urls)

def start(from_date, to_date):
    start_time = time.time()
    ok = parse_all_between(from_date, to_date)
    if ok:
        print("Done without fails!")
    else:
        print("Some fails was ocuur in this urls:")
        print(FAIL_URLS)
    end_time = time.time()
    print("TOTAL TIME: {0}".format(end_time - start_time))

if __name__ == "__main__":
    from_date = date(2018, 12, 1)
    to_date = date(2019, 1, 4)
    try:
        start(from_date, to_date)
    except:
        pass
    finally:
        # Always close when done
        main_driver().close()