"""
  MercuryTide Python Programming Assignment
  - - - - - - - - - - - - - - - - - - - - -

  The following script reads in a URL specified by the user and produces a report. The report
  contains the following information:

  * Title of the web page
  * List of meta tags present
  * Page file size, in KB
  * Total word count
  * Total number of unique words
  * List of the five most common words
  * List of meta tags not present in web page content
  * List of hyperlinks in page, including link text and link target URL/URI

"""


from bs4 import BeautifulSoup
import requests
import re


def get_meta(soup):

    """
    Find any meta tags on the page. Add all tags found to a list. Also compile a list
    of keywords found in keyword meta tags.

    :param soup: object
        BeautifulSoup object

    :return: tuple
        list of all meta tags and list of all keywords

    """

    all_tags = []
    keywords = []

    # Get META tags
    meta_tags = soup.find_all('meta')

    for meta_tag in meta_tags:
        all_tags.append(meta_tag)

        if meta_tag.get('name') == 'keywords':
            keywords += meta_tag.get('content', '').split(',')

    return all_tags, keywords


def filter_content(soup, content_filter):

    """
    Filter page content and return a list of words visible on the web page.

    NOTE: The assignment specifies 'content' but doesn't explicitly state if this refers to visible
    content or all source content. I have assumed visible content for this exercise. This can be altered
    by specifying an alternative filter callback.

    :param soup: object
        BeautifulSoup object

    :param content_filter: function
        filter callback

    :return: list
        List of words found in page
    """

    page_text = soup.findAll(text=True)

    visible_text = filter(content_filter, page_text)

    word_list = []

    for row in visible_text:
        if row.strip():
            words = row.strip().split(' ')

            word_list += [w.strip().replace(',', '').replace('.', '').lower() for w in words]

    return word_list


def is_visible(element):

    """
    Determine if the element should be visible on the web page.

    :param element: object
        BeautifulSoup page element

    :return: boolean
        True to allow element, else false
    """

    # Filter out unwanted elements
    ignore = ['head', 'title', 'style', 'script', '[document]', ]

    if element.parent.name in ignore:
        return False

    # Filter out comment blocks
    elif re.match('<!--.*-->', str(element)):
        return False

    return True


def word_tally(word_list):

    """
    Compiles a dictionary of words. Keys are the word, values are the number of occurrences
    of this word in the page.

    :param word_list: list
        List of words

    :return: dictionary
        Dict of words: total
    """

    word_dict = {}

    for word in word_list:
        if not word_dict.get(word):
            word_dict[word] = 1

        else:
            word_dict[word] += 1

    return word_dict


def run_report(response):

    """
    Process HTML data and print report to console.

    :param response: object
        requests response object
    """

    # Parse page data. I chose to use html5lib as it is what I had installed - change this to your
    # preferred parser as required.

    page_data = BeautifulSoup(response.text, 'html5lib')

    # Get page title and page content size. Content in header is specified in Octets, which are
    # normally equivalent to bytes. I have converted to KB for readability.

    title = page_data.title.string
    size = int(response.headers.get('Content-Length', 0)) / 1024

    print('\nPAGE TITLE: "{}"'.format(title))

    if size:
        print('PAGE SIZE: {0:.2f}K'.format(size))

    else:
        print('PAGE SIZE: not found!')

    # Get META tags, & META tag keywords:

    meta, keywords = get_meta(page_data)

    print('\nMETA TAGS FOUND:\n')

    for tag in meta:
        print(tag, '\n')

    # Get list of words from page content. I have chosen to use only visible content here.

    wordlist = filter_content(page_data, is_visible)

    print('\nPAGE CONTENT - WORD SUMMARY\n')

    # Generate report for word totals and most frequent words:

    word_dict = word_tally(wordlist)
    word_count_list = [{'word': word, 'count': count} for word, count in word_dict.items()]

    print('{} words found in page content'.format(len(wordlist)))
    print('{} unique words in page'.format(len(word_dict)))

    print('\nFive most common words:\n')

    for tally in sorted(word_count_list, key=lambda k: k['count'], reverse=True)[:5]:
        print(' "{}"'.format(tally['word']).ljust(8), '- occurs {} times'.format(tally['count']))

    # Keywords not in content. The keyword list we have from an earlier function, this is compared
    # against the word list:

    print('\nMETA keywords not in content:\n')

    # Words not in content
    for keyword in keywords:
        if keyword.lower().strip() not in wordlist:
            print(' - "{}"'.format(keyword.strip()))

    # Print a list of the links found in the page.

    print('\n')
    print('PAGE HYPERLINKS:\n')

    # Links
    for link in page_data.find_all('a'):
        print('"{}",  "{}"'.format(link.string, link.get('href')))

    return

# ------------------------------------------------------------------- #
#                                MAIN                                 #
# ------------------------------------------------------------------- #


def main():

    print('MercuryTide Web Page Analysis Assignment\n- - - - - - - - - - - - - - - - - - - -')

    url = input('Enter page URL: ')

    # Error handling for requests URL lookup. Return error if not 200 or if there is an exception
    # (e.g. ConnectionError)

    try:
        response = requests.get('http://' + url)

    except Exception as err:
        print('Error getting URL:\n<{0}> {1}'.format(type(err).__name__, err))
        return

    if response.status_code != 200:
        print('HTTP Error {0}:\n{1}'.format(response.status_code, response.text))
        return

    # Run report
    run_report(response)

    return


if __name__ == '__main__':
    main()
