from django.db import models
from lawyer_user.User import User


class BlogPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    title = models.CharField(max_length=45)
    content = models.CharField(max_length=2500)


class BlogCalification(models.Model):
    cal_user = models.ForeignKey(User, on_delete=models.SET_NULL,
                                 null=True)
    blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    like = models.BooleanField(default=True)


class BlogComment(models.Model):
    blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=450)


class Responce(models.Model):
    blog_comment = models.ForeignKey(BlogComment, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    description = models.CharField(max_length=450)
