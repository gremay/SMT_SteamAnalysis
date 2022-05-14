import time
import os
import atexit
import pandas as pd

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
PURPLE = '\033[35m'
TURQUOISE = '\033[36m'
END = '\033[0m'

AT_EXIT_BROWSER = {}
BROWSER_SLEEP = 5
SCROLL_PAUSE_TIME = 0.5


def install_proxy(PROXY_HOST = None, PROXY_PORT = None, TYPE = None):
    fp = webdriver.FirefoxProfile()
    if PROXY_HOST is not None:
        fp.set_preference("network.proxy.type", 1)
    else:
        print(PURPLE, 'Installer: Proxy was not set', END)

    """if TYPE & Type.SOCKS4 == Type.SOCKS4 or TYPE & Type.SOCKS5 == Type.SOCKS5:
        fp.set_preference("network.proxy.socks", PROXY_HOST)
        fp.set_preference("network.proxy.socks_port", int(PROXY_PORT))
        fp.set_preference("network.proxy.socks_version", 4 if TYPE == Type.SOCKS4 else 5)
    elif TYPE & Type.HTTPS == Type.HTTPS:
        fp.set_preference("network.proxy.https", PROXY_HOST)
        fp.set_preference("network.proxy.https_port", int(PROXY_PORT))
    elif TYPE & Type.HTTP == Type.HTTP:
        fp.set_preference("network.proxy.http", PROXY_HOST)
        fp.set_preference("network.proxy.http_port", int(PROXY_PORT))
    elif TYPE & Type.SSL == Type.SSL:
        fp.set_preference("network.proxy.ssl", PROXY_HOST)
        fp.set_preference("network.proxy.ssl_port", int(PROXY_PORT))
    elif TYPE & Type.FTP == Type.FTP:
        fp.set_preference("network.proxy.ftp", PROXY_HOST)
        fp.set_preference("network.proxy.ftp_port", int(PROXY_PORT))"""
    fp.set_preference("general.useragent.override",
                      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A")
    fp.update_preferences()
    options = Options()
    options.headless = True
    return webdriver.Firefox(firefox_profile=fp, executable_path='geckodriver.exe', options=options)


def scroll_to_end(driver, scroll_amount):
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    counter = 0
    for i in range(scroll_amount):
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            if counter == 5:
                break
            else:
                counter += 1
        elif new_height != last_height:
            counter = 0
        last_height = new_height


def fetch_from(url):
    browser = None
    df_reviews = pd.DataFrame()
    game_name = ''
    try:
        browser = install_proxy()
        AT_EXIT_BROWSER[url] = browser

        browser.get('https://steamcommunity.com/404')
        browser.add_cookie({'name': 'Steam_Language', 'value': 'english'})
        browser.get(url)

        time.sleep(BROWSER_SLEEP)
        try:
            cookie_button = browser.find_element_by_id('rejectAllButton')
            age_button = browser.find_element_by_id('age_gate_btn_continue')
            if age_button is not None:
                if cookie_button is not None:
                    cookie_button.click()
                age_button.click()
                time.sleep(BROWSER_SLEEP)
        except:
            time.sleep(1)

        scroll_to_end(browser, 25)
        game_name = browser.find_element_by_class_name('apphub_AppName').text
        print(GREEN, game_name, '| Fetched reviews:', len(browser.find_elements_by_class_name('apphub_UserReviewCardContent')), END)
        for webelement in browser.find_elements_by_class_name('apphub_Card'):
            # helpful count
            found_helpful = 0
            found_helpful_text = webelement.find_element_by_class_name('found_helpful').text
            if 'No one has rated this review as helpful yet' not in found_helpful_text:
                found_helpful = int(found_helpful_text[:found_helpful_text.index(' p')])
            rating = 0 if 'Not' in webelement.find_element_by_class_name('title').text else 1
            hours_played_text = webelement.find_element_by_class_name('hours').text
            hours_played = float(hours_played_text[:hours_played_text.index(' hrs')].replace(',', ''))
            review_text = webelement.find_element_by_class_name('apphub_CardTextContent').text
            # review_text = review_text_with_date[review_text_with_date.index('</div>')+6:]
            review_date = webelement.find_element_by_class_name('date_posted').text
            product_count_text = webelement.find_element_by_class_name('apphub_CardContentMoreLink').text
            product_count = 0
            if product_count_text is not None and len(product_count_text) > 0:
                product_count = int(product_count_text[:product_count_text.index(' product')].replace(',', ''))

            df_reviews = df_reviews.append({'game_name': game_name,
                                            'review_text': review_text,
                                            'hours_played': hours_played,
                                            'rating': rating,
                                            'found_helpful': found_helpful,
                                            'product_count': product_count,
                                            'review_date': review_date}, ignore_index=True)

        # review text, hours played, recommended/not, helpful count, product count
        # content = browser.page_source
    except Exception as e:
        print(RED, 'Error:', e.__traceback__, END)
    finally:
        if browser is not None:
            browser.stop_client()
            browser.quit()
        try:
            del AT_EXIT_BROWSER[url]
        except Exception as e:
            print(RED, 'Error:', e, END)

    return df_reviews, game_name


def on_exit():
    for browser in AT_EXIT_BROWSER:
        browser.stop_client()
        browser.quit()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(TURQUOISE, 'Load reviews...', END)
    file_path = 'reviews.csv'
    if os.path.isfile(file_path):
        df_reviews_all = pd.read_csv(file_path, sep=';')
    else:
        df_reviews_all = pd.DataFrame(columns=['game_name', 'review_text', 'hours_played', 'rating', 'found_helpful',
                                          'product_count', 'review_date'])

    print(TURQUOISE, 'Starting crawler...', END)
    atexit.register(on_exit)

    urls = ['https://steamcommunity.com/app/1201830/reviews/?browsefilter=toprated&snr=1_5_100010_',
            'https://steamcommunity.com/app/1245620/reviews/?filterLanguage=english',
            'https://steamcommunity.com/app/1237970/reviews/',
            'https://steamcommunity.com/app/1174180/reviews/',
            'https://steamcommunity.com/app/848450/reviews/',
            'https://steamcommunity.com/app/1341290/reviews/',
            'https://steamcommunity.com/app/867210/reviews/',
            'https://steamcommunity.com/app/1468720/reviews/',
            'https://steamcommunity.com/app/252490/reviews/',
            'https://steamcommunity.com/app/730/reviews/']
    for url in urls:
        df_reviews_new, game_name = fetch_from(url)
        print(TURQUOISE, 'Update reviews:', game_name, END)
        df_reviews_all = df_reviews_all.append(df_reviews_new)
        time.sleep(60)

    df_reviews_all.to_csv(file_path, sep=';', index=False)

