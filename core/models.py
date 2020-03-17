from django.db import models
from django.core.exceptions import ValidationError
from authorization.models import User, IdentityVerification
from file_management.models import Image


class FriendRequest(models.Model):
    requestee = models.ForeignKey(
        IdentityVerification, on_delete=models.CASCADE, related_name='received_request')
    requestor = models.ForeignKey(
        IdentityVerification, on_delete=models.CASCADE, related_name='sent_request')
    requested_on = models.DateTimeField(auto_now_add=True)
    approved_on = models.DateTimeField(blank=True, null=True)
    declined_on = models.DateTimeField(blank=True, null=True)
    canceled_on = models.DateTimeField(blank=True, null=True)
    deleted_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('requestee', 'requestor')

    def __str__(self):
        requestee_disp = ''
        requestor_disp = ''
        requestee = self.requestee
        requestor = self.requestor
        if hasattr(requestee, 'user') and requestee.user is not None:
            requestee_disp = requestee_disp + \
                (requestee.user.nickname if requestee.user.nickname is not None else '')
        if hasattr(requestor, 'user') and requestor.user is not None:
            requestor_disp = requestor_disp + \
                (requestor.user.nickname if requestor.user.nickname is not None else '')

        requestee_disp = requestee_disp + ' ' + requestee.phoneno
        requestor_disp = requestor_disp + ' ' + requestor.phoneno

        return requestor_disp + ' -> ' + requestee_disp + ('(Approved)' if self.approved_on == True else '')


class Shield(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shield')
    phoneno = models.CharField(max_length=255, blank=True, null=True)
    belong = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Report(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='report')
    who = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reported')
    why = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class MatchRequest(models.Model):
    STATUS_CODE_MATCHING = 1
    STATUS_CODE_MATCHED = 2
    STATUS_CODE_CANCELED = 3
    STATUS_CODE_MATCHING_YAMI = 4

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='match_request')
    personnel_selected = models.SmallIntegerField(default=0)
    date_selected = models.SmallIntegerField(default=0)
    min_age = models.SmallIntegerField(default=20)
    max_age = models.SmallIntegerField(default=30)
    requested_on = models.DateTimeField(auto_now_add=True, blank=True)
    matched_with = models.OneToOneField(
        "self", on_delete=models.SET_NULL, related_name="+", null=True, blank=True)
    matched_on = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(default=0)

    def __str__(self):
        return '{} - {} - {}'.format(self.user.nickname, self.requested_on.strftime('%Y/%m/%d %H:%M'), self.status)


class Feed(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='feed')
    before = models.ForeignKey(
        "self", on_delete=models.SET_NULL, related_name='next', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{} {} - {}'.format(self.id, self.user.nickname, self.created_at.strftime('%Y/%m/%d %H:%M'))


class Like(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='like')
    feed = models.ForeignKey(
        Feed, on_delete=models.CASCADE, related_name='like')
    value = models.BooleanField(default=True)
    is_unread = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        feeds = self.feed.user.feed.all()
        index = 0
        for feed in feeds:
            index = index + 1
            if self.feed == feed:
                break
        index_str = ''
        if(index == 1):
            index_str = 'st'
        elif(index == 2):
            index_str = 'nd'
        elif(index == 3):
            index_str = 'rd'
        else:
            index_str = 'th'
        return '{} likes {}\'s {}{} feed'.format(self.user.nickname, self.feed.user.nickname, index, index_str)


class FeedImage(models.Model):
    feed = models.OneToOneField(
        Feed, on_delete=models.CASCADE, related_name='image')
    data = models.OneToOneField(
        Image, on_delete=models.CASCADE, null=True)


class FeedText(models.Model):
    feed = models.OneToOneField(
        Feed, on_delete=models.CASCADE, related_name='text')
    value = models.CharField(max_length=255)


class FeedRead(models.Model):
    feed = models.ForeignKey(
        Feed, on_delete=models.CASCADE, related_name='read')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='read')
    read_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('feed', 'user')

    def __str__(self):
        return '{} read {}\'s feed'.format(self.user.nickname, self.feed.user.nickname)


class Chat(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chat_sent', null=True)
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chat_recv', null=True)
    greet = models.CharField(max_length=128, default="안녕하세요")
    chat_type = models.SmallIntegerField(default=0)
    approved_on = models.DateTimeField(null=True, blank=True)
    declined_on = models.DateTimeField(null=True, blank=True)
    canceled_on = models.DateTimeField(null=True, blank=True)
    canceled_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chat_canceled', null=True, blank=True)
    cancel_check = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super(Chat, self).clean()
        direct = Chat.objects.filter(
            sender=self.sender, receiver=self.receiver)
        reverse = Chat.objects.filter(
            sender=self.receiver, receiver=self.sender)
        if direct.exists() or reverse.exists():
            if(direct.last().id == self.id):
                return
            if(reverse.last().id == self.id):
                return
            raise ValidationError('Aleady Exists')

    def save(self, *args, **kwargs):
        if not self.pk:
            self.full_clean()
        return super(Chat, self).save(*args, **kwargs)


class Notification(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='notification')
    like = models.BooleanField(default=True)
    like_match = models.BooleanField(default=True)
    request = models.BooleanField(default=True)
    match = models.BooleanField(default=True)
    chat = models.BooleanField(default=True)
