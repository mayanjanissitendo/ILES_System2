from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import decorators, permissions, response, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .models import Evaluation, EvaluationCriteria, InternshipPlacement, WeeklyLog
from .permissions import IsSupervisorOrAdmin
from .serializers import (
    DashboardSerializer,
    EvaluationCriteriaSerializer,
    EvaluationSerializer,
    InternshipPlacementSerializer,
    ScoreBreakdownSerializer,
    UserSerializer,
    WeeklyLogReviewSerializer,
    WeeklyLogSerializer,
)

User = get_user_model()


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if not user:
            return response.Response({"detail": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        return response.Response({"token": token.key, "user": UserSerializer(user).data})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return response.Response(UserSerializer(request.user).data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by("last_name", "first_name")
    serializer_class = UserSerializer

    def get_queryset(self):
        role = self.request.query_params.get("role")
        queryset = super().get_queryset()
        if role:
            queryset = queryset.filter(role=role)
        return queryset


class InternshipPlacementViewSet(viewsets.ModelViewSet):
    queryset = InternshipPlacement.objects.select_related("student", "workplace_supervisor", "academic_supervisor")
    serializer_class = InternshipPlacementSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if user.role == User.Role.STUDENT:
            return queryset.filter(student=user)
        if user.role == User.Role.WORKPLACE_SUPERVISOR:
            return queryset.filter(workplace_supervisor=user)
        if user.role == User.Role.ACADEMIC_SUPERVISOR:
            return queryset.filter(academic_supervisor=user)
        return queryset


class WeeklyLogViewSet(viewsets.ModelViewSet):
    queryset = WeeklyLog.objects.select_related("placement", "placement__student", "reviewed_by")
    serializer_class = WeeklyLogSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if user.role == User.Role.STUDENT:
            return queryset.filter(placement__student=user)
        if user.role == User.Role.WORKPLACE_SUPERVISOR:
            return queryset.filter(placement__workplace_supervisor=user)
        if user.role == User.Role.ACADEMIC_SUPERVISOR:
            return queryset.filter(placement__academic_supervisor=user)
        return queryset

    @decorators.action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        log = self.get_object()
        if log.placement.student != request.user:
            return response.Response({"detail": "Only the student can submit this log."}, status=status.HTTP_403_FORBIDDEN)
        try:
            log.submit()
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages)
        log.save(update_fields=["status", "submitted_at", "updated_at"])
        return response.Response(self.get_serializer(log).data)

    @decorators.action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsSupervisorOrAdmin])
    def review(self, request, pk=None):
        log = self.get_object()
        serializer = WeeklyLogReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            log.review(
                reviewer=request.user,
                status=serializer.validated_data["status"],
                comments=serializer.validated_data.get("comments", ""),
            )
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages)
        log.save(update_fields=["status", "supervisor_comments", "reviewed_by", "reviewed_at", "updated_at"])
        return response.Response(self.get_serializer(log).data)


class EvaluationCriteriaViewSet(viewsets.ModelViewSet):
    queryset = EvaluationCriteria.objects.all()
    serializer_class = EvaluationCriteriaSerializer


class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.select_related("placement", "evaluator", "criteria", "placement__student")
    serializer_class = EvaluationSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if user.role == User.Role.STUDENT:
            return queryset.filter(placement__student=user)
        if user.role == User.Role.WORKPLACE_SUPERVISOR:
            return queryset.filter(placement__workplace_supervisor=user)
        if user.role == User.Role.ACADEMIC_SUPERVISOR:
            return queryset.filter(placement__academic_supervisor=user)
        return queryset


class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        placements = self._placements_for_user(request.user)
        data = DashboardSerializer.build_queryset_summary(placements)
        return response.Response(DashboardSerializer(data).data)

    @decorators.action(detail=False, methods=["get"], url_path="scores")
    def scores(self, request):
        placements = self._placements_for_user(request.user).select_related("student")
        data = [ScoreBreakdownSerializer.build(placement) for placement in placements]
        return response.Response(ScoreBreakdownSerializer(data, many=True).data)

    @decorators.action(detail=False, methods=["get"], url_path="pending-reviews")
    def pending_reviews(self, request):
        logs = WeeklyLog.objects.filter(status=WeeklyLog.Status.SUBMITTED)
        user = request.user
        if user.role == User.Role.WORKPLACE_SUPERVISOR:
            logs = logs.filter(placement__workplace_supervisor=user)
        elif user.role == User.Role.ACADEMIC_SUPERVISOR:
            logs = logs.filter(placement__academic_supervisor=user)
        elif user.role == User.Role.STUDENT:
            logs = logs.none()
        serializer = WeeklyLogSerializer(logs.select_related("placement", "placement__student"), many=True)
        return response.Response(serializer.data)

    def _placements_for_user(self, user):
        placements = InternshipPlacement.objects.all()
        if user.role == User.Role.STUDENT:
            return placements.filter(student=user)
        if user.role == User.Role.WORKPLACE_SUPERVISOR:
            return placements.filter(workplace_supervisor=user)
        if user.role == User.Role.ACADEMIC_SUPERVISOR:
            return placements.filter(academic_supervisor=user)
        return placements
