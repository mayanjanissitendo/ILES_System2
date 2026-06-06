from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    DashboardViewSet,
    EvaluationCriteriaViewSet,
    EvaluationViewSet,
    InternshipPlacementViewSet,
    LoginView,
    MeView,
    UserViewSet,
    WeeklyLogViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("placements", InternshipPlacementViewSet, basename="placements")
router.register("weekly-logs", WeeklyLogViewSet, basename="weekly-logs")
router.register("evaluation-criteria", EvaluationCriteriaViewSet, basename="evaluation-criteria")
router.register("evaluations", EvaluationViewSet, basename="evaluations")
router.register("dashboards", DashboardViewSet, basename="dashboards")

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
]

urlpatterns += router.urls
