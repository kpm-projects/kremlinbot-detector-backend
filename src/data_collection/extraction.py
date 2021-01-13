import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from src.data_collection.comment_data import CommentData
from utils import get_vk_api
from pyOptional import Optional
import re

COMMENT_REGEX = r'^https://vk.com/wall-(\d+)_\d+\?reply=(\d+)'
REGISTRATION_URL_FORM = 'https://vk.com/foaf.php?id={}'


def get_comment_data(comment_link):
    match = re.match(COMMENT_REGEX, comment_link)
    group_id = int(match.group(1))
    comment_id = int(match.group(2))

    vk_api = get_vk_api()
    comment = vk_api.wall.getComment(owner_id=-group_id, comment_id=comment_id, extended=1)

    item = comment['items'][0]
    profile = comment['profiles'][0]

    posts = '{}_{}'.format(item['owner_id'], item['post_id'])
    post = vk_api.wall.getById(posts=posts)[0]

    like_ids = vk_api.likes.getList(type='comment', owner_id=-group_id, item_id=comment_id)['items']

    response = requests.get(REGISTRATION_URL_FORM.format(profile['id']))
    soup = BeautifulSoup(response.text)
    reg_date_iso = soup.findAll('ya:created')[0]['dc:date']
    reg_date = datetime.fromisoformat(reg_date_iso)
    reg_date_unix = int(time.mktime(reg_date.timetuple()))

    return CommentData(
        text=item['text'],
        has_media='attachments' in item,
        time_dif=item['date'] - post['date'],
        likes_cnt=item['likes']['count'],
        self_like=profile['id'] in like_ids,
        answers_cnt=Optional(item.get('thread')).map(lambda d: d['count']).get_or_else(0),
        group_id=group_id,
        reg_date_dif=item['date'] - reg_date_unix,
        is_closed=profile['is_closed']
    )
