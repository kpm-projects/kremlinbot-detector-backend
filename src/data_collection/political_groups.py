import re

import requests
from bs4 import BeautifulSoup

from src.data_collection.utils import get_vk_api

POLITIC_GROUPS_URL = 'https://gosvon.net/?page=all'
POLITIC_GROUP_IDS_PATH = 'data/political_group_ids.txt'
VK_GROUP_REGEX = r'^https://vk.com/(\w+)'


def main():
    response = requests.get(POLITIC_GROUPS_URL)
    soup = BeautifulSoup(response.text)

    with open(POLITIC_GROUP_IDS_PATH, 'w') as political_group_ids_file:
        for a in soup.findAll('a'):
            href = a['href']
            match = re.match(VK_GROUP_REGEX, href)
            if match:
                screen_name = match.group(1)
                vk_api = get_vk_api()

                group_id = vk_api.utils.resolveScreenName(screen_name=screen_name)
                political_group_ids_file.write('{}\n'.format(group_id))


if __name__ == '__main__':
    main()
