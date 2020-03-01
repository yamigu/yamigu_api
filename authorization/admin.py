from django.contrib import admin
from .models import *
admin.site.register(User)
admin.site.register(Location)
admin.site.register(ProfileImage)
admin.site.register(IdentityVerification)
admin.site.register(BelongVerification)
admin.site.register(BVImage)
admin.site.register(FirebaseToken)
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
