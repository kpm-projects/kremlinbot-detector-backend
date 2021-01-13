import csv
import time

import requests
from bs4 import BeautifulSoup

from src.data_collection.commons import HTML_A
from src.data_collection.extraction import get_comment_data

LIMIT = 10
FIRST_ROW = ['text', 'has_media', 'time_dif', 'likes_cnt', 'self_like', 'replies_cnt', 'group_id', 'reg_date_dif',
             'is_closed', 'is_bot']
BOT_IDS_PATH = 'resources/bot_ids.txt'
BOT_DATA_PATH = 'data/bots.tsv'
MAX_PAGES_NUM = 100
GET_BOT_URL_FORM = 'https://gosvon.net/?usr={}&p={}'
GROUP_LINK_NAME = 'Ссылка'


def main():
    with open(BOT_IDS_PATH, 'r') as bot_ids_file:
        lines = bot_ids_file.readlines()
        bot_ids = list(map(int, lines))

    with open(BOT_DATA_PATH, 'w') as bot_data_file:
        tsv_writer = csv.writer(bot_data_file, delimiter='\t')
        tsv_writer.writerow(FIRST_ROW)

        cnt = 0
        # start_time = time.time()

        for bot_id in bot_ids:
            prev_response = None
            for page_num in range(1, MAX_PAGES_NUM):
                response = requests.get(GET_BOT_URL_FORM.format(bot_id, page_num))
                if prev_response is not None and response.text == prev_response.text:
                    break

                soup = BeautifulSoup(response.text)
                for a in soup.findAll('a'):
                    content = a.contents
                    if GROUP_LINK_NAME in content:
                        link = a['href']
                        comment_data = get_comment_data(link)

                        data_list = [
                            comment_data.text,
                            comment_data.has_media,
                            comment_data.time_dif,
                            comment_data.likes_cnt,
                            comment_data.self_like,
                            comment_data.answers_cnt,
                            comment_data.group_id,
                            comment_data.reg_date_dif,
                            comment_data.is_closed,
                            True
                        ]
                        tsv_writer.writerow(data_list)
                        cnt += 1

                        if cnt == LIMIT:
                            # print("--- %s seconds ---" % (time.time() - start_time))
                            return

                prev_response = response


if __name__ == '__main__':
    main()
