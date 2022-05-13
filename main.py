import time
import atexit

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


def scroll_to_end(driver):
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def fetch_from(url):
    browser = None
    try:
        browser = install_proxy()
        AT_EXIT_BROWSER[url] = browser

        browser.get(url)
        time.sleep(BROWSER_SLEEP)
        scroll_to_end(browser)

        print(GREEN, 'fetched reviews:', len(browser.find_elements_by_class_name('apphub_UserReviewCardContent')), END)
        # content = browser.page_source
    except Exception as e:
        print(RED, 'Error:', e, END)
    finally:
        if browser is not None:
            browser.stop_client()
            browser.quit()
        try:
            del AT_EXIT_BROWSER[url]
        except Exception as e:
            print(RED, 'Error:', e, END)


def on_exit():
    for browser in AT_EXIT_BROWSER:
        browser.stop_client()
        browser.quit()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(TURQUOISE, 'Starting crawler...', END)
    atexit.register(on_exit)
    fetch_from('https://steamcommunity.com/app/1201830/reviews/?browsefilter=toprated&snr=1_5_100010_')

