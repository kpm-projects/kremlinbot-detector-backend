from dataclasses import dataclass


@dataclass
class CommentData:
    text: str
    has_media: bool
    time_dif: int
    likes_cnt: int
    self_like: bool
    answers_cnt: int
    group_id: int
    reg_date_dif: int
    is_closed: bool
