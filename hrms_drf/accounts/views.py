from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework.decorators import action, api_view, permission_classes
from django.contrib.auth import get_user_model

from accounts.serializers import RegisterSerializer, UserSerializer, UserPhotoSerializer
from accounts.permissions import IsHRUser

User = get_user_model()


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh = request.data.get('refresh')
            token = OutstandingToken.objects.get(token=refresh)
            BlacklistedToken.objects.create(token=token)
            return Response({'success': True, 'message': 'Logged out'})
        except:
            return Response({'error': 'Invalid token'}, status=400)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    # permission_classes = [IsAuthenticated, IsHRUser]
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RegisterSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        username = instance.username

        if instance.id == request.user.id:
            return Response(
                {
                    'success': False,
                    'error': 'Cannot delete your own account'
                },
                status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)

        return Response(
            {
                'success': True,
                'message': f'User "{username}" deleted successfully'
            },
            status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response({'success': True, 'user': serializer.data})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def upload_user_photo(request):
    user = request.user
    serializer = UserPhotoSerializer(user,
                                     data=request.data,
                                     partial=True,
                                     context={'request': request})

    if serializer.is_valid():
        serializer.save()
        photo_url = request.build_absolute_uri(user.photo.url)
        print(photo_url)
        return Response({'photo': photo_url}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)