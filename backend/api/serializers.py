from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers

from atlas_index.models import (
    AtlasUser,
    Collection,
    CollectionReport,
    CollectionTerm,
    Initiative,
    ReportObject,
    Term,
)

from .permissions import get_atlas_user_for_request_user

User = get_user_model()


class UserCurrentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]


class UserCurrentErrorSerializer(serializers.Serializer):
    username = serializers.ListSerializer(child=serializers.CharField(), required=False)
    first_name = serializers.ListSerializer(
        child=serializers.CharField(), required=False
    )
    last_name = serializers.ListSerializer(
        child=serializers.CharField(), required=False
    )


class UserChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    password_new = serializers.CharField(style={"input_type": "password"})
    password_retype = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    default_error_messages = {
        "password_mismatch": _("Current password is not matching"),
        "password_invalid": _("Password does not meet all requirements"),
        "password_same": _("Both new and current passwords are same"),
    }

    class Meta:
        model = User
        fields = ["password", "password_new", "password_retype"]

    def validate(self, attrs):
        request = self.context.get("request", None)

        if not request.user.check_password(attrs["password"]):
            raise serializers.ValidationError(
                {"password": self.default_error_messages["password_mismatch"]}
            )

        try:
            validate_password(attrs["password_new"])
        except ValidationError as e:
            raise exceptions.ValidationError({"password_new": list(e.messages)}) from e

        if attrs["password_new"] != attrs["password_retype"]:
            raise serializers.ValidationError(
                {"password_retype": self.default_error_messages["password_invalid"]}
            )

        if attrs["password_new"] == attrs["password"]:
            raise serializers.ValidationError(
                {"password_new": self.default_error_messages["password_same"]}
            )
        return super().validate(attrs)


class UserChangePasswordErrorSerializer(serializers.Serializer):
    password = serializers.ListSerializer(child=serializers.CharField(), required=False)
    password_new = serializers.ListSerializer(
        child=serializers.CharField(), required=False
    )
    password_retype = serializers.ListSerializer(
        child=serializers.CharField(), required=False
    )


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    password_retype = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    default_error_messages = {
        "password_mismatch": _("Password are not matching."),
        "password_invalid": _("Password does not meet all requirements."),
    }

    class Meta:
        model = User
        fields = ["username", "password", "password_retype"]

    def validate(self, attrs):
        password_retype = attrs.pop("password_retype")

        try:
            validate_password(attrs.get("password"))
        except exceptions.ValidationError:
            self.fail("password_invalid")

        if attrs["password"] == password_retype:
            return attrs

        return self.fail("password_mismatch")

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)

            # By default newly registered accounts are inactive.
            user.is_active = False
            user.save(update_fields=["is_active"])

        return user


class UserCreateErrorSerializer(serializers.Serializer):
    username = serializers.ListSerializer(child=serializers.CharField(), required=False)
    password = serializers.ListSerializer(child=serializers.CharField(), required=False)
    password_retype = serializers.ListSerializer(
        child=serializers.CharField(), required=False
    )


class InitiativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Initiative
        fields = ["initiative_id", "name", "description"]


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ["term_id", "name", "summary"]


class ReportObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportObject
        fields = ["report_id", "title", "name"]


class CollectionSerializer(serializers.ModelSerializer):
    initiative = InitiativeSerializer(read_only=True)
    initiative_id = serializers.PrimaryKeyRelatedField(
        source="initiative",
        queryset=Initiative.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )

    class Meta:
        model = Collection
        fields = [
            "collection_id",
            "name",
            "search_summary",
            "description",
            "hidden",
            "modified_at",
            "initiative",
            "initiative_id",
        ]
        read_only_fields = ["collection_id", "modified_at", "initiative"]

    def validate_hidden(self, value: str) -> str:
        v = (value or "").strip().upper()
        if v in {"Y", "YES", "TRUE", "1", "ON"}:
            return "Y"
        if v in {"N", "NO", "FALSE", "0", "OFF", ""}:
            return "N"
        raise serializers.ValidationError("Hidden must be 'Y' or 'N'.")

    def _set_modified_by(self, instance: Collection) -> None:
        request = self.context.get("request")
        if request is None or not getattr(request, "user", None):
            return

        atlas_user = get_atlas_user_for_request_user(request.user)
        if atlas_user is None:
            return

        instance.modified_by = AtlasUser.objects.get(pk=atlas_user.pk)

    def create(self, validated_data):
        instance = super().create(validated_data)
        self._set_modified_by(instance)
        instance.save(update_fields=["modified_by"])
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        self._set_modified_by(instance)
        instance.save(update_fields=["modified_by"])
        return instance


class CollectionReportSerializer(serializers.ModelSerializer):
    report = ReportObjectSerializer(read_only=True)
    report_id = serializers.PrimaryKeyRelatedField(
        source="report",
        queryset=ReportObject.objects.all(),
        allow_null=True,
        required=False,
    )
    collection_id = serializers.PrimaryKeyRelatedField(
        source="collection",
        queryset=Collection.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = CollectionReport
        fields = ["link_id", "collection_id", "report", "report_id", "rank"]
        read_only_fields = ["link_id"]


class CollectionTermSerializer(serializers.ModelSerializer):
    term = TermSerializer(read_only=True)
    term_id = serializers.PrimaryKeyRelatedField(
        source="term",
        queryset=Term.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )
    collection_id = serializers.PrimaryKeyRelatedField(
        source="collection",
        queryset=Collection.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )

    class Meta:
        model = CollectionTerm
        fields = ["link_id", "collection_id", "term", "term_id", "rank"]
        read_only_fields = ["link_id", "term"]


class CollectionDetailSerializer(CollectionSerializer):
    reports = CollectionReportSerializer(many=True, read_only=True)
    terms = CollectionTermSerializer(many=True, read_only=True)

    class Meta(CollectionSerializer.Meta):
        fields = CollectionSerializer.Meta.fields + ["reports", "terms"]


class ReportSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportObject
        fields = ["report_id", "title", "name"]


class TermSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ["term_id", "name"]
