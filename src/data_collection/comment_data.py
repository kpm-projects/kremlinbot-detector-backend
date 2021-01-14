from dataclasses import dataclass

COMMENT_DATA_Y = ['text', 'has_media', 'time_dif', 'likes_cnt', 'self_like', 'replies_cnt', 'reg_date_dif',
                  'is_closed', 'is_bot']


@dataclass
class CommentData:
    text: str
    has_media: bool
    time_dif: int
    likes_cnt: int
    self_like: bool
    answers_cnt: int
    reg_date_dif: int
    is_closed: bool
