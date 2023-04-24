from django.contrib import admin
from django.urls import  path,include
#from watchlist_app.api.views import movie_list,movie_details
from watchlist_app.api.views import WatchListAV,WatchDetailAV,StreamPlatformAV,StreamPlatformDetails,ReviewList,ReviewDetail,ReviewCreate,StreamPlatformVS,UserReview
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register(r'stream',StreamPlatformVS,basename='streamplatform')


urlpatterns = [
   
    path('list/', WatchListAV.as_view(), name='movie_list'),
    path('list/<int:pk>/', WatchDetailAV.as_view(), name='movie_details'),
    path('', include(router.urls)),
    
    #path('stream/', StreamPlatformAV.as_view(), name='Stream_platform'),
    # path('stream/<int:pk>/', StreamPlatformDetails.as_view(), name='platform_details'),
    path('<int:pk>/review_create/', ReviewCreate.as_view(), name='Review-create'),

    path('<int:pk>/reviews/', ReviewList.as_view(), name='ReviewList'),
    path('review/<int:pk>/', ReviewDetail.as_view(), name='ReviewDetail'),
    path('review/', UserReview.as_view(), name='user-ReviewDetail'),

    
]