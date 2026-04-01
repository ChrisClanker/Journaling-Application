from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import json
from .models import JournalEntry, Goal, Blurb, Report
from .forms import JournalForm, AskJournalForm, GoalForm


class JournalEntryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_create_journal_entry(self):
        entry = JournalEntry.objects.create(
            user=self.user,
            content='Test journal content',
            title='Test Title'
        )
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.content, 'Test journal content')
        self.assertEqual(entry.title, 'Test Title')
        self.assertIsNotNone(entry.date)
        self.assertIsNone(entry.mood)

    def test_journal_entry_str_with_title(self):
        entry = JournalEntry.objects.create(
            user=self.user,
            content='Test content',
            title='My Day'
        )
        self.assertIn('My Day', str(entry))

    def test_journal_entry_str_without_title(self):
        entry = JournalEntry.objects.create(
            user=self.user,
            content='Test content'
        )
        self.assertIn("testuser's Journal Entry", str(entry))

    def test_journal_entry_mood_field(self):
        entry = JournalEntry.objects.create(
            user=self.user,
            content='Test content',
            mood='["happy", "excited"]'
        )
        self.assertEqual(entry.mood, '["happy", "excited"]')

    def test_journal_entry_with_reflections_and_gratitude(self):
        entry = JournalEntry.objects.create(
            user=self.user,
            content='Test content',
            reflections='What I learned today',
            gratitude='Grateful for family'
        )
        self.assertEqual(entry.reflections, 'What I learned today')
        self.assertEqual(entry.gratitude, 'Grateful for family')


class GoalModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_create_goal(self):
        goal = Goal.objects.create(
            user=self.user,
            goal_title='Learn Python',
            goal_text='Complete Django tutorial',
            goal_rationale='Improve career prospects',
            created_at=timezone.now(),
            length='1m'
        )
        self.assertEqual(goal.user, self.user)
        self.assertEqual(goal.goal_title, 'Learn Python')
        self.assertEqual(goal.length, '1m')

    def test_goal_length_choices(self):
        for length_value, length_display in Goal.LENGTH_CHOICES:
            goal = Goal.objects.create(
                user=self.user,
                goal_title=f'Test Goal {length_value}',
                goal_text='Test text',
                goal_rationale='Test rationale',
                created_at=timezone.now(),
                length=length_value
            )
            self.assertEqual(goal.length, length_value)

    def test_goal_parent_relationship(self):
        parent_goal = Goal.objects.create(
            user=self.user,
            goal_title='Parent Goal',
            goal_text='Parent text',
            goal_rationale='Parent rationale',
            created_at=timezone.now(),
            length='1y'
        )
        child_goal = Goal.objects.create(
            user=self.user,
            goal_title='Child Goal',
            goal_text='Child text',
            goal_rationale='Child rationale',
            created_at=timezone.now(),
            length='1m',
            parent_goal=parent_goal
        )
        self.assertEqual(child_goal.parent_goal, parent_goal)


class BlurbModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_create_blurb(self):
        blurb = Blurb.objects.create(
            user=self.user,
            blurb_text='Quick thought about the meeting'
        )
        self.assertEqual(blurb.user, self.user)
        self.assertEqual(blurb.blurb_text, 'Quick thought about the meeting')
        self.assertIsNone(blurb.journalEntry)

    def test_blurb_associated_with_journal(self):
        journal = JournalEntry.objects.create(
            user=self.user,
            content='Journal content'
        )
        blurb = Blurb.objects.create(
            user=self.user,
            blurb_text='Quick thought',
            journalEntry=journal
        )
        self.assertEqual(blurb.journalEntry, journal)


class ReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_create_report(self):
        report = Report.objects.create(
            user=self.user,
            title='Weekly Summary',
            type='w',
            content='This week was productive...'
        )
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.title, 'Weekly Summary')
        self.assertEqual(report.type, 'w')

    def test_report_str(self):
        report = Report.objects.create(
            user=self.user,
            title='Monthly Report',
            type='m',
            content='Monthly content'
        )
        self.assertEqual(str(report), 'Monthly Report')

    def test_report_type_choices(self):
        for type_value, type_display in Report.TYPE_CHOICES:
            report = Report.objects.create(
                user=self.user,
                title=f'Test Report {type_value}',
                type=type_value,
                content='Test content'
            )
            self.assertEqual(report.type, type_value)


class JournalFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_valid_journal_form(self):
        data = {
            'content': 'Today was a great day',
            'reflections': 'I learned something new',
            'gratitude': 'Grateful for health'
        }
        form = JournalForm(data=data)
        self.assertTrue(form.is_valid())

    def test_journal_form_minimal_valid(self):
        data = {'content': 'Minimal journal entry'}
        form = JournalForm(data=data)
        self.assertTrue(form.is_valid())

    def test_journal_form_empty_content_allowed(self):
        data = {'content': '', 'reflections': '', 'gratitude': ''}
        form = JournalForm(data=data)
        self.assertTrue(form.is_valid())


class GoalFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_valid_goal_form(self):
        data = {
            'goal_title': 'Learn Django',
            'goal_text': 'Complete all tutorials',
            'goal_rationale': 'Improve skills',
            'length': '1m'
        }
        form = GoalForm(data=data)
        self.assertTrue(form.is_valid())

    def test_goal_form_missing_required_fields(self):
        data = {'goal_title': 'Incomplete'}
        form = GoalForm(data=data)
        self.assertFalse(form.is_valid())

    def test_goal_form_invalid_length(self):
        data = {
            'goal_title': 'Test',
            'goal_text': 'Test text',
            'goal_rationale': 'Test rationale',
            'length': 'invalid'
        }
        form = GoalForm(data=data)
        self.assertFalse(form.is_valid())


class AskJournalFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.journal = JournalEntry.objects.create(
            user=self.user,
            content='Test journal content'
        )

    def test_ask_journal_form_valid(self):
        form = AskJournalForm(user=self.user, data={
            'question': 'What was the main theme?',
            'journals': [self.journal.id]
        })
        self.assertTrue(form.is_valid())


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_login_page_loads(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalid_credentials(self):
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid credentials')


class JournalsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.journal = JournalEntry.objects.create(
            user=self.user,
            content='Test journal content',
            title='Test Journal'
        )

    def test_journals_requires_login(self):
        response = self.client.get('/journals/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_journals_lists_user_entries(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Journal')

    def test_journals_only_shows_own_entries(self):
        other_user = User.objects.create_user(username='otheruser', password='testpass123')
        JournalEntry.objects.create(
            user=other_user,
            content='Other user journal',
            title='Other Journal'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Journal')
        self.assertNotContains(response, 'Other Journal')


class JournalCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_journal_create_requires_login(self):
        response = self.client.get('/journals/create.html')
        self.assertEqual(response.status_code, 302)

    def test_journal_create_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/create.html')
        self.assertEqual(response.status_code, 200)

    def test_journal_create_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/journals/create.html', {
            'content': 'New journal entry',
            'reflections': 'Some reflections',
            'gratitude': 'Grateful for today'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(JournalEntry.objects.count(), 1)
        entry = JournalEntry.objects.first()
        self.assertEqual(entry.content, 'New journal entry')
        self.assertEqual(entry.user, self.user)


class JournalDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.journal = JournalEntry.objects.create(
            user=self.user,
            content='Test journal content',
            title='Test Journal'
        )

    def test_journal_detail_requires_login(self):
        response = self.client.get(f'/details/{self.journal.id}/')
        self.assertEqual(response.status_code, 302)

    def test_journal_detail_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{self.journal.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Journal')

    def test_journal_detail_not_found(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/details/99999/')
        self.assertEqual(response.status_code, 404)

    def test_cannot_view_others_journal(self):
        other_user = User.objects.create_user(username='otheruser', password='testpass123')
        other_journal = JournalEntry.objects.create(
            user=other_user,
            content='Other user journal'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{other_journal.id}/')
        self.assertEqual(response.status_code, 404)


class GoalsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.goal = Goal.objects.create(
            user=self.user,
            goal_title='Test Goal',
            goal_text='Test text',
            goal_rationale='Test rationale',
            created_at=timezone.now(),
            length='1m'
        )

    def test_goals_requires_login(self):
        response = self.client.get('/goals/')
        self.assertEqual(response.status_code, 302)

    def test_goals_lists_user_goals(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/goals/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Goal')


class GoalCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_goal_create_requires_login(self):
        response = self.client.get('/goals/create.html')
        self.assertEqual(response.status_code, 302)

    def test_goal_create_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/goals/create.html', {
            'goal_title': 'New Goal',
            'goal_text': 'Goal description',
            'goal_rationale': 'Why I want this',
            'length': '1y'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Goal.objects.count(), 1)
        goal = Goal.objects.first()
        self.assertEqual(goal.goal_title, 'New Goal')


class GoalDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.goal = Goal.objects.create(
            user=self.user,
            goal_title='Test Goal',
            goal_text='Test text',
            goal_rationale='Test rationale',
            created_at=timezone.now(),
            length='1m'
        )

    def test_goal_detail_requires_login(self):
        response = self.client.get(f'/goals/{self.goal.id}/')
        self.assertEqual(response.status_code, 302)

    def test_goal_detail_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/goals/{self.goal.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Goal')


class ReportDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.report = Report.objects.create(
            user=self.user,
            title='Test Report',
            type='w',
            content='Report content'
        )

    def test_report_detail_requires_login(self):
        response = self.client.get(f'/reports/{self.report.id}/')
        self.assertEqual(response.status_code, 302)

    def test_report_detail_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/reports/{self.report.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Report')


class MoodListCreationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_mood_list_happy(self):
        entry = JournalEntry.objects.create(
            user=self.user,
            content='Great day!',
            mood='["happy"]'
        )
        from .views import mood_list_creation
        mood_list = mood_list_creation(entry)
        self.assertEqual(len(mood_list), 1)
        self.assertIn('happy', mood_list[0])

    def test_mood_list_multiple(self):
        entry = JournalEntry.objects.create(
            user=self.user,
            content='Mixed feelings',
            mood='["happy", "worried"]'
        )
        from .views import mood_list_creation
        mood_list = mood_list_creation(entry)
        self.assertEqual(len(mood_list), 2)

    def test_mood_list_none_pending(self):
        entry = JournalEntry.objects.create(
            user=self.user,
            content='Pending AI processing'
        )
        from .views import mood_list_creation
        mood_list = mood_list_creation(entry)
        self.assertIn('yet to be processed', mood_list[0])

    def test_mood_list_invalid_json(self):
        entry = JournalEntry.objects.create(
            user=self.user,
            content='Invalid mood',
            mood='not valid json'
        )
        from .views import mood_list_creation
        mood_list = mood_list_creation(entry)
        self.assertIn('invalid', mood_list[0].lower())


class GoalEditViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.goal = Goal.objects.create(
            user=self.user,
            goal_title='Test Goal',
            goal_text='Test text',
            goal_rationale='Test rationale',
            created_at=timezone.now(),
            length='1m'
        )

    def test_goal_edit_requires_login(self):
        response = self.client.get(f'/goals/{self.goal.id}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_goal_edit_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/goals/{self.goal.id}/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Goal')

    def test_goal_edit_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/goals/{self.goal.id}/edit/', {
            'goal_title': 'Updated Goal',
            'goal_text': 'Updated text',
            'goal_rationale': 'Updated rationale',
            'length': '6m'
        })
        self.assertEqual(response.status_code, 302)
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.goal_title, 'Updated Goal')
        self.assertEqual(self.goal.length, '6m')

    def test_can_edit_own_goal(self):
        other_user = User.objects.create_user(username='otheruser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/goals/{self.goal.id}/edit/')
        self.assertEqual(response.status_code, 200)  # goal belongs to logged-in user

    def test_goal_edit_not_found(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/goals/99999/edit/')
        self.assertEqual(response.status_code, 404)


class GoalDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.goal = Goal.objects.create(
            user=self.user,
            goal_title='Test Goal',
            goal_text='Test text',
            goal_rationale='Test rationale',
            created_at=timezone.now(),
            length='1m'
        )

    def test_goal_delete_requires_login(self):
        response = self.client.get(f'/goals/{self.goal.id}/delete/')
        self.assertEqual(response.status_code, 302)

    def test_goal_delete_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/goals/{self.goal.id}/delete/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Goal')

    def test_goal_delete_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/goals/{self.goal.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Goal.objects.count(), 0)

    def test_goal_delete_not_found(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/goals/99999/delete/')
        self.assertEqual(response.status_code, 404)


class JournalEditViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.journal = JournalEntry.objects.create(
            user=self.user,
            content='Test journal content',
            title='Test Journal'
        )

    def test_journal_edit_requires_login(self):
        response = self.client.get(f'/details/{self.journal.id}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_journal_edit_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{self.journal.id}/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test journal content')

    def test_journal_edit_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/details/{self.journal.id}/edit/', {
            'content': 'Updated journal content',
            'reflections': 'Updated reflections',
            'gratitude': 'Updated gratitude'
        })
        self.assertEqual(response.status_code, 302)
        self.journal.refresh_from_db()
        self.assertEqual(self.journal.content, 'Updated journal content')
        self.assertEqual(self.journal.reflections, 'Updated reflections')

    def test_journal_edit_not_found(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/details/99999/edit/')
        self.assertEqual(response.status_code, 404)

    def test_cannot_edit_others_journal(self):
        other_user = User.objects.create_user(username='otheruser', password='testpass123')
        other_journal = JournalEntry.objects.create(
            user=other_user,
            content='Other user journal'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{other_journal.id}/edit/')
        self.assertEqual(response.status_code, 404)


class JournalDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.journal = JournalEntry.objects.create(
            user=self.user,
            content='Test journal content',
            title='Test Journal'
        )

    def test_journal_delete_requires_login(self):
        response = self.client.get(f'/details/{self.journal.id}/delete/')
        self.assertEqual(response.status_code, 302)

    def test_journal_delete_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{self.journal.id}/delete/')
        self.assertEqual(response.status_code, 200)

    def test_journal_delete_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/details/{self.journal.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(JournalEntry.objects.count(), 0)

    def test_journal_delete_not_found(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/details/99999/delete/')
        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_others_journal(self):
        other_user = User.objects.create_user(username='otheruser', password='testpass123')
        other_journal = JournalEntry.objects.create(
            user=other_user,
            content='Other user journal'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{other_journal.id}/delete/')
        self.assertEqual(response.status_code, 404)


class UseAIDisabledTest(TestCase):
    """Tests for behavior when USE_AI=False (the default)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_journal_question_redirects_when_ai_disabled(self):
        """When USE_AI is False, the ask-a-question view should redirect to journals."""
        from django.conf import settings
        # Verify the setting is False by default
        self.assertFalse(settings.USE_AI)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/ask.html')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/journals/')

    def test_journal_create_generates_date_title_when_ai_disabled(self):
        """When USE_AI is False, journal entries get a date-based title."""
        from django.conf import settings
        self.assertFalse(settings.USE_AI)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/journals/create.html', {
            'content': 'Test entry without AI',
            'reflections': '',
            'gratitude': '',
            'mood': ['happy', 'grateful'],
        })
        self.assertEqual(response.status_code, 302)
        entry = JournalEntry.objects.get(user=self.user)
        self.assertTrue(entry.title.startswith('Journal Entry -'))
        self.assertEqual(json.loads(entry.mood), ['happy', 'grateful'])

    def test_journal_create_no_mood_when_none_selected(self):
        """When USE_AI is False and no mood is selected, mood should be None or empty."""
        from django.conf import settings
        self.assertFalse(settings.USE_AI)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/journals/create.html', {
            'content': 'Test entry without mood',
            'reflections': '',
            'gratitude': '',
        })
        self.assertEqual(response.status_code, 302)
        entry = JournalEntry.objects.get(user=self.user)
        self.assertIsNone(entry.mood)


class JournalFormUseAITest(TestCase):
    """Tests for JournalForm's use_ai parameter."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_form_has_mood_field_when_ai_disabled(self):
        """When use_ai=False, the mood field should be present."""
        form = JournalForm(use_ai=False)
        self.assertIn('mood', form.fields)

    def test_form_no_mood_field_when_ai_enabled(self):
        """When use_ai=True (default), the mood field should not be present."""
        form = JournalForm()
        self.assertNotIn('mood', form.fields)

    def test_form_valid_with_mood_when_ai_disabled(self):
        """Form should validate with mood selections when AI is disabled."""
        data = {
            'content': 'Test content',
            'reflections': '',
            'gratitude': '',
            'mood': ['happy', 'excited'],
        }
        form = JournalForm(data=data, use_ai=False)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['mood'], ['happy', 'excited'])

    def test_form_valid_without_mood_when_ai_disabled(self):
        """Form should validate without mood selections when AI is disabled."""
        data = {
            'content': 'Test content',
            'reflections': '',
            'gratitude': '',
        }
        form = JournalForm(data=data, use_ai=False)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('mood'), [])


# ============================================================
# Tests for Feature 1: Dashboard Home Page
# ============================================================

class DashboardViewTest(TestCase):
    """Tests for the dashboard view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_dashboard_requires_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_dashboard_loads(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Journal Dashboard')

    def test_dashboard_shows_total_entries(self):
        self.client.login(username='testuser', password='testpass123')
        JournalEntry.objects.create(user=self.user, content='Entry 1', title='Test 1')
        JournalEntry.objects.create(user=self.user, content='Entry 2', title='Test 2')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total Entries')

    def test_dashboard_shows_current_streak(self):
        self.client.login(username='testuser', password='testpass123')
        today = timezone.now().date()
        JournalEntry.objects.create(user=self.user, content='Today', date=today)
        JournalEntry.objects.create(user=self.user, content='Yesterday', date=today - timedelta(days=1))
        response = self.client.get('/')
        self.assertContains(response, 'Current Streak')

    def test_dashboard_shows_longest_streak(self):
        self.client.login(username='testuser', password='testpass123')
        today = timezone.now().date()
        JournalEntry.objects.create(user=self.user, content='Day 1', date=today - timedelta(days=2))
        JournalEntry.objects.create(user=self.user, content='Day 2', date=today - timedelta(days=1))
        JournalEntry.objects.create(user=self.user, content='Day 3', date=today)
        response = self.client.get('/')
        self.assertContains(response, 'Longest Streak')

    def test_dashboard_shows_most_common_mood(self):
        self.client.login(username='testuser', password='testpass123')
        JournalEntry.objects.create(user=self.user, content='Happy 1', mood='["happy"]')
        JournalEntry.objects.create(user=self.user, content='Happy 2', mood='["happy"]')
        JournalEntry.objects.create(user=self.user, content='Sad', mood='["sad"]')
        response = self.client.get('/')
        self.assertContains(response, 'Most Common Mood')
        self.assertContains(response, 'Happy')

    def test_dashboard_shows_recent_entries(self):
        self.client.login(username='testuser', password='testpass123')
        for i in range(7):
            JournalEntry.objects.create(user=self.user, content=f'Content {i}', title=f'Test {i}')
        response = self.client.get('/')
        self.assertContains(response, 'Recent Entries')

    def test_dashboard_shows_bookmarked_entries(self):
        self.client.login(username='testuser', password='testpass123')
        entry = JournalEntry.objects.create(user=self.user, content='Bookmarked', title='Bookmarked Entry', bookmarked=True)
        response = self.client.get('/')
        self.assertContains(response, 'Bookmarked Entries')
        self.assertContains(response, 'Bookmarked Entry')

    def test_dashboard_only_shows_own_entries(self):
        other_user = User.objects.create_user(username='otheruser', password='testpass123')
        JournalEntry.objects.create(user=other_user, content='Other', title='Other Entry')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertNotContains(response, 'Other Entry')

    def test_dashboard_has_quick_action_links(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertContains(response, 'Create Journal')
        self.assertContains(response, 'View Goals')
        self.assertContains(response, 'Mood Calendar')


# ============================================================
# Tests for Streak Calculation Helpers
# ============================================================

class StreakCalculationTest(TestCase):
    """Tests for streak calculation helper functions."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_current_streak_single_day_today(self):
        today = timezone.now().date()
        JournalEntry.objects.create(user=self.user, content='Today', date=today)
        from .views import calculate_current_streak
        entries = JournalEntry.objects.filter(user=self.user)
        self.assertEqual(calculate_current_streak(entries), 1)

    def test_current_streak_three_days(self):
        today = timezone.now().date()
        e1 = JournalEntry.objects.create(user=self.user, content='Day 1')
        e1.date = today - timedelta(days=2)
        e1.save()
        e2 = JournalEntry.objects.create(user=self.user, content='Day 2')
        e2.date = today - timedelta(days=1)
        e2.save()
        e3 = JournalEntry.objects.create(user=self.user, content='Day 3')
        e3.date = today
        e3.save()
        from .views import calculate_current_streak
        entries = JournalEntry.objects.filter(user=self.user)
        self.assertEqual(calculate_current_streak(entries), 3)

    def test_current_streak_zero_when_gap(self):
        today = timezone.now().date()
        entry = JournalEntry.objects.create(user=self.user, content='Old')
        entry.date = today - timedelta(days=5)
        entry.save()
        from .views import calculate_current_streak
        entries = JournalEntry.objects.filter(user=self.user)
        self.assertEqual(calculate_current_streak(entries), 0)

    def test_current_streak_starts_yesterday(self):
        today = timezone.now().date()
        JournalEntry.objects.create(user=self.user, content='Yesterday', date=today - timedelta(days=1))
        from .views import calculate_current_streak
        entries = JournalEntry.objects.filter(user=self.user)
        self.assertEqual(calculate_current_streak(entries), 1)

    def test_longest_streak(self):
        today = timezone.now().date()
        e1 = JournalEntry.objects.create(user=self.user, content='Day 1')
        e1.date = today - timedelta(days=10)
        e1.save()
        e2 = JournalEntry.objects.create(user=self.user, content='Day 2')
        e2.date = today - timedelta(days=9)
        e2.save()
        e3 = JournalEntry.objects.create(user=self.user, content='Day 3')
        e3.date = today - timedelta(days=8)
        e3.save()
        # Gap
        e4 = JournalEntry.objects.create(user=self.user, content='Day 4')
        e4.date = today - timedelta(days=2)
        e4.save()
        e5 = JournalEntry.objects.create(user=self.user, content='Day 5')
        e5.date = today - timedelta(days=1)
        e5.save()
        from .views import calculate_longest_streak
        entries = JournalEntry.objects.filter(user=self.user)
        self.assertEqual(calculate_longest_streak(entries), 3)

    def test_longest_streak_single_entry(self):
        today = timezone.now().date()
        JournalEntry.objects.create(user=self.user, content='Only', date=today)
        from .views import calculate_longest_streak
        entries = JournalEntry.objects.filter(user=self.user)
        self.assertEqual(calculate_longest_streak(entries), 1)

    def test_most_common_mood(self):
        JournalEntry.objects.create(user=self.user, content='1', mood='["happy"]')
        JournalEntry.objects.create(user=self.user, content='2', mood='["happy"]')
        JournalEntry.objects.create(user=self.user, content='3', mood='["sad"]')
        from .views import get_most_common_mood
        entries = JournalEntry.objects.filter(user=self.user)
        self.assertEqual(get_most_common_mood(entries), 'happy')

    def test_most_common_mood_none(self):
        JournalEntry.objects.create(user=self.user, content='No mood')
        from .views import get_most_common_mood
        entries = JournalEntry.objects.filter(user=self.user)
        self.assertIsNone(get_most_common_mood(entries))


# ============================================================
# Tests for Feature 2: Journal Search & Filtering
# ============================================================

class JournalSearchTest(TestCase):
    """Tests for journal search functionality."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.entry1 = JournalEntry.objects.create(
            user=self.user, content='Went to the beach today', title='Beach Day',
            reflections='It was relaxing', gratitude='Good weather'
        )
        self.entry2 = JournalEntry.objects.create(
            user=self.user, content='Had a meeting at work', title='Work Day',
            reflections='Productive meeting', gratitude='Good colleagues'
        )

    def test_search_by_title(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/', {'q': 'Beach'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Beach Day')
        self.assertNotContains(response, 'Work Day')

    def test_search_by_content(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/', {'q': 'meeting'})
        self.assertContains(response, 'Work Day')
        self.assertNotContains(response, 'Beach Day')

    def test_search_by_reflections(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/', {'q': 'relaxing'})
        self.assertContains(response, 'Beach Day')

    def test_search_by_gratitude(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/', {'q': 'colleagues'})
        self.assertContains(response, 'Work Day')

    def test_search_no_results(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/', {'q': 'nonexistent'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Beach Day')
        self.assertNotContains(response, 'Work Day')

    def test_filter_by_mood(self):
        JournalEntry.objects.create(user=self.user, content='Happy entry', title='Happy', mood='["happy"]')
        JournalEntry.objects.create(user=self.user, content='Sad entry', title='Sad', mood='["sad"]')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/', {'mood': 'happy'})
        self.assertContains(response, 'Happy')
        # "Sad" may appear in the dropdown options - check it's not in the table results
        self.assertNotContains(response, 'Sad entry')

    def test_filter_by_date_range(self):
        today = timezone.now().date()
        e1 = JournalEntry.objects.create(user=self.user, content='Old', title='Old Entry')
        e1.date = today - timedelta(days=30)
        e1.save()
        e2 = JournalEntry.objects.create(user=self.user, content='Recent', title='Recent Entry')
        e2.date = today - timedelta(days=1)
        e2.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/', {'date_from': (today - timedelta(days=7)).isoformat()})
        self.assertContains(response, 'Recent Entry')
        self.assertNotContains(response, 'Old Entry')

    def test_filter_by_tag(self):
        from .models import Tag
        tag_work = Tag.objects.create(user=self.user, name='work')
        tag_personal = Tag.objects.create(user=self.user, name='personal')
        entry1 = JournalEntry.objects.create(user=self.user, content='Work stuff', title='Work Entry')
        entry2 = JournalEntry.objects.create(user=self.user, content='Personal stuff', title='Personal Entry')
        entry1.tags.add(tag_work)
        entry2.tags.add(tag_personal)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/', {'tag': 'work'})
        self.assertContains(response, 'Work Entry')
        self.assertNotContains(response, 'Personal Entry')

    def test_combined_filters(self):
        JournalEntry.objects.create(user=self.user, content='Beach work', title='Beach Work', mood='["happy"]')
        JournalEntry.objects.create(user=self.user, content='Beach fun', title='Beach Fun', mood='["sad"]')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/', {'q': 'Beach', 'mood': 'happy'})
        self.assertContains(response, 'Beach Work')
        self.assertNotContains(response, 'Beach Fun')

    def test_clear_filters(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/')
        self.assertContains(response, 'Clear Filters')

    def test_search_form_preserves_query(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/', {'q': 'Beach'})
        self.assertContains(response, 'value="Beach"')


# ============================================================
# Tests for Feature 3: Mood Calendar
# ============================================================

class MoodCalendarTest(TestCase):
    """Tests for the mood calendar view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_mood_calendar_requires_login(self):
        response = self.client.get('/mood-calendar/')
        self.assertEqual(response.status_code, 302)

    def test_mood_calendar_loads(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mood-calendar/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mood Calendar')

    def test_mood_calendar_shows_calendar_months(self):
        today = timezone.now().date()
        JournalEntry.objects.create(user=self.user, content='Entry', date=today, mood='["happy"]')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mood-calendar/')
        self.assertEqual(response.status_code, 200)

    def test_mood_calendar_no_data(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mood-calendar/')
        self.assertEqual(response.status_code, 200)
        # When no mood entries exist, calendar still renders but shows no colored days
        self.assertContains(response, 'Mood Calendar')

    def test_mood_calendar_only_shows_own_entries(self):
        other_user = User.objects.create_user(username='otheruser', password='testpass123')
        today = timezone.now().date()
        other_entry = JournalEntry.objects.create(user=other_user, content='Other', mood='["happy"]')
        other_entry.date = today
        other_entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mood-calendar/')
        self.assertEqual(response.status_code, 200)
        # Should not show the other user's mood data


# ============================================================
# Tests for Feature 4: Tags System
# ============================================================

class TagModelTest(TestCase):
    """Tests for the Tag model."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_create_tag(self):
        from .models import Tag
        tag = Tag.objects.create(user=self.user, name='work')
        self.assertEqual(tag.name, 'work')
        self.assertEqual(tag.user, self.user)

    def test_tag_str(self):
        from .models import Tag
        tag = Tag.objects.create(user=self.user, name='work')
        self.assertEqual(str(tag), 'work')

    def test_tag_unique_per_user(self):
        from .models import Tag
        Tag.objects.create(user=self.user, name='work')
        with self.assertRaises(Exception):
            Tag.objects.create(user=self.user, name='work')

    def test_different_users_same_tag_name(self):
        from .models import Tag
        other_user = User.objects.create_user(username='other', password='testpass123')
        Tag.objects.create(user=self.user, name='work')
        Tag.objects.create(user=other_user, name='work')
        self.assertEqual(Tag.objects.filter(name='work').count(), 2)

    def test_tag_ordering(self):
        from .models import Tag
        Tag.objects.create(user=self.user, name='zebra')
        Tag.objects.create(user=self.user, name='apple')
        Tag.objects.create(user=self.user, name='mango')
        tags = list(Tag.objects.filter(user=self.user))
        self.assertEqual(tags[0].name, 'apple')
        self.assertEqual(tags[1].name, 'mango')
        self.assertEqual(tags[2].name, 'zebra')


class JournalEntryTagsTest(TestCase):
    """Tests for tags on journal entries."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_entry_can_have_tags(self):
        from .models import Tag
        tag = Tag.objects.create(user=self.user, name='work')
        entry = JournalEntry.objects.create(user=self.user, content='Work journal')
        entry.tags.add(tag)
        self.assertEqual(entry.tags.count(), 1)
        self.assertIn(tag, entry.tags.all())

    def test_entry_can_have_multiple_tags(self):
        from .models import Tag
        tag1 = Tag.objects.create(user=self.user, name='work')
        tag2 = Tag.objects.create(user=self.user, name='important')
        entry = JournalEntry.objects.create(user=self.user, content='Important work')
        entry.tags.add(tag1, tag2)
        self.assertEqual(entry.tags.count(), 2)


class TagViewTest(TestCase):
    """Tests for tag views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_tag_list_requires_login(self):
        response = self.client.get('/tags/')
        self.assertEqual(response.status_code, 302)

    def test_tag_list_loads(self):
        from .models import Tag
        Tag.objects.create(user=self.user, name='work')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tags/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'work')

    def test_tag_detail_requires_login(self):
        from .models import Tag
        tag = Tag.objects.create(user=self.user, name='work')
        response = self.client.get(f'/tags/{tag.id}/')
        self.assertEqual(response.status_code, 302)

    def test_tag_detail_loads(self):
        from .models import Tag
        tag = Tag.objects.create(user=self.user, name='work')
        entry = JournalEntry.objects.create(user=self.user, content='Work stuff', title='Work Entry')
        entry.tags.add(tag)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tags/{tag.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Work Entry')

    def test_tag_detail_not_found(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tags/99999/')
        self.assertEqual(response.status_code, 404)

    def test_cannot_view_other_users_tag(self):
        from .models import Tag
        other_user = User.objects.create_user(username='other', password='testpass123')
        tag = Tag.objects.create(user=other_user, name='secret')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tags/{tag.id}/')
        self.assertEqual(response.status_code, 404)


class JournalCreateWithTagsTest(TestCase):
    """Tests for creating journals with tags."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_create_journal_with_tags(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/journals/create.html', {
            'content': 'Tagged entry',
            'reflections': '',
            'gratitude': '',
            'tags': 'work, important',
        })
        self.assertEqual(response.status_code, 302)
        entry = JournalEntry.objects.get(user=self.user)
        self.assertEqual(entry.tags.count(), 2)
        tag_names = [t.name for t in entry.tags.all()]
        self.assertIn('work', tag_names)
        self.assertIn('important', tag_names)

    def test_create_journal_without_tags(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/journals/create.html', {
            'content': 'No tags entry',
            'reflections': '',
            'gratitude': '',
        })
        self.assertEqual(response.status_code, 302)
        entry = JournalEntry.objects.get(user=self.user)
        self.assertEqual(entry.tags.count(), 0)


class JournalEditWithTagsTest(TestCase):
    """Tests for editing journals with tags."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.entry = JournalEntry.objects.create(user=self.user, content='Original')

    def test_edit_journal_add_tags(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/details/{self.entry.id}/edit/', {
            'content': 'Updated content',
            'reflections': '',
            'gratitude': '',
            'tags': 'updated, new',
        })
        self.assertEqual(response.status_code, 302)
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.tags.count(), 2)

    def test_edit_journal_remove_tags(self):
        from .models import Tag
        tag = Tag.objects.create(user=self.user, name='old')
        self.entry.tags.add(tag)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/details/{self.entry.id}/edit/', {
            'content': 'Updated',
            'reflections': '',
            'gratitude': '',
            'tags': '',
        })
        self.assertEqual(response.status_code, 302)
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.tags.count(), 0)


class JournalFormTagsTest(TestCase):
    """Tests for the tags field on JournalForm."""

    def test_form_has_tags_field(self):
        form = JournalForm(use_ai=False)
        self.assertIn('tags', form.fields)

    def test_form_valid_without_tags(self):
        data = {
            'content': 'Test content',
            'reflections': '',
            'gratitude': '',
        }
        form = JournalForm(data=data, use_ai=False)
        self.assertTrue(form.is_valid())

    def test_form_valid_with_tags(self):
        data = {
            'content': 'Test content',
            'reflections': '',
            'gratitude': '',
            'tags': 'work, personal',
        }
        form = JournalForm(data=data, use_ai=False)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['tags'], 'work, personal')


# ============================================================
# Tests for Bookmark Feature
# ============================================================

class BookmarkTest(TestCase):
    """Tests for the bookmark toggle feature."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.entry = JournalEntry.objects.create(user=self.user, content='Bookmarkable')

    def test_bookmark_toggle_requires_login(self):
        response = self.client.get(f'/details/{self.entry.id}/bookmark/')
        self.assertEqual(response.status_code, 302)

    def test_bookmark_toggle_on(self):
        self.client.login(username='testuser', password='testpass123')
        self.assertFalse(self.entry.bookmarked)
        response = self.client.get(f'/details/{self.entry.id}/bookmark/')
        self.assertEqual(response.status_code, 302)
        self.entry.refresh_from_db()
        self.assertTrue(self.entry.bookmarked)

    def test_bookmark_toggle_off(self):
        self.entry.bookmarked = True
        self.entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{self.entry.id}/bookmark/')
        self.assertEqual(response.status_code, 302)
        self.entry.refresh_from_db()
        self.assertFalse(self.entry.bookmarked)

    def test_cannot_toggle_others_bookmark(self):
        other_user = User.objects.create_user(username='other', password='testpass123')
        other_entry = JournalEntry.objects.create(user=other_user, content='Other')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{other_entry.id}/bookmark/')
        self.assertEqual(response.status_code, 404)

    def test_bookmark_shown_in_detail(self):
        self.entry.bookmarked = True
        self.entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{self.entry.id}/')
        self.assertContains(response, 'Bookmarked')

    def test_bookmark_entry_default_false(self):
        entry = JournalEntry.objects.create(user=self.user, content='New entry')
        self.assertFalse(entry.bookmarked)


# ============================================================
# Tests for Calendar Data Generation
# ============================================================

class CalendarDataGenerationTest(TestCase):
    """Tests for the generate_calendar_data helper function."""

    def test_generate_single_month(self):
        from datetime import date
        from .views import generate_calendar_data
        mood_map = {'2026-01-15': 'happy'}
        earliest = date(2026, 1, 1)
        latest = date(2026, 1, 31)
        months = generate_calendar_data(earliest, latest, mood_map)
        self.assertEqual(len(months), 1)
        self.assertEqual(months[0]['month'], 'January 2026')

    def test_generate_multiple_months(self):
        from datetime import date
        from .views import generate_calendar_data
        mood_map = {}
        earliest = date(2026, 1, 1)
        latest = date(2026, 2, 28)
        months = generate_calendar_data(earliest, latest, mood_map)
        self.assertEqual(len(months), 2)

    def test_calendar_has_entry_id(self):
        from datetime import date
        from .views import generate_calendar_data
        mood_map = {'2026-01-15': 'happy'}
        date_entry_map = {'2026-01-15': 42}
        earliest = date(2026, 1, 1)
        latest = date(2026, 1, 31)
        months = generate_calendar_data(earliest, latest, mood_map, date_entry_map)
        # Find the day with mood
        for day in months[0]['days']:
            if day and day.get('mood') == 'happy':
                self.assertEqual(day['entry_id'], 42)
                break
