from  .forms import CreatePostForm
from django.contrib import admin
from .models import  Author,Book,BookInstance,Genre, Transaction , Comment , Post

admin.site.register(Author)
admin.site.register(Book)
admin.site.register(BookInstance)
admin.site.register(Genre)
admin.site.register(Transaction)
admin.site.register(Comment)
admin.site.register(Post)

