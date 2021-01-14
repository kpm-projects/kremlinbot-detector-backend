import codecs
import csv

import requests
from bs4 import BeautifulSoup

from data_collection.comment_data import COMMENT_DATA_Y
from data_collection.extraction import get_comment_data_list_by_link
from data_collection.utils import get_config, get_bot_ids

BOTS_NUM = 'bots_num'
BOT_DATA_PATH = '../../data/bots.tsv'
MAX_PAGES_NUM = 100
GET_BOT_URL_FORM = 'https://gosvon.net/?usr={}&p={}'
GROUP_LINK_NAME = 'Ссылка'
BANNED = 'Страница забанена'


def main():
    bot_ids = get_bot_ids()
    with codecs.open(BOT_DATA_PATH, 'w+', encoding='utf8') as bot_data_file:
        tsv_writer = csv.writer(bot_data_file, delimiter='\t')
        tsv_writer.writerow(COMMENT_DATA_Y)

        limit = get_config()[BOTS_NUM]
        if limit == 0:
            return
        cnt = 0
        # start_time = time.time()

        for bot_id in bot_ids:
            prev_response = None
            for page_num in range(1, MAX_PAGES_NUM):
                response = requests.get(GET_BOT_URL_FORM.format(bot_id, page_num))
                if BANNED in response.text:
                    break
                if prev_response is not None and response.text == prev_response.text:
                    break

                soup = BeautifulSoup(response.text, features='html.parser')
                for a in soup.findAll('a'):
                    content = a.contents
                    if GROUP_LINK_NAME in content:
                        link = a['href']
                        data_list = get_comment_data_list_by_link(link, True)
                        if data_list is None:
                            continue

                        tsv_writer.writerow(data_list)
                        cnt += 1

                        if cnt == limit:
                            # print("--- %s seconds ---" % (time.time() - start_time))
                            return

                prev_response = response


if __name__ == '__main__':
    main()
