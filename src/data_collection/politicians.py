import codecs
import csv
import re

import requests
from bs4 import BeautifulSoup

from data_collection.comment_data import COMMENT_DATA_Y
from data_collection.extraction import get_comment_data, get_comment_data_list
from data_collection.utils import get_vk_api, get_config, get_bot_ids

POLITIC_GROUPS_URL = 'https://gosvon.net/?page=all'
POLITICIAN_DATA_PATH = '../../data/politicians.tsv'
VK_GROUP_REGEX = r'^https://vk.com/(\w+)'
GROUP_EXCEPTION = 'gosvon'
POLITICIANS_NUM = 'politicians_num'
MAX_COUNT = 100
MAX_OFFSET = 1000


def main():
    response = requests.get(POLITIC_GROUPS_URL)
    soup = BeautifulSoup(response.text, features='html.parser')
    vk_api = get_vk_api()

    bot_ids = get_bot_ids()
    with codecs.open(POLITICIAN_DATA_PATH, 'w+', encoding='utf8') as politician_data_file:
        tsv_writer = csv.writer(politician_data_file, delimiter='\t')
        tsv_writer.writerow(COMMENT_DATA_Y)

        limit = get_config()[POLITICIANS_NUM]
        if limit == 0:
            return
        cnt = 0

        for a in soup.findAll('a'):
            href = a['href']
            match = re.match(VK_GROUP_REGEX, href)
            if match:
                domain = match.group(1)
                if domain == GROUP_EXCEPTION:
                    continue

                group_object = vk_api.utils.resolveScreenName(screen_name=domain)
                if len(group_object) == 0:
                    continue

                group_id = group_object['object_id']
                for post_offset in range(0, MAX_OFFSET, MAX_COUNT):
                    post_items = \
                        vk_api.wall.get(owner_id=-group_id, offset=post_offset, count=MAX_COUNT, filter='owner')[
                            'items']
                    post_ids = map(lambda item: item['id'], post_items)

                    for post_id in post_ids:
                        for comment_offset in range(0, MAX_OFFSET, MAX_COUNT):
                            comment_items = \
                                vk_api.wall.getComments(owner_id=-group_id, post_id=post_id, offset=comment_offset,
                                                        count=MAX_COUNT)[
                                    'items']
                            politician_item_ids = filter(lambda item: item['from_id'] not in bot_ids, comment_items)
                            comment_ids = map(lambda item: item['id'], politician_item_ids)

                            for comment_id in comment_ids:
                                data_list = get_comment_data_list(-group_id, comment_id, False)
                                if data_list is None:
                                    continue

                                tsv_writer.writerow(data_list)
                                cnt += 1

                                if cnt == limit:
                                    # print("--- %s seconds ---" % (time.time() - start_time))
                                    return


if __name__ == '__main__':
    main()
