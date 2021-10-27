from blog.models import *
from django.db.models import Q
from rest_framework.decorators import action
from lawyer_user.models import *
from rest_framework import permissions, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from .permissions import *
from .serializers import *


class Login(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request.session['id'] = request.user.id
        request.session['email'] = request.user.email
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        request.session['id'] = request.user.id
        request.session['email'] = request.user.email
        return Response(status=status.HTTP_200_OK)


class Logout(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        request.session.flush()
        return Response(status=status.HTTP_200_OK)


class CreateUser(GenericAPIView, mixins.CreateModelMixin):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            request.session['id'] = user.id
            request.session['email'] = user.email
            return Response(self.serializer_class(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewset(viewsets.ModelViewSet):
    permission_classes = [Cookies]
    queryset = User.objects.all().order_by('pk')
    lookup_field = 'email'
    lookup_value_regex = '[\w@.]+'


    def get_serializer_class(self):
        try:
            if self.request.path[1:].split('/')[1] == 'me':
                return UserSerializer
            return PublicUserSerializer
        except IndexError:
            return PublicUserSerializer

    def self_view(self, request):
        id = request.session['id']
        user = User.objects.get(pk=id)
        context = {'request': request}
        serializer = self.get_serializer_class()
        return Response(serializer(user, context=context).data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        id = request.session['id']
        user = User.objects.get(pk=id)
        context = {'request': request}
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(user, data=request.data,
                                      context=context, partial=partial)
        if serializer.is_valid():
            return Response(serializer_class(serializer.save(), context=context).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def list(self, request):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, email=None):
        context = {'request': request}
        user = self.get_object()
        serializer = self.get_serializer_class()
        return Response(serializer(user, context=context).data)


class AccountViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = AccountSerializer
    queryset = Account.objects.all().order_by('pk')
    lookup_field = 'name'

    def self_view(self, request):
        try:
            id = request.session['id']
            user = User.objects.get(pk=id)
            context = {'request': request}
            return Response(self.serializer_class(user.account_type,
                                                  context=context).data)
        except KeyError:
            return Response({'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_403_FORBIDDEN)


class LawyerViewset(viewsets.ModelViewSet):
    permission_classes = [Cookies]
    serializer_class = LawyerSerializer
    queryset = Lawyer.objects.all().order_by('pk')

    def list(self, request, user_email=None):
        context = {'request': request}
        if user_email == 'me':
            user_id = request.session['id']
            user = User.objects.get(pk=user_id)
        else:
            user = User.objects.get(email=user_email)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def create(self, request, user_email=None):
        if user_email != 'me':
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(pk=request.session['id'])
            obj = serializer.save(lawyer=user)
            return Response(self.serializer_class(obj).data)


class UserCalificationsViewset(viewsets.ModelViewSet):
    permission_classes = [OwnerOrOnlyRead]
    serializer_class = UserCalificationSerializer
    queryset = UserCalification.objects.all().order_by('pk')


    def self_view(self, request):
        try:
            id = request.session['id']
            user = User.objects.get(pk=id)
            context = {'request': request}
            return Response(self.serializer_class(user.comentaries.get(),
                                                  context=context).data)
        except KeyError:
            return Response({'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_403_FORBIDDEN)

    def list(self, request, user_email=None, id=None):
        context = {'request': request}
        if user_email == 'me':
            user_id = request.session['id']
        else:
            user_id = User.objects.get(email=user_email).pk
        user = User.objects.get(pk=user_id)
        queryset = UserCalification.objects.filter(target=user).order_by('pk')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def create(self, request, user_email=None):
        context = {'request': request}
        serializer = self.serializer_class(data=request.data)
        target = User.objects.get(email=user_email)
        owner = User.objects.get(pk=request.session['id'])
        if owner == target:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if serializer.is_valid():
            com = serializer.save(owner=owner, target=target)
            com.save()
            return Response(self.serializer_class(com,
                                                  context=context).data)
        return Response(serializer.errors)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class UserCommentariesViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [OwnerOrOnlyRead]
    serializer_class = UserCalificationSerializer
    queryset = UserCalification.objects.all().order_by('pk')

    def list(self, request, user_email=None, id=None):
        context = {'request': request}
        if user_email == 'me':
            user_id = request.session['id']
            user = User.objects.get(pk=user_id)
        else:
            user = User.objects.get(email=user_email)
        queryset = UserCalification.objects.filter(owner=user).order_by('pk')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BufeteViewset(viewsets.ModelViewSet):
    permission_classes = [LROrReadOnly]
    serializer_class = BufeteSerializer
    queryset = Bufete.objects.all().order_by('pk')

    def self_view(self, request):
        context = {'request': request}
        user = User.objects.get(pk=request.session['id'])
        queryset = Bufete.objects.filter(lawyers=user).order_by('pk')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        context = {'request': request}
        lr_id = request.session['id']
        lr = User.objects.get(pk=lr_id)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            obj = serializer.save(legal_representative=lr, lawyers=[lr])
            return Response(self.serializer_class(obj.save(), context=context).data)
        return Response(serializer.errors)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class BufeteCalificationsViewset(viewsets.ModelViewSet):
    permission_classes = [OwnerOrOnlyRead]
    serializer_class = BufeteCalificationSerializer
    queryset = BufeteCalification.objects.all().order_by('pk')

    def list(self, request, bufete_pk=None):
        context = {'request': request}
        bufete = Bufete.objects.get(pk=bufete_pk)
        queryset = BufeteCalification.objects.filter(target=bufete).order_by('pk')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def create(self, request, bufete_pk=None):
        context = {'request': request}
        serializer = self.serializer_class(data=request.data)
        target = Bufete.objects.get(pk=bufete_pk)
        owner = User.objects.get(pk=request.session['id'])
        if serializer.is_valid():
            com = serializer.save(owner=owner, target=target)
            return Response(self.serializer_class(com,
                                                  context=context).data)
        return Response(serializer.errors)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CaseViewset(viewsets.ModelViewSet):
    permission_classes = [CasePermisions]

    def get_queryset(self):
        user_id = self.request.session['id']
        user = User.objects.get(pk=user_id)
        try:
            if self.request.path[1:].split('/')[1] == 'me':
                return Case.objects.filter(Q(owner=user) |
                                           Q(in_representation_of=user))
            if len(user.bellow_to.all()) or user.lawyer:
                return Case.objects.all()
        except IndexError:
            if len(user.bellow_to.all()) or user.lawyer:
                return Case.objects.all()
            return Case.objects.filter(Q(owner=user) |
                                       Q(in_representation_of=user))
        except ObjectDoesNotExist:
            return Case.objects.filter(Q(owner=user) |
                                       Q(in_representation_of=user))

    def get_serializer_class(self):
        try:
            if self.request.path[1:].split('/')[1] == 'me':
                return CaseSerializer
        except IndexError:
            if self.action == 'list':
                return PublicCaseSerializer
        finally:
            return CaseSerializer

    @action(methods=['get'], detail=True)
    def postulations(self, request, pk=None):
        context = {'request': request}
        serializer = InterestedSerializer
        inte = Interested.objects.filter(case__pk=pk)
        return Response(serializer(inte, many=True, context=context).data)

    @action(methods=['post'], detail=True, permission_classes=[IsLawyer])
    def postulate(self, request, pk=None):
        context = {'request': request}
        reqdata = request.data
        bufete_id = reqdata.pop('bufete', None)
        user = User.objects.get(pk=request.session['id'])
        if bufete_id:
            bufete = Bufete.objects.get(pk=bufete_id)
        else:
            bufete = None
        data = {'user': user, 'bufete': bufete, 'case': self.get_object()}
        serializer = InterestedSerializer(data=data)
        if serializer.is_valid():
            obj = serializer.save(**data)
            return Response(InterestedSerializer(obj, context=context).data)
        return Response(serializer.errors)


class BlogpostViewset(viewsets.ModelViewSet):
    permission_classes = [OwnerOrOnlyRead]
    queryset = BlogPost.objects.all()
    serializer_class = BlogpostSerializer

    def self_view(self, request):
        context = {'request': request}
        user = User.objects.get(pk=request.session['id'])
        queryset = BlogPost.objects.filter(owner=user).order_by('pk')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        context = {'request': request}
        user = User.objects.get(pk=request.session['id'])
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            obj = serializer.save(owner=user)
            return Response(self.serializer_class(obj, context=context).data)
        return Response(serializer.errors)


class BlogCalificationViewset(viewsets.ModelViewSet):
    permission_classes = [OwnerOrOnlyRead]
    queryset = BlogCalification.objects.all()
    serializer_class = BlogCalificationSerializer

    def create(self, request, blog_pk=None):
        context = {'request': request}
        user = User.objects.get(pk=request.session['id'])
        blog = BlogPost.objects.get(pk=blog_pk)
        try:
            Response(blog.califications.get(owner=user))
            return Response({'detail': 'You can only perform one calification per blog'})
        except ObjectDoesNotExist:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                obj = serializer.save(owner=user, blog=blog)
                return Response(self.serializer_class(obj, context=context).data)
            return Response(serializer.errors)


class BlogCommentViewset(viewsets.ModelViewSet):
    permission_classes = [OwnerOrOnlyRead]
    queryset = BlogComment.objects.all()
    serializer_class = BlogCommentSerializer

    def create(self, request, blog_pk=None):
        context = {'request': request}
        user = User.objects.get(pk=request.session['id'])
        blog = BlogPost.objects.get(pk=blog_pk)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            obj = serializer.save(owner=user, blog=blog)
            return Response(self.serializer_class(obj, context=context).data)
        return Response(serializer.errors)

    def list(self, request, blog_pk=None):
        context = {'request': request}
        queryset = BlogComment.objects.filter(blog=blog_pk).order_by('pk')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context=context)
        return Response(serializer.data)


class ResponceViewset(viewsets.ModelViewSet):
    permission_classes = [OwnerOrOnlyRead]
    queryset = Responce.objects.all()
    serializer_class = ResponceSerializer

    def create(self, request, blog_pk=None, blogcomment_pk=None):
        context = {'request': request}
        user = User.objects.get(pk=request.session['id'])
        blog_comment = BlogComment.objects.get(pk=blogcomment_pk)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            obj = serializer.save(owner=user, blog_comment=blog_comment)
            return Response(self.serializer_class(obj, context=context).data)
        return Response(serializer.errors)

    def list(self, request, blog_pk=None, blogcomment_pk=None):
        context = {'request': request}
        queryset = Responce.objects.filter(blog_comment=blogcomment_pk).order_by('pk')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context=context)
        return Response(serializer.data)
