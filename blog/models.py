from django.db import models
from lawyer_user.models import Tag
from lawyer_user.User import User


class BlogPost(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    title = models.CharField(max_length=45)
    content = models.CharField(max_length=2500)
    types = [
             ('NT', 'Noticias'),
             ('LB', 'Blog de abogados'),
             ('UB', 'Blog de Usuarios')
            ]
    type = models.CharField(max_length=2, choices=types)
    tags = models.ManyToManyField(Tag)


class BlogCalification(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL,
                                 null=True)
    blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    like = models.BooleanField(default=True)


class BlogComment(models.Model):
    blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=450)


class Responce(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    blog_comment = models.ForeignKey(BlogComment, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    description = models.CharField(max_length=450)
