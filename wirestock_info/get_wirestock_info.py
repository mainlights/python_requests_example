import os
from collections import Counter
from dotenv import load_dotenv

import requests
import csv


load_dotenv()
user_credentials = {
        "username": os.getenv('USERNAME'),
        "password": os.getenv('PASSWORD'),
    }

data_types = [
    'Platform', 'Type of media', 'All media', 'Accepted media', 'On review media', 'To revise', 'Rejected',
    'Approval rate', 'Amount', 'Downloads',
]


def login():
    url = 'https://api-kube.wirestock.io/api/auth/login'
    token = requests.post(url, json=user_credentials, headers={
        'accept': 'application/json, text/plain, */*',
    }).json()
    return token['data']['access_token']


def get_video_info(token):
    page_number = 1
    videos_list = []
    while True:
        url = f'https://api-kube.wirestock.io/api/search/portfolio/maria.chistyakova?page=' \
              f'{page_number}&types[]=video'
        media_list = requests.get(url, headers={'authorization': f'Bearer {token}'}).json()['data']
        if len(media_list) != 0:
            [videos_list.append(i) for i in media_list]
            page_number += 1
        else:
            break

    videos_status = Counter([media['status'] for media in videos_list])
    accepted_videos_count = videos_status.get('accepted')
    on_review_videos_count = videos_status.get('submitted')
    if not on_review_videos_count:
        on_review_videos_count = 0
    total_video_count = len(videos_list)

    uploaded_videos = {
        'All media': total_video_count,
        'Type of media': 'Video',
        'Accepted media': accepted_videos_count,
        'On review media': on_review_videos_count,
        'To revise': total_video_count-accepted_videos_count-on_review_videos_count
    }
    return uploaded_videos


def get_photo_info(token):
    page_number = 1
    photos_list = []
    while True:
        url = f'https://api-kube.wirestock.io/api/search/portfolio/maria.chistyakova?page={page_number}&types[]=' \
              'photo'
        media_list = requests.get(url, headers={'authorization': f'Bearer {token}'}).json()['data']
        if len(media_list) != 0:
            [photos_list.append(i) for i in media_list if i['type'] == 'photo']
            page_number += 1
        else:
            break

    photos_status = Counter([media['status'] for media in photos_list])
    accepted_photos_count = photos_status.get('accepted', 0)
    on_review_photos_count = photos_status.get('submitted', 0)

    uploaded_photos = {
        'All media': len(photos_list),
        'Type of media': 'Photo',
        'Accepted media': accepted_photos_count,
        'On review media': on_review_photos_count,
        'To revise': str(len(photos_list) - accepted_photos_count - on_review_photos_count)
    }
    return uploaded_photos


def get_sales_summary(token):
    url = 'https://api-kube.wirestock.io/api/users/195734/earnings/summary'
    response_sales_summary = requests.get(url, headers={'authorization': f'Bearer {token}'}).json()
    sales_summary = {
        'Amount': response_sales_summary['data']['amount'],
        'Downloads': response_sales_summary['data']['downloads']
    }
    return sales_summary


def get_items_status(token):
    url = 'https://api-kube.wirestock.io/api/users/by-username/maria.chistyakova'
    response_items_status = requests.get(url, headers={'authorization': f'Bearer {token}'}).json()
    items_status = {
        'Rejected': response_items_status['data']['rejected_media_count'],
        'Approval rate': f"{response_items_status['data']['approval_rate']}%"
    }
    return items_status


def get_all_info(token):
    photo_info = {
        'Platform': 'Wirestock',
        'Type of media': None
    }
    video_info = {
        'Platform': 'Wirestock',
        'Type of media': None
    }
    photo_info.update(get_photo_info(token))
    video_info.update(get_video_info(token))
    video_info.update(get_items_status(token))
    video_info.update(get_sales_summary(token))
    return photo_info, video_info


def save_csv_file(token):
    info = get_all_info(token)
    with open("wirestock_data.csv", 'w') as f:
        writer = csv.DictWriter(f, fieldnames=data_types)
        writer.writerow(info[0])
        writer.writerow(info[1])


save_csv_file(login())
