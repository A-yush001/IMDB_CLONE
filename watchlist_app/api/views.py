from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from watchlist_app.models import WatchList,StreamPlatform,Review
from watchlist_app.api.serializers import WatchListSerializer,StreamPlatformSerializer,ReviewSerializer
from rest_framework.response import Response
#from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from watchlist_app.api.permissions import IsAdminOrReadOnly,IsReviewUserOrReadOnly
from rest_framework.throttling import UserRateThrottle,AnonRateThrottle,ScopedRateThrottle
from watchlist_app.api.throttling import ReviewCreateThrottle, ReviewListThrottle
from watchlist_app.api.pagination import WatchlistPaginations


class UserReview(generics.ListAPIView):
     serializer_class = ReviewSerializer
     #throttle_classes = [ReviewListThrottle,AnonRateThrottle]
   # permission_classes=[IsAuthenticated]

     #def get_queryset(self):
     #   username=self.kwargs['username']
      #  return Review.objects.filter(review_user__username=username)

     def get_queryset(self):
        username = self.request.query_params.get('username')
        return Review.objects.filter(review_user__username=username)
    


class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes=[IsAuthenticated]
    throttle_classes=[ReviewCreateThrottle]
    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self, serializer):
         pk=self.kwargs['pk']
         Watchlist=WatchList.objects.get(pk=pk)

         review_user=self.request.user
         request_queryset =Review.objects.filter( WatchList=Watchlist, review_user=review_user)

         if request_queryset.exists():
                raise ValidationError("You have already reviewed this movie!!")
         
         if Watchlist.number_rating ==0:
             Watchlist.avg_rating=serializer.validated_data['rating']   
         else:
               Watchlist.avg_rating  =( Watchlist.avg_rating+serializer.validated_data['rating'])/2;
         
         Watchlist.number_rating=Watchlist.number_rating+1

         Watchlist.save() 

         serializer.save(WatchList=Watchlist,review_user=review_user)
        

class ReviewList(generics.ListAPIView):
    #queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    throttle_classes = [ReviewListThrottle,AnonRateThrottle]
   # permission_classes=[IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['review_user__username', 'active']
    def get_queryset(self):
        pk=self.kwargs['pk']
        return Review.objects.filter(WatchList=pk)


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes=[IsReviewUserOrReadOnly]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'review-detail'
    pagination_class = WatchlistPaginations













#class ReviewDetail(mixins.RetrieveModelMixin,generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer
#
#     def get(self, request, *args, **kwargs):
#            return self.retrieve(request, *args, **kwargs)
#
#class ReviewList(mixins.ListModelMixin,
#                  mixins.CreateModelMixin,
#                  generics.GenericAPIView):
#    queryset = Review.objects.all()
#    serializer_class = ReviewSerializer
#
#    def get(self, request, *args, **kwargs):
#        return self.list(request, *args, **kwargs)
#
#    def post(self, request, *args, **kwargs):
#        return self.create(request, *args, **kwargs)








class WatchListAV(APIView):
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = WatchlistPaginations


    def get(self,request):
        movies=WatchList.objects.all()
        serializer=WatchListSerializer(movies,many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer=WatchListSerializer(data=request.data)
        if serializer.is_valid():
           serializer.save()
           return Response(serializer.data)
        else:
           return Response(serializer.errors)



class WatchDetailAV(APIView):
    permission_classes = [IsAdminOrReadOnly]
    def get(self,request,pk):
        try:
           movie=WatchList.objects.get(pk=pk)
        except WatchList.DoesNotExist:
           return Response({'Error':"Movie not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer=WatchListSerializer(movie)
        return Response(serializer.data)
    
    def put(self,request,pk):
        movie=WatchList.objects.get(pk=pk)
        serializer=WatchListSerializer(movie,data=request.data)
        if serializer.is_valid():
           serializer.save()
           return Response(serializer.data)
        else:
           return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self,request,pk):
        movie=WatchList.objects.get(pk=pk)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class StreamPlatformVS(viewsets.ModelViewSet):
    queryset = StreamPlatform.objects.all()
    serializer_class =StreamPlatformSerializer
    permission_classes = [IsAdminOrReadOnly]

#class StreamPlatformVS(viewsets.ViewSet):
#    def list(self, request):
#        queryset = StreamPlatform.objects.all()
#        serializer =StreamPlatformSerializer(queryset, many=True)
#        return Response(serializer.data)
#
#    def retrieve(self, request, pk=None):
#        queryset = StreamPlatform.objects.all()
#        WatchList = get_object_or_404(queryset, pk=pk)
#        serializer = StreamPlatformSerializer(WatchList)
#        return Response(serializer.data)
#    
#    def create(self,request):
#        serializer=StreamPlatformSerializer(data=request.data)
#        if serializer.is_valid():
#                serializer.save()
#                return Response(serializer.data)
#        else:
#               return Response(serializer.errors)



class StreamPlatformAV(APIView):
       def get(self,request):
             platform=StreamPlatform.objects.all()
             serializer=StreamPlatformSerializer(platform,many=True)
             return Response(serializer.data)
       
       def post(self,request):
             serializer=StreamPlatformSerializer(data=request.data)
             if serializer.is_valid():
               serializer.save()
               return Response(serializer.data)
             else:
               return Response(serializer.errors)

class StreamPlatformDetails(APIView):
   def get(self,request,pk):
          try:
              platform=StreamPlatform.objects.get(pk=pk)
          except StreamPlatform.DoesNotExist:
              return Response({'Error':"Platform not found"}, status=status.HTTP_404_NOT_FOUND)
              
          serializer=StreamPlatformSerializer(platform)
          return Response(serializer.data)
   

   def put(self,request,pk):
       platform=StreamPlatform.objects.get(pk=pk)
       serializer=StreamPlatformSerializer(platform,data=request.data)
       if serializer.is_valid():
           serializer.save()
           return Response(serializer.data)
       else:
           return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
       

   def delete(self, request,pk):
       platform=StreamPlatform.objects.get(pk=pk) 
       platform.delete()
       return Response(status=status.HTTP_204_NO_CONTENT) 
           
             
             


























#@api_view(['GET','POST'])
#def movie_list(request):
#    if request.method == 'GET':
#        movies=Movie.objects.all()
#        serializer=MovieSerializer(movies,many=True)
#        return Response(serializer.data)
#    if request.method == 'POST':
#        serializer=MovieSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data)
#        else:
#            return Response(serializer.errors)
#
#@api_view(['GET','PUT','DELETE'])
#def movie_details(request,pk):
#    if request.method == 'GET':
#        try:
#            movie=Movie.objects.get(pk=pk)
#        except Movie.DoesNotExist:
#            return Response({'Error':"Movie not found"}, status=status.HTTP_404_NOT_FOUND)
#
#        serializer=MovieSerializer(movie)
#        return Response(serializer.data)
#    
#    if request.method == 'PUT':
#        movie=Movie.objects.get(pk=pk)
#        serializer=MovieSerializer(movie,data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data)
#        else:
#            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
#
#
#    if request.method == 'DELETE':
#        movie=Movie.objects.get(pk=pk)
#        movie.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)