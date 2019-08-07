from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render , get_object_or_404, redirect
from django.http import  HttpResponse , JsonResponse
from django.views import  generic
from django.views.generic import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required , permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin   # for class-based views
from .models import  Book,BookInstance,Author , Transaction, Post, Comment
from .forms import RenewBookForm , CreatePostForm
import datetime
import stripe     # library by stripe to provide API functionality
from django.views.generic.edit import CreateView, UpdateView , DeleteView
from django.contrib import messages

class BookCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):

    permission_required = ('catalog.can_mark_returned',)
    model = Book
    fields = ['title','author','summary','genre']    # these fields get associated with the form which is automatically sent to the template
    template_name = 'catalog/add_book.html'

class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'genre']
    template_name = 'catalog/add_book.html'


class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    #login_url = '/catalog/accounts/login'  # reqd. by LoginRequiredMixin  , redirect_field_name = 'next' - by default ,
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    context_object_name = 'bookinstance_list'

    def get_queryset(self):    # to set the object(s) contexed to the HTML template
        return BookInstance.objects.filter(borrower = self.request.user).filter(status = 'o')


def index(request):

    #request.session.set_test_cookie()

    storage = messages.get_messages(request)

    visits = request.session.get('visits',0)
    request.session['visits'] = visits + 1

    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    num_instances_available = BookInstance.objects.filter(status = 'a').count()
    num_authors = Author.objects.all().count()

    return render(request,'catalog/index.html', context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors,'visits':visits,'storage':storage})

    #response.set_cookie('visits',visits +1)
    #return response


def temp(request):
    if not request.COOKIES.get('fav_color'):    # a website can only access its own cookies , safety features within web browsers
        if request.method == 'GET':
            return render(request,'catalog/ask_color.html')

        else:
            fav_color = request.POST.get('fav_color','')
            response = HttpResponse("Cookie set")
            response.set_cookie('fav_color',fav_color, 3600)
            return response
    else:
        color = request.COOKIES.get('fav_color')
        return render(request,'catalog/cookies.html',{'color':color})

class BookListView(generic.ListView):
    model = Book
    template_name = 'Books_Display.html'
    context_object_name = 'Book_List'

    def get_queryset(self):
        return Book.objects.all()

class BookDetails(generic.DetailView):
    model = Book
    template_name = "catalog/Book_Details.html"      # the context model is automatically passed in 'lowered-case' to the template

@permission_required('catalog.can_mark_returned',login_url="/catalog/accounts/login/")
def renew_book_librarian(request, book_id):
    book_inst = get_object_or_404(BookInstance,pk = book_id)

    #binding data to the form model
    if request.method == 'POST':
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_inst.due_back = form.cleaned_data['renew_date']
            book_inst.save()

            return HttpResponseRedirect(reverse('catalog:index'))  # reverse generates the url from view name

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks = 3)
        form = RenewBookForm(initial = {'renew_date': proposed_renewal_date ,})  # the last comma indicates that this is not just a single element but a dictionary

    return render(request,'catalog/book_renew_librarian.html',{ 'form':form , 'bookinst':book_inst })

@login_required(login_url = "/catalog/accounts/login/")
def borrow_book(request,book_id):
    bookt = Book.objects.get(pk = book_id)
    book_title = bookt.title
    availables = BookInstance.objects.filter(book = book_id).filter(status = 'a')

    if availables:
        IssueBookId = availables[0].id
        IssueBook = BookInstance.objects.get(pk = IssueBookId)
        IssueBook.status = 'o'
        IssueBook.borrower = request.user
        IssueBook.due_back =  datetime.date.today() + datetime.timedelta(weeks = 3)
        IssueBook.save()
        return  HttpResponse("You have successfully issued book ")

    else:
        return HttpResponse("This book is not available to issue")


# function that is called by ajax to return data/ book suggestions
def suggest(request):

    if request.method == 'POST':
        tolook = request.POST['string']
        result = Book.objects.filter(title__startswith = tolook)
        if result :
            return render(request,'catalog/suggest.html', {'result':result })
        else:
            return HttpResponse('no suggestions')

    else:
        tolook = request.GET['string']
        result = Book.objects.filter(title__startswith = tolook)
        if result:
            return render(request, 'catalog/suggest.html', {'result': result})
        else:
            return HttpResponse('no suggestions')

def pay(request):

    stripe.api_key = "sk_test_DWYn74ZR8o3jdsjqIH1oQFXv"
    token = request.POST['stripeToken']

    charge = stripe.Charge.create(
        amount = 999,
        currency = 'usd',
        description = 'Example charge',
        source = token,
    )

    return HttpResponseRedirect(reverse('catalog:index'))

def paytm(request):
   pass

@login_required(login_url = '/catalog/accounts/login/')
def pay_with_stripe(request):

    if request.method == 'POST':
        amount = int(request.POST['amount']) * 100

    else:
        amount = 100

    stripe_key = "pk_test_L7UWO6ZqRCmS6NY4WNb7ryGw"
    return render(request,"catalog/stripe_test.html",{'stripe_key':stripe_key , 'amount':amount})


def checkout(request):  # for stripe-gateway

    stripe.api_key = "sk_test_DWYn74ZR8o3jdsjqIH1oQFXv"
    token = request.POST['stripeToken']

    if request.method == 'POST':
        money = int(request.POST['amount'])

    else:
        money = 100


    try:
        charge = stripe.Charge.create(
            amount= money,
            currency='usd',
            description='Example charge',
            source=token,
        )
    except stripe.error.CardError as ce:
        return False

    Transaction.objects.create(Customer = request.user, amount = money/100)

    return render(request,'catalog/payment done.html',)


class PostListView(ListView):
    model = Post
    template_name = 'catalog/posts.html'
    context_object_name = 'post_List'

    def get_quryset(self,request):     # overrides queryset attribute, if set, in the class
        return Post.objects.all()

class PostDetail(DetailView):
    model = Post
    template_name = 'catalog/post_details.html'
    context_object_name = 'post'

@login_required()
def PostCreate(request):

    if request.method == 'GET':
        form = CreatePostForm()  # creates a blank form instance
        return render(request,'catalog/add_post.html',{ 'form':form ,})

    elif request.method == 'POST':
        form = CreatePostForm(request.POST)

        if form.is_valid():
            f = CreatePostForm(request.POST)   # since this is a modelform, f gets converted to a post instance
            new_post = f.save(commit=False)   # does not hit the database
            new_post.created_by = request.user
            new_post.created_on = datetime.datetime.now()
            new_post.save()
            return HttpResponseRedirect(reverse('catalog:post-list'))

        else:
            return render(request,'catalog/add_post.html',{'form':form,})


class PostUpdate(LoginRequiredMixin,UpdateView):

    model = Post
    fields = ['title','content']
    template_name = 'catalog/add_post.html'


class PostDelete(LoginRequiredMixin,DeleteView):
    model = Post


@login_required()
def AddComment(request,post_id):

    if request.method == 'POST':
        comment_data = request.POST.get("Content")
        if(comment_data):
            target_post = get_object_or_404(Post, pk = post_id)
            CurrentUser = request.user
            if target_post:                                          # just for verification
                new_comment = Comment(content=comment_data,created_by=CurrentUser,post=target_post)
                if request.POST.get("parent_comment",None):
                    new_comment.parent_comment = request.POST.get("parent_comment")

                new_comment.save()

                if request.is_ajax():
                    return JsonResponse({'content':comment_data , 'time':new_comment.created_on})
                else:
                    return HttpResponseRedirect(reverse('catalog:post-details', args=[post_id,]))

    else:
        return HttpResponse("Invalid Request")


@login_required()
def AddAjaxComment(request,post_id):

    if request.method == 'POST':
        comment_data = request.POST.get("Cont")
        if(comment_data):
            target_post = get_object_or_404(Post, pk = post_id)
            CurrentUser = request.user
            if target_post:
                new_comment = Comment(content=comment_data,created_by=CurrentUser,post=target_post)
                new_comment.save()
                return render(request,'catalog/ajax_comment.html',{'string':new_comment.content ,})

        else:
            return HttpResponse("No data posted")

    else:
        return HttpResponse("Invalid Request")

@login_required()
def EditComment(request,comment_id):
    target_comment = get_object_or_404(Comment,pk=comment_id)

    if request.user == target_comment.created_by or request.user.is_superuser:

        if request.method == 'POST':
            new_content = request.POST.get('EditedContent',None)
            if new_content:
                target_comment.content = new_content
                target_comment.save()
                post = target_comment.post
                post_id = post.id
                return HttpResponseRedirect(reverse('catalog:post-details', args=[post_id]))

        else:
            return HttpResponseRedirect(reverse('catalog:post-list'))

    else:
        return HttpResponse("You are not authorised to access the page")

@login_required()
def EditCommentAjax(request,comment_id):
    target_comment = get_object_or_404(Comment,pk=comment_id)

    if request.user == target_comment.created_by or request.user.is_superuser:

        if request.method == 'POST':
            new_content = request.POST.get('EditedContent',None)
            if new_content:
                target_comment.content = new_content
                target_comment.save()
                post = target_comment.post
                return HttpResponse("Thank you")

        else:
            return HttpResponseRedirect(reverse('catalog:post-list'))

    else:
        return HttpResponse(" Unauthorised Access",status=403)

@login_required()
def DeleteComment(request,comment_id):

    target_comment = get_object_or_404(Comment, pk=comment_id)

    if request.user == target_comment.created_by or request.user.is_superuser:

        target_comment.delete()
        return HttpResponse("Deletion Successful",status=200)

    else:
        return HttpResponse("You are not authorised to access this url",status=403)



def test_message(request):
    messages.add_message(request,messages.INFO,'welcome')
    return render(request,'catalog/TestMessage.html',{})