from django.contrib.auth import get_user_model
from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atlas_index.models import (
    Collection,
    CollectionReport,
    CollectionTerm,
    ReportObject,
    Term,
)

from .permissions import AtlasRolePermission
from .serializers import (
    CollectionDetailSerializer,
    CollectionReportSerializer,
    CollectionSerializer,
    CollectionTermSerializer,
    ReportSearchSerializer,
    TermSearchSerializer,
    UserChangePasswordErrorSerializer,
    UserChangePasswordSerializer,
    UserCreateErrorSerializer,
    UserCreateSerializer,
    UserCurrentErrorSerializer,
    UserCurrentSerializer,
)

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserCurrentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(pk=self.request.user.pk)

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action == "me":
            return UserCurrentSerializer
        elif self.action == "change_password":
            return UserChangePasswordSerializer

        return super().get_serializer_class()

    @extend_schema(
        responses={
            200: UserCreateSerializer,
            400: UserCreateErrorSerializer,
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: UserCurrentSerializer,
            400: UserCurrentErrorSerializer,
        }
    )
    @action(["get", "put", "patch"], detail=False)
    def me(self, request, *args, **kwargs):
        if request.method == "GET":
            serializer = self.get_serializer(self.request.user)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = self.get_serializer(
                self.request.user, data=request.data, partial=False
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == "PATCH":
            serializer = self.get_serializer(
                self.request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @extend_schema(
        responses={
            204: None,
            400: UserChangePasswordErrorSerializer,
        }
    )
    @action(["post"], url_path="change-password", detail=False)
    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["password_new"])
        self.request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["delete"], url_path="delete-account", detail=False)
    def delete_account(self, request, *args, **kwargs):
        self.request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, AtlasRolePermission]
    queryset = Collection.objects.all().order_by("-modified_at")

    def get_permissions(self):
        if self.action == "create":
            self.required_permissions = ("Create Collection",)
        elif self.action in {"update", "partial_update", "set_links"}:
            self.required_permissions = ("Edit Collection",)
        elif self.action == "destroy":
            self.required_permissions = ("Delete Collection",)
        else:
            self.required_permissions = ()

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CollectionDetailSerializer
        return CollectionSerializer

    @action(["post"], detail=True, url_path="set-links")
    def set_links(self, request, *args, **kwargs):
        collection: Collection = self.get_object()
        report_ids = request.data.get("report_ids", [])
        term_ids = request.data.get("term_ids", [])

        if report_ids is None:
            report_ids = []
        if term_ids is None:
            term_ids = []

        if not isinstance(report_ids, list):
            return Response(
                {"report_ids": "Expected a list of report IDs."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(term_ids, list):
            return Response(
                {"term_ids": "Expected a list of term IDs."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            CollectionReport.objects.filter(collection=collection).delete()
            CollectionTerm.objects.filter(collection=collection).delete()

            CollectionReport.objects.bulk_create(
                [
                    CollectionReport(
                        collection=collection,
                        report_id=rid,
                        rank=i,
                    )
                    for i, rid in enumerate(report_ids)
                ]
            )

            CollectionTerm.objects.bulk_create(
                [
                    CollectionTerm(
                        collection=collection,
                        term_id=tid,
                        rank=i,
                    )
                    for i, tid in enumerate(term_ids)
                ]
            )

        serializer = CollectionDetailSerializer(collection)
        return Response(serializer.data)

    def perform_destroy(self, instance: Collection) -> None:
        with transaction.atomic():
            CollectionReport.objects.filter(collection=instance).delete()
            CollectionTerm.objects.filter(collection=instance).delete()
            instance.delete()


class CollectionReportViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionReportSerializer
    permission_classes = [IsAuthenticated, AtlasRolePermission]
    queryset = CollectionReport.objects.select_related("collection", "report").all()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            self.required_permissions = ("Edit Collection",)
        else:
            self.required_permissions = ()
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        collection_id = self.request.query_params.get("collection_id")
        if collection_id:
            return qs.filter(collection_id=collection_id)
        return qs


class ReportSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        q = (request.query_params.get("q") or "").strip()
        qs = ReportObject.objects.all()

        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(name__icontains=q)

        qs = qs.order_by("title")[:20]
        return Response(ReportSearchSerializer(qs, many=True).data)


class TermSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        q = (request.query_params.get("q") or "").strip()
        qs = Term.objects.all()

        if q:
            qs = qs.filter(name__icontains=q)

        qs = qs.order_by("name")[:20]
        return Response(TermSearchSerializer(qs, many=True).data)


class CollectionTermViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionTermSerializer
    permission_classes = [IsAuthenticated, AtlasRolePermission]
    queryset = CollectionTerm.objects.select_related("collection", "term").all()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            self.required_permissions = ("Edit Collection",)
        else:
            self.required_permissions = ()
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        collection_id = self.request.query_params.get("collection_id")
        if collection_id:
            return qs.filter(collection_id=collection_id)
        return qs
