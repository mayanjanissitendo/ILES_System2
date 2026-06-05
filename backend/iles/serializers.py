from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import serializers

from .models import Evaluation, EvaluationCriteria, InternshipPlacement, WeeklyLog, WorkflowStatusHistory

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "full_name", "role", "phone_number", "student_number"]
        read_only_fields = ["id"]


class InternshipPlacementSerializer(serializers.ModelSerializer):
    student_detail = UserSerializer(source="student", read_only=True)
    workplace_supervisor_detail = UserSerializer(source="workplace_supervisor", read_only=True)
    academic_supervisor_detail = UserSerializer(source="academic_supervisor", read_only=True)

    class Meta:
        model = InternshipPlacement
        fields = [
            "id",
            "student",
            "student_detail",
            "workplace_supervisor",
            "workplace_supervisor_detail",
            "academic_supervisor",
            "academic_supervisor_detail",
            "organization_name",
            "organization_address",
            "department",
            "position_title",
            "start_date",
            "end_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        student = attrs.get("student", getattr(self.instance, "student", None))
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": "End date cannot be before start date."})
        if student and start_date and end_date:
            overlap = InternshipPlacement.objects.filter(
                student=student,
                start_date__lte=end_date,
                end_date__gte=start_date,
            )
            if self.instance:
                overlap = overlap.exclude(pk=self.instance.pk)
            if overlap.exists():
                raise serializers.ValidationError("This student already has a placement in that date range.")
        return attrs


class WeeklyLogSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="placement.student.get_full_name", read_only=True)
    organization_name = serializers.CharField(source="placement.organization_name", read_only=True)
    is_locked = serializers.BooleanField(read_only=True)

    class Meta:
        model = WeeklyLog
        fields = [
            "id",
            "placement",
            "student_name",
            "organization_name",
            "week_number",
            "week_start_date",
            "week_end_date",
            "activities",
            "skills_learned",
            "challenges",
            "hours_worked",
            "status",
            "supervisor_comments",
            "reviewed_by",
            "reviewed_at",
            "submitted_at",
            "is_locked",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reviewed_by", "reviewed_at", "submitted_at", "created_at", "updated_at"]

    def validate(self, attrs):
        if self.instance and self.instance.is_locked:
            raise serializers.ValidationError("Approved or reviewed logs cannot be edited.")
        placement = attrs.get("placement", getattr(self.instance, "placement", None))
        week_start_date = attrs.get("week_start_date", getattr(self.instance, "week_start_date", None))
        week_end_date = attrs.get("week_end_date", getattr(self.instance, "week_end_date", None))
        if week_start_date and week_end_date and week_end_date < week_start_date:
            raise serializers.ValidationError({"week_end_date": "Week end date cannot be before start date."})
        if placement and week_start_date and week_end_date:
            if week_start_date < placement.start_date or week_end_date > placement.end_date:
                raise serializers.ValidationError("Weekly log dates must be inside the placement period.")
        return attrs


class WeeklyLogReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[WeeklyLog.Status.REVIEWED, WeeklyLog.Status.APPROVED, WeeklyLog.Status.REJECTED])
    comments = serializers.CharField(required=False, allow_blank=True)


class WorkflowStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source="changed_by.get_full_name", read_only=True)

    class Meta:
        model = WorkflowStatusHistory
        fields = ["id", "weekly_log", "from_status", "to_status", "changed_by", "changed_by_name", "comment", "created_at"]
        read_only_fields = ["id", "created_at"]


class EvaluationCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationCriteria
        fields = ["id", "name", "category", "description", "max_score", "is_active"]
        read_only_fields = ["id"]


class EvaluationSerializer(serializers.ModelSerializer):
    evaluator_detail = UserSerializer(source="evaluator", read_only=True)
    weighted_score = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Evaluation
        fields = [
            "id",
            "placement",
            "evaluator",
            "evaluator_detail",
            "evaluation_type",
            "criteria",
            "score",
            "comments",
            "weighted_score",
            "submitted_at",
        ]
        read_only_fields = ["id", "weighted_score", "submitted_at"]

    def validate(self, attrs):
        if attrs.get("evaluation_type") == Evaluation.Type.FINAL:
            raise serializers.ValidationError("Final score is calculated automatically.")
        return attrs


class ScoreBreakdownSerializer(serializers.Serializer):
    placement_id = serializers.IntegerField()
    student = UserSerializer()
    workplace_average = serializers.DecimalField(max_digits=5, decimal_places=2)
    academic_average = serializers.DecimalField(max_digits=5, decimal_places=2)
    logbook_average = serializers.DecimalField(max_digits=5, decimal_places=2)
    final_score = serializers.DecimalField(max_digits=5, decimal_places=2)

    @staticmethod
    def build(placement):
        averages = placement.evaluations.values("evaluation_type").annotate(avg_score=Avg("score"))
        by_type = {item["evaluation_type"]: item["avg_score"] or Decimal("0.00") for item in averages}
        workplace = by_type.get(Evaluation.Type.WORKPLACE, Decimal("0.00"))
        academic = by_type.get(Evaluation.Type.ACADEMIC, Decimal("0.00"))
        logbook = by_type.get(Evaluation.Type.LOGBOOK, Decimal("0.00"))
        final = (workplace * Decimal("0.40")) + (academic * Decimal("0.30")) + (logbook * Decimal("0.30"))
        return {
            "placement_id": placement.id,
            "student": placement.student,
            "workplace_average": workplace,
            "academic_average": academic,
            "logbook_average": logbook,
            "final_score": final.quantize(Decimal("0.01")),
        }


class DashboardSerializer(serializers.Serializer):
    placements = serializers.IntegerField()
    active_placements = serializers.IntegerField()
    submitted_logs = serializers.IntegerField()
    pending_reviews = serializers.IntegerField()
    approved_logs = serializers.IntegerField()
    average_score = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)

    @staticmethod
    def build_queryset_summary(placements):
        logs = WeeklyLog.objects.filter(placement__in=placements)
        evaluations = Evaluation.objects.filter(placement__in=placements)
        return {
            "placements": placements.count(),
            "active_placements": placements.filter(is_active=True).count(),
            "submitted_logs": logs.filter(status=WeeklyLog.Status.SUBMITTED).count(),
            "pending_reviews": logs.filter(status=WeeklyLog.Status.SUBMITTED).count(),
            "approved_logs": logs.filter(status=WeeklyLog.Status.APPROVED).count(),
            "average_score": evaluations.aggregate(avg=Avg("score"))["avg"],
        }
