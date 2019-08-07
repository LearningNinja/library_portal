from django.urls import path , include, re_path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.index,name='index'),   # function based view
    path('books/',views.BookListView.as_view(),name='books'),   # class based view
    path('books/<int:pk>/',views.BookDetails.as_view(),name='book-details'),
    path('accounts/', include('django.contrib.auth.urls')),                      # handles the login, logout logic
    path('books/borrowed/',views.LoanedBooksByUserListView.as_view(),name='my-borrowed'),
    path('book/<int:book_id>/renew/',views.renew_book_librarian, name = 'renew-book-librarian'),  # book_id variable is accesible to the view directly
    path('books/<int:book_id>/issue/',views.borrow_book, name='book-issue'),
    path('return_suggestions/',views.suggest,name='suggest'),
    path('pay/',views.pay,name = 'collect-payment'),
    path('checkout/',views.checkout,name='checkout'),
    path('pay_with_stripe/',views.pay_with_stripe,name='stripe'),
    path('add_book/',views.BookCreate.as_view(),name='book-create'),
    path('update/book/<int:pk>/',views.BookUpdate.as_view(),name='book-update'),
    path('blogs/',views.PostListView.as_view(),name='post-list'),
    path('blogs/<int:pk>/',views.PostDetail.as_view(),name='post-details'),
    path('blogs/create/',views.PostCreate,name='post-create'),
    path('blogs/<int:post_id>/comment/',views.AddComment,name='make-comment'),
    path('blogs/edit_comment/<int:comment_id>/',views.EditComment,name='edit-comment'),
    path('blogs/edit_comment_ajax/<int:comment_id>/',views.EditCommentAjax,name='edit-comment-ajax'),
    path('blogs/<int:post_id>/ajax_comment/',views.AddAjaxComment,name='ajax-comment'),
    path('blogs/delete_comment/<int:comment_id>/',views.DeleteComment,name='delete-comment'),
    path('temp/',views.temp),
    path('message_framework/',views.test_message,name='message')
    #path('pay_with_paytm/',views.pay_with_paytm,name='paytm'),
    #path('paytm_response/',views.paytm_response,name='paytm_response'),



]