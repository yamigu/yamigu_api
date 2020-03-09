from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from .models import *
from core.models import *
from file_management.serializers import *
from django.urls import reverse

admin.site.register(Location)
admin.site.register(ProfileImage)
admin.site.register(IdentityVerification)
admin.site.register(BelongVerification)
admin.site.register(FirebaseToken)


class IVInline(admin.TabularInline):
    model = IdentityVerification


class BVEditLinkToInlineObject(object):
    def edit_link(self, instance):
        print(instance._meta.model_name)
        url = reverse('admin:authorization_bvimage_change',
                      args=[instance.image.last().pk])
        if instance.pk:
            return mark_safe(u'<a href="{u}">edit</a>'.format(u=url))
        else:
            return ''


class BVInline(BVEditLinkToInlineObject, admin.TabularInline):
    model = BelongVerification
    readonly_fields = ('bv_image', 'edit_link')

    def bv_image(self, obj):

        url = ImageSerializer(obj.image.last().data).data
        return mark_safe('<img src="{url}" width="320px" />'.format(url=url['src']))


class BVImageAdmin(admin.ModelAdmin):
    model = BVImage
    readonly_fields = ('belong', 'department', 'bv_image')
    exclude = ('data',)

    def belong(self, obj):
        return obj.bv.belong

    def department(self, obj):
        return obj.bv.department

    def bv_image(self, obj):
        url = ImageSerializer(obj.data).data
        return mark_safe('<img src="{url}" width="320px" />'.format(url=url['src']))


class ProfileImageInline(admin.TabularInline):
    model = ProfileImage
    ordering = ('number',)
    exclude = ('data', 'number')
    readonly_fields = ('profile_image',)
    max_num = 1

    def profile_image(self, obj):
        url = ImageSerializer(obj.data).data
        return mark_safe('<img src="{url}" width="320px" />'.format(url=url['src']))


class RecvChatInline(admin.TabularInline):
    model = Chat
    fk_name = "sender"
    max_num = 0


class SentChatInline(admin.TabularInline):
    model = Chat
    fk_name = "receiver"
    max_num = 0


class UserAdmin(admin.ModelAdmin):
    search_fields = ('nickname', 'uid', 'real_name')
    readonly_fields = ('verified',)
    list_display = ('uid', 'nickname', 'personal_info', 'belong',
                    'verified', 'num_of_yami', 'num_of_free')
    exclude = ('is_admin', 'is_staff', 'is_active', 'password',
               'groups', 'user_permissions', 'Superuser_status', )
    inlines = (IVInline, BVInline, ProfileImageInline,
               RecvChatInline, SentChatInline)

    def personal_info(self, user):
        try:
            return '{}({})'.format(user.iv.realname, user.iv.birthdate)
        except:
            return ''

    def verified(self, user):
        try:
            if(user.bv.image.count() > 0):
                if(user.bv.image.last().is_checked):
                    return '인증 완료'
                return '인증 진행중'
        except:
            return '미인증'

    def belong(self, user):
        try:
            return user.bv.belong
        except:
            return ''

    def department(self, user):
        try:
            return user.bv.department
        except:
            return ''


admin.site.register(User, UserAdmin)
admin.site.register(BVImage, BVImageAdmin)

# class UserAdmin(admin.ModelAdmin):
#     list_filter = ('is_certified',)
#     list_display = ('id', 'uid', 'nickname', 'birth', 'gender_string', 'real_name', 'is_certified_string', 'yami')
#     list_editable = ('yami',)
#     search_fields = ('nickname', 'uid', 'real_name')
#     readonly_fields = ('uid', 'real_name', 'last_login', 'created_at')
#     exclude = ('is_admin', 'is_staff', 'is_active', 'password', 'groups', 'user_permissions', 'Superuser_status')
#     ordering = ('-id',)

#     def gender_string(self, obj):
#         gen_str = ''
#         if obj.gender == 1:
#             gen_str = '남'
#         elif obj.gender == 0:
#             gen_str = '여'
#         return gen_str
#     def is_certified_string(self, obj):
#         cer_str = '미인증'
#         if(obj.is_certified == 1):
#             cer_str = '진행중'
#         elif(obj.is_certified == 2):
#             cer_str = '완료'
#         return cer_str
#     def has_add_permission(self, request):
#         return False
#     gender_string.short_description = "성별"


# admin.site.register(User, UserAdmin)
