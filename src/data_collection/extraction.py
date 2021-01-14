import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from data_collection.comment_data import CommentData
from data_collection.utils import get_vk_api
from pyOptional import Optional
import re

COMMENT_REGEX = r'^https://vk.com/wall(-?\d+)_\d+\?reply=(\d+)'
REGISTRATION_URL_FORM = 'https://vk.com/foaf.php?id={}'
EMPTY_COMMENT_FLAG = 'а'

def get_comment_data_list_by_link(comment_link, is_bot):
    comment_data = get_comment_data_by_link(comment_link)
    if comment_data is None:
        return None
    return construct_comment_data_list(comment_data, is_bot)


def get_comment_data_list(owner_id, comment_id, is_bot):
    comment_data = get_comment_data(owner_id, comment_id)
    if comment_data is None:
        return None
    return construct_comment_data_list(comment_data, is_bot)


def construct_comment_data_list(comment_data, is_bot):
    return [
        comment_data.text,
        comment_data.has_media,
        comment_data.time_dif,
        comment_data.likes_cnt,
        comment_data.self_like,
        comment_data.answers_cnt,
        comment_data.reg_date_dif,
        comment_data.is_closed,
        is_bot
    ]


def get_comment_data_by_link(comment_link):
    match = re.match(COMMENT_REGEX, comment_link)
    # if match is None:
    #     return None
    group_id = int(match.group(1))
    comment_id = int(match.group(2))
    return get_comment_data(group_id, comment_id)


def get_comment_data(owner_id, comment_id):
    vk_api = get_vk_api()
    comment = vk_api.wall.getComment(owner_id=owner_id, comment_id=comment_id, extended=1)

    item = comment['items'][0]
    profile = comment['profiles'][0]

    text = item['text'].replace('\n', ' ')
    if len(text) == 0:
        text = EMPTY_COMMENT_FLAG

    posts = '{}_{}'.format(item['owner_id'], item['post_id'])
    post = vk_api.wall.getById(posts=posts)[0]

    like_ids = vk_api.likes.getList(type='comment', owner_id=owner_id, item_id=comment_id)['items']

    response = requests.get(REGISTRATION_URL_FORM.format(profile['id']))
    soup = BeautifulSoup(response.text, 'lxml')
    created = soup.findAll('ya:created')
    if len(created) == 0:
        return None
    reg_date_iso = created[0]['dc:date']
    reg_date = datetime.fromisoformat(reg_date_iso)
    reg_date_unix = int(time.mktime(reg_date.timetuple()))

    return CommentData(
        text=text,
        has_media='attachments' in item,
        time_dif=item['date'] - post['date'],
        likes_cnt=item['likes']['count'],
        self_like=profile['id'] in like_ids,
        answers_cnt=Optional(item.get('thread')).map(lambda d: d['count']).get_or_else(0),
        reg_date_dif=item['date'] - reg_date_unix,
        is_closed=profile['is_closed']
    )
