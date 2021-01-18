import pickle
import re

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from data_collection.comment_data import COMMENT_DATA_X
from data_collection.extraction import COMMENT_REGEX, get_comment_data_list_by_link_x, get_comment_data_list_x
from data_collection.utils import get_config, get_vk_api
import pandas as pd

from ml_part.results import get_answer

MODEL_PATH = '../ml_part/mystem_nltk-stopwords_badwords_RandomForestClassifier_model.pkl'


def main():
    token = get_config()['vk_public_token']
    vk_session = vk_api.VkApi(token=token)
    long_poll = VkLongPoll(vk_session)
    vk = vk_session.get_api()
    vk_user_api = get_vk_api()
    with open(MODEL_PATH, 'rb') as file:
        model, mapper, min_max_scaler = pickle.load(file)

    for event in long_poll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            text = event.text
            x = [-1]
            if re.match(COMMENT_REGEX, text):
                x = get_comment_data_list_by_link_x(vk_user_api, text)
            elif event.attachments is not None and event.attachments.get('attach1'):
                match = re.match(r'(-?\d+)_(\d+)', event.attachments['attach1'])
                group_id = int(match.group(1))
                comment_id = int(match.group(2))
                x = get_comment_data_list_x(vk_user_api, group_id, comment_id)

            if x == [-1]:
                answer_text = 'Please, send comment link'
            elif x is None:
                answer_text = 'Invalid comment'
            else:
                x_df = pd.DataFrame([x], columns=COMMENT_DATA_X)
                predict = get_answer(model, mapper, min_max_scaler, x_df)
                if predict:
                    answer_text = 'IT\'S A BOT!!!'
                else:
                    answer_text = 'It isn\'t a bot'

            vk.messages.send(
                user_id=event.user_id,
                message=answer_text,
                random_id=get_random_id()
            )


if __name__ == '__main__':
    main()
