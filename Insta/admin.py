from django.contrib import admin
from Insta.models import Post,InstaUser,Like,Userconnection,Comment
# Register your models here.
admin.site.register(Post)
admin.site.register(InstaUser)
admin.site.register(Like)
admin.site.register(Userconnection)
admin.site.register(Comment)