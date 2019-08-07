import datetime
import re

from django.utils.html import strip_tags

def count_words(html_string):
    message = strip_tags(html_string)
    count = len(re.findall(r'\w+',message))
    return count

def get_read_time(post_content):
    word_count = count_words(post_content)
    read_time_min = word_count/200.0
    read_time_sec = read_time_min * 60
    read_time = str(datetime.timedelta(seconds=read_time_sec))
    return read_time