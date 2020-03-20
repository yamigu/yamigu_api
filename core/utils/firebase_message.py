from fcm_django.models import FCMDevice
from firebase_admin import db
from datetime import datetime
from authorization.models import User
import threading
from django.conf import settings


def send_push_thread(user_id, data, is_chat=False):
    devices = FCMDevice.objects.filter(user=user_id)
    user = User.objects.get(id=user_id)
    print(user.nickname)
    for device in devices:
        device.send_message(
            data=data, title=data['title'], body=data['content'])
    # ref = db.reference('user/{}/notifications'.format(user.uid))
    # badge = 0
    # ref_dict = ref.get().values()
    # for noti in ref_dict:
    #     try:
    #         if noti['isUnread']:
    #             badge = badge + 1
    #     except TypeError:
    #         pass
    # if is_chat:
    #     badge = badge + 1
    # for device in devices:
    #     if(not device.active):
    #         continue
    #     if(device.type == 'android'):
    #         data['badge'] = badge
    #         device.send_message(data=data)
    #     else:
    #         device.send_message(
    #             data=data, title=data['title'], body=data['content'], badge=badge)


def send_message_thread(user_list, room_id, content):
    ref = db.reference('message/{}'.format(room_id))
    key = ref.push().key
    ref.child(key).set({
        'key': key,
        'idSender': settings.MANAGER_UID,
        'message': content,
        'time': int(((datetime.now() - datetime(1970, 1, 1)).total_seconds() - 3600 * 9) * 1000)
    })
    for user in user_list:
        ref2 = db.reference('user/{}/chat/{}'.format(user.uid, room_id))
        ref2.set({
            'is_unread': True,
        })


def send_push(user_id, data, is_chat=False):
    t = threading.Thread(target=send_push_thread,
                         args=(user_id, data, is_chat))
    t.start()


def send_message(user_id, room_id, content):
    t = threading.Thread(target=send_message_thread,
                         args=(user_id, room_id, content))
    t.start()
