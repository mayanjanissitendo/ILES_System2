from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student Intern"
        WORKPLACE_SUPERVISOR = "workplace_supervisor", "Workplace Supervisor"
        ACADEMIC_SUPERVISOR = "academic_supervisor", "Academic Supervisor"
        ADMIN = "admin", "Internship Administrator"

    role = models.CharField(max_length=32, choices=Role.choices)
    phone_number = models.CharField(max_length=20, blank=True)
    student_number = models.CharField(max_length=32, blank=True, unique=True, null=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"


class InternshipPlacement(models.Model):
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="placements",
        limit_choices_to={"role": CustomUser.Role.STUDENT},
    )
    workplace_supervisor = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="workplace_placements",
        limit_choices_to={"role": CustomUser.Role.WORKPLACE_SUPERVISOR},
    )
    academic_supervisor = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="academic_placements",
        limit_choices_to={"role": CustomUser.Role.ACADEMIC_SUPERVISOR},
    )
    organization_name = models.CharField(max_length=180)
    organization_address = models.TextField()
    department = models.CharField(max_length=120, blank=True)
    position_title = models.CharField(max_length=120)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "student__last_name"]
        constraints = [
            models.CheckConstraint(
                check=Q(end_date__gte=models.F("start_date")),
                name="placement_end_date_after_start_date",
            )
        ]

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date cannot be before start date."})

        overlap = InternshipPlacement.objects.filter(
            student=self.student,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
        )
        if self.pk:
            overlap = overlap.exclude(pk=self.pk)
        if overlap.exists():
            raise ValidationError("This student already has a placement in that date range.")

    def __str__(self):
        return f"{self.student} at {self.organization_name}"


class WeeklyLog(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        REVIEWED = "reviewed", "Reviewed"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    placement = models.ForeignKey(
        InternshipPlacement,
        on_delete=models.CASCADE,
        related_name="weekly_logs",
    )
    week_number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    week_start_date = models.DateField()
    week_end_date = models.DateField()
    activities = models.TextField()
    skills_learned = models.TextField(blank=True)
    challenges = models.TextField(blank=True)
    hours_worked = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("80.00"))],
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    supervisor_comments = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name="reviewed_logs",
        null=True,
        blank=True,
        limit_choices_to=Q(role=CustomUser.Role.WORKPLACE_SUPERVISOR)
        | Q(role=CustomUser.Role.ACADEMIC_SUPERVISOR),
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["placement", "week_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["placement", "week_number"],
                name="unique_weekly_log_per_placement_week",
            ),
            models.CheckConstraint(
                check=Q(week_end_date__gte=models.F("week_start_date")),
                name="weekly_log_end_date_after_start_date",
            ),
        ]

    @property
    def is_locked(self):
        return self.status in {self.Status.REVIEWED, self.Status.APPROVED}

    def clean(self):
        if self.week_end_date < self.week_start_date:
            raise ValidationError({"week_end_date": "Week end date cannot be before start date."})
        if self.placement_id:
            if self.week_start_date < self.placement.start_date or self.week_end_date > self.placement.end_date:
                raise ValidationError("Weekly log dates must be inside the placement period.")

    def submit(self):
        if self.status != self.Status.DRAFT:
            raise ValidationError("Only draft logs can be submitted.")
        if timezone.localdate() > self.week_end_date + timedelta(days=7):
            raise ValidationError("This weekly log is past the submission deadline.")
        self.status = self.Status.SUBMITTED
        self.submitted_at = timezone.now()

    def review(self, reviewer, status, comments=""):
        valid_statuses = {self.Status.REVIEWED, self.Status.APPROVED, self.Status.REJECTED}
        if self.status != self.Status.SUBMITTED:
            raise ValidationError("Only submitted logs can be reviewed.")
        if status not in valid_statuses:
            raise ValidationError("Invalid review status.")
        self.status = status
        self.supervisor_comments = comments
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()

    def __str__(self):
        return f"Week {self.week_number} - {self.placement.student}"


class WorkflowStatusHistory(models.Model):
    weekly_log = models.ForeignKey(
        WeeklyLog,
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    from_status = models.CharField(max_length=16, choices=WeeklyLog.Status.choices, blank=True)
    to_status = models.CharField(max_length=16, choices=WeeklyLog.Status.choices)
    changed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name="workflow_status_changes",
        null=True,
        blank=True,
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "workflow status history"

    def __str__(self):
        return f"{self.weekly_log} {self.from_status or 'new'} -> {self.to_status}"


class EvaluationCriteria(models.Model):
    class Category(models.TextChoices):
        WORKPLACE = "workplace", "Workplace"
        ACADEMIC = "academic", "Academic"
        LOGBOOK = "logbook", "Logbook"

    name = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField(blank=True)
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("100.00"),
        validators=[MinValueValidator(Decimal("1.00"))],
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "name"]
        constraints = [
            models.UniqueConstraint(fields=["category", "name"], name="unique_criteria_name_per_category")
        ]

    def __str__(self):
        return f"{self.name} ({self.category})"


class Evaluation(models.Model):
    class Type(models.TextChoices):
        WORKPLACE = "workplace", "Workplace Evaluation"
        ACADEMIC = "academic", "Academic Evaluation"
        LOGBOOK = "logbook", "Logbook Evaluation"
        FINAL = "final", "Final Score"

    placement = models.ForeignKey(
        InternshipPlacement,
        on_delete=models.CASCADE,
        related_name="evaluations",
    )
    evaluator = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="evaluations_given",
        limit_choices_to=Q(role=CustomUser.Role.WORKPLACE_SUPERVISOR)
        | Q(role=CustomUser.Role.ACADEMIC_SUPERVISOR)
        | Q(role=CustomUser.Role.ADMIN),
    )
    evaluation_type = models.CharField(max_length=16, choices=Type.choices)
    criteria = models.ForeignKey(
        EvaluationCriteria,
        on_delete=models.PROTECT,
        related_name="evaluations",
        null=True,
        blank=True,
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("100.00"))],
    )
    comments = models.TextField(blank=True)
    weighted_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["placement", "evaluation_type", "criteria"],
                name="unique_evaluation_per_type_and_criteria",
            )
        ]

    @staticmethod
    def weight_for(evaluation_type):
        return {
            Evaluation.Type.WORKPLACE: Decimal("0.40"),
            Evaluation.Type.ACADEMIC: Decimal("0.30"),
            Evaluation.Type.LOGBOOK: Decimal("0.30"),
            Evaluation.Type.FINAL: Decimal("1.00"),
        }[evaluation_type]

    def clean(self):
        if self.criteria and self.criteria.category != self.evaluation_type:
            raise ValidationError("Criteria category must match evaluation type.")
        if self.evaluation_type == self.Type.FINAL:
            raise ValidationError("Final scores are computed by the system, not submitted directly.")

    def save(self, *args, **kwargs):
        self.full_clean()
        self.weighted_score = (self.score * self.weight_for(self.evaluation_type)).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.placement.student} - {self.evaluation_type}: {self.score}"
