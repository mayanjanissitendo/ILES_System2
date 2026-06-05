from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Evaluation, EvaluationCriteria, InternshipPlacement, WeeklyLog, WorkflowStatusHistory

User = get_user_model()


class IlesBusinessLogicTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username="student", password="pass", role=User.Role.STUDENT)
        self.workplace = User.objects.create_user(
            username="workplace",
            password="pass",
            role=User.Role.WORKPLACE_SUPERVISOR,
        )
        self.academic = User.objects.create_user(
            username="academic",
            password="pass",
            role=User.Role.ACADEMIC_SUPERVISOR,
        )
        self.placement = InternshipPlacement.objects.create(
            student=self.student,
            workplace_supervisor=self.workplace,
            academic_supervisor=self.academic,
            organization_name="Acme Ltd",
            organization_address="Kampala",
            position_title="Software Intern",
            start_date=timezone.localdate(),
            end_date=timezone.localdate() + timedelta(days=90),
        )

    def test_rejects_overlapping_placement(self):
        placement = InternshipPlacement(
            student=self.student,
            workplace_supervisor=self.workplace,
            academic_supervisor=self.academic,
            organization_name="Other Ltd",
            organization_address="Kampala",
            position_title="Intern",
            start_date=self.placement.start_date + timedelta(days=7),
            end_date=self.placement.end_date + timedelta(days=7),
        )
        with self.assertRaises(ValidationError):
            placement.clean()

    def test_weekly_log_submission_sets_timestamp(self):
        log = WeeklyLog.objects.create(
            placement=self.placement,
            week_number=1,
            week_start_date=self.placement.start_date,
            week_end_date=self.placement.start_date + timedelta(days=5),
            activities="Built API endpoints",
            hours_worked=Decimal("40.00"),
        )
        log.submit()
        self.assertEqual(log.status, WeeklyLog.Status.SUBMITTED)
        self.assertIsNotNone(log.submitted_at)

    def test_review_requires_submitted_log(self):
        log = WeeklyLog.objects.create(
            placement=self.placement,
            week_number=2,
            week_start_date=self.placement.start_date + timedelta(days=7),
            week_end_date=self.placement.start_date + timedelta(days=12),
            activities="Tested forms",
            hours_worked=Decimal("36.00"),
        )
        with self.assertRaises(ValidationError):
            log.review(self.workplace, WeeklyLog.Status.APPROVED, "Good")

    def test_evaluation_weighted_score(self):
        criteria = EvaluationCriteria.objects.create(name="Professionalism", category=EvaluationCriteria.Category.WORKPLACE)
        evaluation = Evaluation.objects.create(
            placement=self.placement,
            evaluator=self.workplace,
            evaluation_type=Evaluation.Type.WORKPLACE,
            criteria=criteria,
            score=Decimal("80.00"),
        )
        self.assertEqual(evaluation.weighted_score, Decimal("32.00"))

    def test_criteria_must_match_evaluation_type(self):
        criteria = EvaluationCriteria.objects.create(name="Report quality", category=EvaluationCriteria.Category.ACADEMIC)
        evaluation = Evaluation(
            placement=self.placement,
            evaluator=self.workplace,
            evaluation_type=Evaluation.Type.WORKPLACE,
            criteria=criteria,
            score=Decimal("70.00"),
        )
        with self.assertRaises(ValidationError):
            evaluation.full_clean()

    def test_weekly_log_dates_must_stay_inside_placement(self):
        log = WeeklyLog(
            placement=self.placement,
            week_number=3,
            week_start_date=self.placement.start_date - timedelta(days=7),
            week_end_date=self.placement.start_date - timedelta(days=1),
            activities="Before internship",
            hours_worked=Decimal("10.00"),
        )
        with self.assertRaises(ValidationError):
            log.clean()

    def test_workflow_status_history_records_transitions(self):
        log = WeeklyLog.objects.create(
            placement=self.placement,
            week_number=4,
            week_start_date=self.placement.start_date + timedelta(days=21),
            week_end_date=self.placement.start_date + timedelta(days=26),
            activities="Documented system flow",
            hours_worked=Decimal("38.00"),
        )
        previous = log.status
        log.submit()
        log.save()
        WorkflowStatusHistory.objects.create(
            weekly_log=log,
            from_status=previous,
            to_status=log.status,
            changed_by=self.student,
            comment="Submitted by student",
        )
        self.assertEqual(log.status_history.count(), 1)
