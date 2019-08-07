from datetime import date
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from .utils import get_read_time, count_words
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q,F

class Transaction(models.Model):
    Customer = models.ForeignKey(User, on_delete = models.CASCADE)
    amount = models.IntegerField()

    def __str__(self):
        return self.amount

class Genre(models.Model):

    name = models.CharField(max_length=200 , help_text= "Enter a book genre (e.g. Science Fiction, French Poetry etc.)")

    def __str__(self):
        return self.name


class Book(models.Model):

    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL , null = True, blank=True)  # use ' ' on model if it hasn't been defined yet
    summary = models.TextField(max_length = 1000, null = True , blank = True)
    isbn = models.CharField('ISBN', max_length = 13 , null = True , blank = True)
    genre = models.ManyToManyField(Genre, help_text = 'Select genres')
    cover = models.FileField(upload_to = "books/cover_images" , null = True , blank = True)

    @property     # properties can be used to work for functions in html template code
    def total_copies(self):
        return BookInstance.objects.filter(book = self.title).count()

    @property
    def available_copies(self):
        return BookInstance.objects.filter(book = self.title).filter(status = 'a')


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('catalog:book-details' , args=[self.id])


class BookInstance(models.Model):

    class Meta:
        permissions = (('can_mark_returned','Set Book as returned'),)


    id = models.IntegerField(primary_key = True )
    book = models.ForeignKey(Book, on_delete = models.CASCADE)
    due_back = models.DateField()
    borrower = models.ForeignKey(User,on_delete = models.SET_NULL , null = True , blank = True )

    # second value in a tuple is what the user can see, the first one is actually stored in database
    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(max_length = 1 , choices = LOAN_STATUS , default = 'm')

    def __str__(self):
       return self.book.title

    @property   # used to get function like method like results in a template, can be used like attribute
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back :
            return True

        return False



class Author(models.Model):
    first_name = models.CharField(max_length = 100)
    last_name =  models.CharField(max_length = 100)
    date_of_birth = models.DateField(null=True , blank = True )

    def get_absolute_url(self):
        return reverse('catalog:author-details', args=[self.id])

    def __str__(self):
        return ( self.first_name + " " + self.last_name )


class Post(models.Model):
    title = models.CharField(max_length = 120)
    content = models.TextField(max_length = 1000000)
    created_by = models.ForeignKey(User,on_delete = models.CASCADE )
    created_on = models.DateTimeField(auto_now = False , auto_now_add = True )
    last_updated = models.DateTimeField(auto_now = True , auto_now_add = False, null=True)
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post-details' , args = [self.id])

    @property
    def post_thread(self):
        direct_comments = Comment.objects.filter(parent_comment=None, post=self)
        return direct_comments


    @property
    def read_time(self):
        read_time = get_read_time(self.content)
        return read_time

    class Meta:
        permissions = (('remove_post','can delete the post'),('edit_post','can edit the post'))
        ordering = ['created_on',]

    '''def get_readonly_fields(self,request,obj=None):
        if obj:
            return ['created_on','created_by']
        else:
            return []
    '''

class Comment(models.Model):
    parent_comment = models.ForeignKey('self',on_delete = models.CASCADE ,null=True ,blank=True)
    content = models.TextField(max_length=10000)
    post = models.ForeignKey(Post,on_delete = models.CASCADE,null=True)
    created_on = models.DateTimeField(auto_now=False, auto_now_add=True)  # auto_now_add is for saving the value as current for 1st time
    last_updated = models.DateTimeField(auto_now=True , auto_now_add=False)  # auto_now is useful for last update sort of fields.
    created_by = models.ForeignKey(User,on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.content[:30]

    def children(self):
        return Comment.objects.filter(parent_comment = self)

    class Meta:
        permissions = (('edit_comment','can edit the comment'),('remove_comment','can delete the comment'))
        ordering = ['created_on']
