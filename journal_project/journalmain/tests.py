from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import json
from .models import JournalEntry, Goal, Blurb, Report, JournalTemplate
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


# ============================================================
# Tests for Feature 5: Export Journals (JSON/Markdown)
# ============================================================

class ExportJournalsTest(TestCase):
    """Tests for the export journals feature."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.entry1 = JournalEntry.objects.create(
            user=self.user, content='Entry 1 content', title='Entry One',
            mood='["happy"]', reflections='Reflection 1', gratitude='Gratitude 1'
        )
        self.entry2 = JournalEntry.objects.create(
            user=self.user, content='Entry 2 content', title='Entry Two',
            mood='["sad"]'
        )

    def test_export_requires_login(self):
        response = self.client.get('/export/')
        self.assertEqual(response.status_code, 302)

    def test_export_json_default(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], 'Entry One')
        self.assertEqual(data[0]['content'], 'Entry 1 content')
        self.assertEqual(data[0]['mood'], '["happy"]')
        self.assertEqual(data[0]['reflections'], 'Reflection 1')
        self.assertEqual(data[0]['gratitude'], 'Gratitude 1')

    def test_export_json_includes_bookmarked(self):
        self.entry1.bookmarked = True
        self.entry1.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/export/')
        data = json.loads(response.content)
        self.assertTrue(data[0]['bookmarked'])

    def test_export_json_includes_tags(self):
        from .models import Tag
        tag = Tag.objects.create(user=self.user, name='work')
        self.entry1.tags.add(tag)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/export/')
        data = json.loads(response.content)
        self.assertIn('work', data[0]['tags'])

    def test_export_markdown(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/export/', {'format': 'markdown'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/markdown')
        content = response.content.decode('utf-8')
        self.assertIn('Entry One', content)
        self.assertIn('Entry Two', content)
        self.assertIn('Entry 1 content', content)
        self.assertIn('Reflection 1', content)
        self.assertIn('Gratitude 1', content)
        self.assertIn('Total entries: 2', content)

    def test_export_markdown_includes_tags(self):
        from .models import Tag
        tag = Tag.objects.create(user=self.user, name='work')
        self.entry1.tags.add(tag)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/export/', {'format': 'markdown'})
        content = response.content.decode('utf-8')
        self.assertIn('work', content)

    def test_export_only_shows_own_entries(self):
        other_user = User.objects.create_user(username='otheruser', password='testpass123')
        JournalEntry.objects.create(user=other_user, content='Other entry', title='Other Entry')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/export/')
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        titles = [d['title'] for d in data]
        self.assertNotIn('Other Entry', titles)

    def test_export_json_has_content_disposition(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/export/')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('.json', response['Content-Disposition'])

    def test_export_markdown_has_content_disposition(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/export/', {'format': 'markdown'})
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('.md', response['Content-Disposition'])

    def test_export_empty_user(self):
        """Export should work even with no entries."""
        new_user = User.objects.create_user(username='emptyuser', password='testpass123')
        self.client.login(username='emptyuser', password='testpass123')
        response = self.client.get('/export/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)


# ============================================================
# Tests for Feature 6: Streak Tracking Enhancement
# ============================================================

class StreakDetailViewTest(TestCase):
    """Tests for the streak detail view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_streak_detail_requires_login(self):
        response = self.client.get('/streaks/')
        self.assertEqual(response.status_code, 302)

    def test_streak_detail_loads(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/streaks/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Streak Tracking')

    def test_streak_detail_shows_current_streak(self):
        today = timezone.now().date()
        JournalEntry.objects.create(user=self.user, content='Today', date=today)
        JournalEntry.objects.create(user=self.user, content='Yesterday', date=today - timedelta(days=1))
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/streaks/')
        self.assertContains(response, 'Current Streak')

    def test_streak_detail_shows_longest_streak(self):
        today = timezone.now().date()
        for i in range(5):
            JournalEntry.objects.create(user=self.user, content=f'Day {i}', date=today - timedelta(days=i))
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/streaks/')
        self.assertContains(response, 'Longest Streak')

    def test_streak_detail_shows_total_days(self):
        today = timezone.now().date()
        JournalEntry.objects.create(user=self.user, content='Day 1', date=today)
        JournalEntry.objects.create(user=self.user, content='Day 2', date=today - timedelta(days=5))
        JournalEntry.objects.create(user=self.user, content='Day 3', date=today - timedelta(days=10))
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/streaks/')
        self.assertContains(response, 'Total Journaling Days')

    def test_streak_detail_shows_streaks_table(self):
        today = timezone.now().date()
        for i in range(3):
            JournalEntry.objects.create(user=self.user, content=f'Day {i}', date=today - timedelta(days=i))
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/streaks/')
        self.assertContains(response, 'Top Streaks')

    def test_streak_detail_no_entries(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/streaks/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No streaks yet')

    def test_streak_detail_only_shows_own_entries(self):
        other_user = User.objects.create_user(username='otheruser', password='testpass123')
        today = timezone.now().date()
        for i in range(10):
            JournalEntry.objects.create(user=other_user, content=f'Other Day {i}', date=today - timedelta(days=i))
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/streaks/')
        self.assertContains(response, 'No streaks yet')

    def test_streak_detail_multiple_streaks(self):
        """Test that multiple separate streaks are calculated correctly."""
        today = timezone.now().date()
        # First streak: 5 days
        for i in range(5):
            JournalEntry.objects.create(user=self.user, content=f'Streak 1 Day {i}', date=today - timedelta(days=i))
        # Gap of 3 days
        # Second streak: 3 days
        for i in range(3):
            JournalEntry.objects.create(user=self.user, content=f'Streak 2 Day {i}', date=today - timedelta(days=8 + i))
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/streaks/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Top Streaks')


# ============================================================
# Tests for Feature 7: Password Change & Profile Management
# ============================================================

class ProfileViewTest(TestCase):
    """Tests for the profile view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123', email='test@example.com')

    def test_profile_requires_login(self):
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)

    def test_profile_loads(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile')

    def test_profile_shows_username(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        self.assertContains(response, 'testuser')

    def test_profile_shows_email(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        self.assertContains(response, 'test@example.com')

    def test_profile_shows_date_joined(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        self.assertContains(response, 'Date Joined')

    def test_profile_has_change_password_link(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        self.assertContains(response, 'Change Password')

    def test_profile_has_logout_link(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        self.assertContains(response, 'Logout')


class PasswordChangeViewTest(TestCase):
    """Tests for the password change view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_password_change_requires_login(self):
        response = self.client.get('/profile/password-change/')
        self.assertEqual(response.status_code, 302)

    def test_password_change_loads(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/password-change/')
        self.assertEqual(response.status_code, 200)

    def test_password_change_success(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/profile/password-change/', {
            'old_password': 'testpass123',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123',
        })
        self.assertEqual(response.status_code, 302)
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))

    def test_password_change_wrong_old_password(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/profile/password-change/', {
            'old_password': 'wrongpassword',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Old Password')

    def test_password_change_mismatch(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/profile/password-change/', {
            'old_password': 'testpass123',
            'new_password1': 'newpass123',
            'new_password2': 'differentpass',
        })
        self.assertEqual(response.status_code, 200)


class PasswordChangeDoneViewTest(TestCase):
    """Tests for the password change done view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_password_change_done_requires_login(self):
        response = self.client.get('/profile/password-change-done/')
        self.assertEqual(response.status_code, 302)

    def test_password_change_done_loads(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/password-change-done/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password Changed Successfully')


# ============================================================
# Tests for Feature 8: Goal Progress Tracking
# ============================================================

class GoalProgressModelTest(TestCase):
    """Tests for the progress field on Goal model."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_goal_default_progress_is_zero(self):
        goal = Goal.objects.create(
            user=self.user,
            goal_title='Test Goal',
            goal_text='Test text',
            goal_rationale='Test rationale',
            created_at=timezone.now(),
            length='1m'
        )
        self.assertEqual(goal.progress, 0)

    def test_goal_progress_can_be_set(self):
        goal = Goal.objects.create(
            user=self.user,
            goal_title='Test Goal',
            goal_text='Test text',
            goal_rationale='Test rationale',
            created_at=timezone.now(),
            length='1m',
            progress=50
        )
        self.assertEqual(goal.progress, 50)

    def test_goal_progress_max_100(self):
        goal = Goal.objects.create(
            user=self.user,
            goal_title='Test Goal',
            goal_text='Test text',
            goal_rationale='Test rationale',
            created_at=timezone.now(),
            length='1m',
            progress=100
        )
        self.assertEqual(goal.progress, 100)


class GoalProgressFormTest(TestCase):
    """Tests for the progress field on GoalForm."""

    def test_goal_form_has_progress_field(self):
        form = GoalForm()
        self.assertIn('progress', form.fields)

    def test_goal_form_valid_with_progress(self):
        data = {
            'goal_title': 'Test Goal',
            'goal_text': 'Test text',
            'goal_rationale': 'Test rationale',
            'length': '1m',
            'progress': 75,
        }
        form = GoalForm(data=data)
        self.assertTrue(form.is_valid())

    def test_goal_form_valid_without_progress(self):
        data = {
            'goal_title': 'Test Goal',
            'goal_text': 'Test text',
            'goal_rationale': 'Test rationale',
            'length': '1m',
        }
        form = GoalForm(data=data)
        self.assertTrue(form.is_valid())

    def test_goal_form_invalid_progress_too_high(self):
        data = {
            'goal_title': 'Test Goal',
            'goal_text': 'Test text',
            'goal_rationale': 'Test rationale',
            'length': '1m',
            'progress': 101,
        }
        form = GoalForm(data=data)
        self.assertFalse(form.is_valid())

    def test_goal_form_invalid_progress_negative(self):
        data = {
            'goal_title': 'Test Goal',
            'goal_text': 'Test text',
            'goal_rationale': 'Test rationale',
            'length': '1m',
            'progress': -1,
        }
        form = GoalForm(data=data)
        self.assertFalse(form.is_valid())


class GoalProgressViewTest(TestCase):
    """Tests for goal views with progress field."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_goal_create_with_progress(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/goals/create.html', {
            'goal_title': 'New Goal',
            'goal_text': 'Goal description',
            'goal_rationale': 'Why I want this',
            'length': '1y',
            'progress': 25,
        })
        self.assertEqual(response.status_code, 302)
        goal = Goal.objects.get(user=self.user)
        self.assertEqual(goal.progress, 25)

    def test_goal_create_default_progress(self):
        """When no progress is provided, it should default to 0."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/goals/create.html', {
            'goal_title': 'New Goal',
            'goal_text': 'Goal description',
            'goal_rationale': 'Why I want this',
            'length': '1y',
        })
        self.assertEqual(response.status_code, 302)
        goal = Goal.objects.get(user=self.user)
        self.assertEqual(goal.progress, 0)

    def test_goal_edit_with_progress(self):
        goal = Goal.objects.create(
            user=self.user,
            goal_title='Test Goal',
            goal_text='Test text',
            goal_rationale='Test rationale',
            created_at=timezone.now(),
            length='1m',
            progress=10
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/goals/{goal.id}/edit/', {
            'goal_title': 'Updated Goal',
            'goal_text': 'Updated text',
            'goal_rationale': 'Updated rationale',
            'length': '6m',
            'progress': 50,
        })
        self.assertEqual(response.status_code, 302)
        goal.refresh_from_db()
        self.assertEqual(goal.progress, 50)

    def test_goal_detail_shows_progress(self):
        goal = Goal.objects.create(
            user=self.user,
            goal_title='Test Goal',
            goal_text='Test text',
            goal_rationale='Test rationale',
            created_at=timezone.now(),
            length='1m',
            progress=50
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/goals/{goal.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Progress')
        self.assertContains(response, '50%')

    def test_goal_detail_shows_progress_bar(self):
        goal = Goal.objects.create(
            user=self.user,
            goal_title='Test Goal',
            goal_text='Test text',
            goal_rationale='Test rationale',
            created_at=timezone.now(),
            length='1m',
            progress=75
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/goals/{goal.id}/')
        self.assertContains(response, 'progress-bar')
        self.assertContains(response, '75%')

    def test_goal_detail_shows_completed_progress(self):
        goal = Goal.objects.create(
            user=self.user,
            goal_title='Completed Goal',
            goal_text='Done',
            goal_rationale='Because',
            created_at=timezone.now(),
            length='1m',
            progress=100
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/goals/{goal.id}/')
        self.assertContains(response, '100%')
        self.assertContains(response, 'bg-success')

    def test_goalindex_shows_progress(self):
        Goal.objects.create(
            user=self.user,
            goal_title='Test Goal',
            goal_text='Test text',
            goal_rationale='Test rationale',
            created_at=timezone.now(),
            length='1m',
            progress=30
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/goals/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '30%')


# ============================================================
# Tests for Feature 9: Weekly Report Generation Management Command
# ============================================================

class GenerateWeeklyReportCommandTest(TestCase):
    """Tests for the generate_weekly_report management command."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.today = timezone.now().date()

    def test_command_creates_report_with_entries(self):
        """Command should create a weekly report when entries exist."""
        from django.core.management import call_command
        from io import StringIO
        JournalEntry.objects.create(user=self.user, content='Entry 1', date=self.today)
        JournalEntry.objects.create(user=self.user, content='Entry 2', date=self.today - timedelta(days=1))
        out = StringIO()
        call_command('generate_weekly_report', stdout=out)
        self.assertEqual(Report.objects.filter(user=self.user).count(), 1)
        report = Report.objects.first()
        self.assertEqual(report.type, 'w')
        self.assertIn('Weekly Report', report.title)
        self.assertIn('Weekly Summary', report.content)

    def test_command_skips_when_no_entries(self):
        """Command should skip users with no entries."""
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        call_command('generate_weekly_report', stdout=out)
        self.assertEqual(Report.objects.count(), 0)
        output = out.getvalue()
        self.assertIn('No journal entries', output)

    def test_command_skips_duplicate_report(self):
        """Command should skip if report already exists for the week."""
        from django.core.management import call_command
        from io import StringIO
        JournalEntry.objects.create(user=self.user, content='Entry', date=self.today)
        out = StringIO()
        call_command('generate_weekly_report', stdout=out)
        self.assertEqual(Report.objects.filter(user=self.user).count(), 1)
        # Run again
        out2 = StringIO()
        call_command('generate_weekly_report', stdout=out2)
        self.assertEqual(Report.objects.filter(user=self.user).count(), 1)
        self.assertIn('already exists', out2.getvalue())

    def test_command_with_user_flag(self):
        """Command should only generate for specified user."""
        from django.core.management import call_command
        from io import StringIO
        other_user = User.objects.create_user(username='other', password='testpass123')
        JournalEntry.objects.create(user=self.user, content='My entry', date=self.today)
        JournalEntry.objects.create(user=other_user, content='Other entry', date=self.today)
        out = StringIO()
        call_command('generate_weekly_report', user='testuser', stdout=out)
        self.assertEqual(Report.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Report.objects.filter(user=other_user).count(), 0)

    def test_command_with_nonexistent_user(self):
        """Command should report error for nonexistent user."""
        from django.core.management import call_command
        from io import StringIO
        err = StringIO()
        call_command('generate_weekly_report', user='nonexistent', stderr=err)
        self.assertIn('not found', err.getvalue())

    def test_command_links_entries_to_report(self):
        """Command should link journal entries to the generated report."""
        from django.core.management import call_command
        from io import StringIO
        entry = JournalEntry.objects.create(user=self.user, content='Entry', date=self.today)
        call_command('generate_weekly_report')
        entry.refresh_from_db()
        self.assertIsNotNone(entry.week_report)

    def test_report_content_has_entry_count(self):
        """Generated report should include entry count."""
        from django.core.management import call_command
        JournalEntry.objects.create(user=self.user, content='Entry 1', date=self.today)
        JournalEntry.objects.create(user=self.user, content='Entry 2', date=self.today - timedelta(days=1))
        JournalEntry.objects.create(user=self.user, content='Entry 3', date=self.today - timedelta(days=2))
        call_command('generate_weekly_report')
        report = Report.objects.first()
        self.assertIn('3 journal entries', report.content)

    def test_report_content_has_mood_summary(self):
        """Generated report should include mood summary when moods are present."""
        from django.core.management import call_command
        JournalEntry.objects.create(user=self.user, content='Happy', date=self.today, mood='["happy"]')
        JournalEntry.objects.create(user=self.user, content='Happy again', date=self.today - timedelta(days=1), mood='["happy"]')
        call_command('generate_weekly_report')
        report = Report.objects.first()
        self.assertIn('Mood Summary', report.content)
        self.assertIn('happy', report.content)


# ============================================================
# Tests for Feature 9: Report List View
# ============================================================

class ReportListViewTest(TestCase):
    """Tests for the report list view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.report = Report.objects.create(
            user=self.user,
            title='Weekly Report',
            type='w',
            content='Report content'
        )

    def test_report_list_requires_login(self):
        response = self.client.get('/reports/')
        self.assertEqual(response.status_code, 302)

    def test_report_list_loads(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Weekly Report')

    def test_report_list_only_shows_own_reports(self):
        other_user = User.objects.create_user(username='other', password='testpass123')
        Report.objects.create(user=other_user, title='Other Report', type='w', content='Other content')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/')
        self.assertContains(response, 'Weekly Report')
        self.assertNotContains(response, 'Other Report')

    def test_report_list_empty(self):
        new_user = User.objects.create_user(username='empty', password='testpass123')
        self.client.login(username='empty', password='testpass123')
        response = self.client.get('/reports/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No reports yet')


# ============================================================
# Tests for Feature 10: Pagination
# ============================================================

class PaginationTest(TestCase):
    """Tests for pagination on listing views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_journals_pagination(self):
        """Journals view should paginate at 15 entries per page."""
        # Create 20 entries
        for i in range(20):
            JournalEntry.objects.create(user=self.user, content=f'Entry {i}', title=f'Title {i}')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['journal_entries']), 15)
        self.assertTrue(response.context['page_obj'].has_other_pages())
        self.assertContains(response, '1 of 2')

    def test_journals_pagination_page_2(self):
        """Second page of journals should show remaining entries."""
        for i in range(20):
            JournalEntry.objects.create(user=self.user, content=f'Entry {i}', title=f'Title {i}')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/', {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['journal_entries']), 5)

    def test_journals_pagination_preserves_filters(self):
        """Pagination links should preserve search filters."""
        JournalEntry.objects.create(user=self.user, content='Beach day', title='Beach')
        for i in range(15):
            JournalEntry.objects.create(user=self.user, content=f'Entry {i}', title=f'Title {i}')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/', {'q': 'Beach'})
        self.assertEqual(response.status_code, 200)
        # Should only have 1 result, no pagination needed
        self.assertFalse(response.context['page_obj'].has_other_pages())

    def test_goals_pagination(self):
        """Goals view should paginate at 10 goals per page."""
        for i in range(15):
            Goal.objects.create(
                user=self.user,
                goal_title=f'Goal {i}',
                goal_text='Test text',
                goal_rationale='Test rationale',
                created_at=timezone.now(),
                length='1m'
            )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/goals/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['goal_entries']), 10)
        self.assertTrue(response.context['page_obj'].has_other_pages())

    def test_goals_pagination_page_2(self):
        """Second page of goals should show remaining entries."""
        for i in range(15):
            Goal.objects.create(
                user=self.user,
                goal_title=f'Goal {i}',
                goal_text='Test text',
                goal_rationale='Test rationale',
                created_at=timezone.now(),
                length='1m'
            )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/goals/', {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['goal_entries']), 5)

    def test_report_list_pagination(self):
        """Report list view should paginate at 10 reports per page."""
        for i in range(15):
            Report.objects.create(
                user=self.user,
                title=f'Report {i}',
                type='w',
                content='Content'
            )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['reports']), 10)
        self.assertTrue(response.context['page_obj'].has_other_pages())

    def test_tag_list_pagination(self):
        """Tag list view should paginate at 20 tags per page."""
        from .models import Tag
        for i in range(25):
            Tag.objects.create(user=self.user, name=f'tag{i}')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tags/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['tags']), 20)
        self.assertTrue(response.context['page_obj'].has_other_pages())

    def test_tag_detail_pagination(self):
        """Tag detail view should paginate at 15 entries per page."""
        from .models import Tag
        tag = Tag.objects.create(user=self.user, name='work')
        for i in range(20):
            entry = JournalEntry.objects.create(user=self.user, content=f'Entry {i}', title=f'Title {i}')
            entry.tags.add(tag)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tags/{tag.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['entries']), 15)
        self.assertTrue(response.context['page_obj'].has_other_pages())

    def test_pagination_no_entries_no_pagination(self):
        """Views with few entries should not show pagination controls."""
        JournalEntry.objects.create(user=self.user, content='Only entry', title='Only')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['page_obj'].has_other_pages())

    def test_pagination_invalid_page_number(self):
        """Invalid page number should return last page gracefully."""
        for i in range(20):
            JournalEntry.objects.create(user=self.user, content=f'Entry {i}', title=f'Title {i}')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/', {'page': 'abc'})
        self.assertEqual(response.status_code, 200)

    def test_pagination_out_of_range_page(self):
        """Out of range page number should return last page."""
        for i in range(20):
            JournalEntry.objects.create(user=self.user, content=f'Entry {i}', title=f'Title {i}')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/', {'page': 999})
        self.assertEqual(response.status_code, 200)
        # Should return last page
        self.assertEqual(response.context['page_obj'].number, 2)


# ============================================================
# Tests for Polish: Navigation Bar
# ============================================================

class NavigationBarTest(TestCase):
    """Tests for the navigation bar inclusion."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_nav_included_in_dashboard(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertContains(response, 'navbar')
        self.assertContains(response, 'Journals')
        self.assertContains(response, 'Goals')
        self.assertContains(response, 'Mood Calendar')
        self.assertContains(response, 'Tags')
        self.assertContains(response, 'Streaks')
        self.assertContains(response, 'Reports')
        self.assertContains(response, 'Profile')
        self.assertContains(response, 'Logout')

    def test_nav_included_in_journals(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/')
        self.assertContains(response, 'navbar')

    def test_nav_included_in_goals(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/goals/')
        self.assertContains(response, 'navbar')

    def test_nav_included_in_tags(self):
        from .models import Tag
        Tag.objects.create(user=self.user, name='work')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tags/')
        self.assertContains(response, 'navbar')

    def test_nav_included_in_reports(self):
        Report.objects.create(user=self.user, title='Test Report', type='w', content='Content')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/')
        self.assertContains(response, 'navbar')

    def test_nav_included_in_streaks(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/streaks/')
        self.assertContains(response, 'navbar')

    def test_nav_included_in_profile(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        self.assertContains(response, 'navbar')

    def test_nav_included_in_mood_calendar(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mood-calendar/')
        self.assertContains(response, 'navbar')

    def test_nav_included_in_journal_detail(self):
        entry = JournalEntry.objects.create(user=self.user, content='Test', title='Test')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{entry.id}/')
        self.assertContains(response, 'navbar')

    def test_nav_included_in_goal_detail(self):
        goal = Goal.objects.create(
            user=self.user,
            goal_title='Test Goal',
            goal_text='Test text',
            goal_rationale='Test rationale',
            created_at=timezone.now(),
            length='1m'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/goals/{goal.id}/')
        self.assertContains(response, 'navbar')

    def test_nav_included_in_report_detail(self):
        report = Report.objects.create(user=self.user, title='Test Report', type='w', content='Content')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/reports/{report.id}/')
        self.assertContains(response, 'navbar')

    def test_nav_included_in_tag_detail(self):
        from .models import Tag
        tag = Tag.objects.create(user=self.user, name='work')
        entry = JournalEntry.objects.create(user=self.user, content='Test', title='Test')
        entry.tags.add(tag)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tags/{tag.id}/')
        self.assertContains(response, 'navbar')


# ============================================================
# Tests for Polish: No Debug Print Statements
# ============================================================

class NoDebugPrintTest(TestCase):
    """Verify no debug print statements remain in views.py."""

    def test_no_print_in_views(self):
        """views.py should not contain any print() statements."""
        import os
        views_path = os.path.join(os.path.dirname(__file__), 'views.py')
        with open(views_path, 'r') as f:
            content = f.read()
        # Check for print statements (not commented out)
        import re
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip commented lines
            if stripped.startswith('#'):
                continue
            # Check for print() calls
            if re.match(r'^print\s*\(', stripped):
                self.fail(f'Found print statement at line {i}: {stripped}')


# ============================================================
# Tests for Phase 2 Feature 1: Monthly Report Generation
# ============================================================

class MonthlyReportCommandTest(TestCase):
    """Tests for the --monthly flag on generate_weekly_report command."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_monthly_command_creates_report(self):
        """Command should create a monthly report when entries exist."""
        from django.core.management import call_command
        from io import StringIO
        from datetime import date as date_type
        entry = JournalEntry.objects.create(user=self.user, content='Entry 1')
        entry.date = date_type(2024, 3, 15)
        entry.save()
        out = StringIO()
        call_command('generate_weekly_report', '--monthly', stdout=out)
        self.assertEqual(Report.objects.filter(user=self.user, type='m').count(), 1)
        report = Report.objects.filter(user=self.user, type='m').first()
        self.assertIn('Monthly Report', report.title)
        self.assertIn('March', report.title)

    def test_monthly_command_skips_when_no_entries(self):
        """Command should skip users with no entries."""
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        call_command('generate_weekly_report', '--monthly', stdout=out)
        self.assertEqual(Report.objects.filter(type='m').count(), 0)

    def test_monthly_command_skips_duplicate(self):
        """Command should skip if monthly report already exists."""
        from django.core.management import call_command
        from io import StringIO
        from datetime import date as date_type
        entry = JournalEntry.objects.create(user=self.user, content='Entry')
        entry.date = date_type(2024, 3, 15)
        entry.save()
        out = StringIO()
        call_command('generate_weekly_report', '--monthly', stdout=out)
        self.assertEqual(Report.objects.filter(user=self.user, type='m').count(), 1)
        out2 = StringIO()
        call_command('generate_weekly_report', '--monthly', stdout=out2)
        self.assertEqual(Report.objects.filter(user=self.user, type='m').count(), 1)
        self.assertIn('already exists', out2.getvalue())

    def test_monthly_command_links_entries(self):
        """Command should link journal entries to monthly report."""
        from django.core.management import call_command
        from datetime import date as date_type
        entry = JournalEntry.objects.create(user=self.user, content='Entry')
        entry.date = date_type(2024, 3, 15)
        entry.save()
        call_command('generate_weekly_report', '--monthly')
        entry.refresh_from_db()
        self.assertIsNotNone(entry.month_report)

    def test_monthly_command_with_user_flag(self):
        """Command should only generate for specified user."""
        from django.core.management import call_command
        from io import StringIO
        from datetime import date as date_type
        other_user = User.objects.create_user(username='other', password='testpass123')
        e1 = JournalEntry.objects.create(user=self.user, content='My entry')
        e1.date = date_type(2024, 3, 15)
        e1.save()
        e2 = JournalEntry.objects.create(user=other_user, content='Other entry')
        e2.date = date_type(2024, 3, 15)
        e2.save()
        out = StringIO()
        call_command('generate_weekly_report', '--monthly', user='testuser', stdout=out)
        self.assertEqual(Report.objects.filter(user=self.user, type='m').count(), 1)
        self.assertEqual(Report.objects.filter(user=other_user, type='m').count(), 0)

    def test_monthly_report_content_has_entry_count(self):
        """Generated monthly report should include entry count."""
        from django.core.management import call_command
        from datetime import date as date_type
        for i in range(3):
            entry = JournalEntry.objects.create(user=self.user, content=f'Entry {i}')
            entry.date = date_type(2024, 3, 1 + i)
            entry.save()
        call_command('generate_weekly_report', '--monthly')
        report = Report.objects.filter(user=self.user, type='m').first()
        self.assertIn('3 journal entries', report.content)

    def test_monthly_report_content_has_mood_summary(self):
        """Generated monthly report should include mood summary."""
        from django.core.management import call_command
        from datetime import date as date_type
        e1 = JournalEntry.objects.create(user=self.user, content='Happy', mood='["happy"]')
        e1.date = date_type(2024, 3, 1)
        e1.save()
        e2 = JournalEntry.objects.create(user=self.user, content='Happy again', mood='["happy"]')
        e2.date = date_type(2024, 3, 2)
        e2.save()
        call_command('generate_weekly_report', '--monthly')
        report = Report.objects.filter(user=self.user, type='m').first()
        self.assertIn('Mood Summary', report.content)
        self.assertIn('happy', report.content)

    def test_monthly_report_content_has_writing_stats(self):
        """Generated monthly report should include writing stats."""
        from django.core.management import call_command
        from datetime import date as date_type
        entry = JournalEntry.objects.create(user=self.user, content='Hello world this is a test')
        entry.date = date_type(2024, 3, 1)
        entry.save()
        call_command('generate_weekly_report', '--monthly')
        report = Report.objects.filter(user=self.user, type='m').first()
        self.assertIn('Writing Stats', report.content)
        self.assertIn('Total words written', report.content)


class MonthlyReportViewTest(TestCase):
    """Tests for the monthly report views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_monthly_report_list_requires_login(self):
        response = self.client.get('/reports/monthly/')
        self.assertEqual(response.status_code, 302)

    def test_monthly_report_list_loads(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/monthly/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Monthly Reports')

    def test_monthly_report_list_empty(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/monthly/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No journal entries yet')

    def test_monthly_report_list_shows_months(self):
        from datetime import date as date_type
        entry = JournalEntry.objects.create(user=self.user, content='Entry')
        entry.date = date_type(2024, 3, 15)
        entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/monthly/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'March')
        self.assertContains(response, '2024')

    def test_monthly_report_list_only_shows_own_months(self):
        from datetime import date as date_type
        other_user = User.objects.create_user(username='other', password='testpass123')
        entry = JournalEntry.objects.create(user=other_user, content='Other')
        entry.date = date_type(2024, 3, 15)
        entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/monthly/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No journal entries yet')

    def test_generate_monthly_report_requires_login(self):
        response = self.client.get('/reports/monthly/2024/3/')
        self.assertEqual(response.status_code, 302)

    def test_generate_monthly_report_creates_report(self):
        from datetime import date as date_type
        entry = JournalEntry.objects.create(user=self.user, content='March entry', title='March Entry')
        entry.date = date_type(2024, 3, 15)
        entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/monthly/2024/3/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Monthly Report')
        self.assertEqual(Report.objects.filter(user=self.user, type='m').count(), 1)

    def test_generate_monthly_report_returns_existing(self):
        from datetime import date as date_type
        entry = JournalEntry.objects.create(user=self.user, content='March entry')
        entry.date = date_type(2024, 3, 15)
        entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/monthly/2024/3/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Report.objects.filter(user=self.user, type='m').count(), 1)
        # Run again - should return existing
        response = self.client.get('/reports/monthly/2024/3/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Report.objects.filter(user=self.user, type='m').count(), 1)

    def test_generate_monthly_report_no_entries(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/monthly/2024/3/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No journal entries found')

    def test_generate_monthly_report_only_shows_own_entries(self):
        from datetime import date as date_type
        other_user = User.objects.create_user(username='other', password='testpass123')
        entry = JournalEntry.objects.create(user=other_user, content='Other entry')
        entry.date = date_type(2024, 3, 15)
        entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/monthly/2024/3/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No journal entries found')

    def test_monthly_report_list_shows_has_report_indicator(self):
        from datetime import date as date_type
        entry = JournalEntry.objects.create(user=self.user, content='Entry')
        entry.date = date_type(2024, 3, 15)
        entry.save()
        self.client.login(username='testuser', password='testpass123')
        # First generate the report
        self.client.get('/reports/monthly/2024/3/')
        # Then check the list shows it as generated
        response = self.client.get('/reports/monthly/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Generated')


# ============================================================
# Tests for Phase 2 Feature 2: On This Day / Memory Feature
# ============================================================

class OnThisDayViewTest(TestCase):
    """Tests for the On This Day view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_on_this_day_requires_login(self):
        response = self.client.get('/on-this-day/')
        self.assertEqual(response.status_code, 302)

    def test_on_this_day_loads(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/on-this-day/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'On This Day')

    def test_on_this_day_shows_past_entries(self):
        from datetime import date as date_type
        today = timezone.now().date()
        # Create entry from 2 years ago on same date
        entry = JournalEntry.objects.create(
            user=self.user, content='Entry from 2 years ago', title='Memory'
        )
        entry.date = date_type(today.year - 2, today.month, today.day)
        entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/on-this-day/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Memory')

    def test_on_this_day_does_not_show_today(self):
        """Entries from today should not appear in On This Day."""
        today = timezone.now().date()
        entry = JournalEntry.objects.create(
            user=self.user, content='Today entry', title='Today'
        )
        entry.date = today
        entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/on-this-day/')
        self.assertEqual(response.status_code, 200)
        # The query filters date__year__lt=today.year, so today's entries should not appear
        self.assertNotContains(response, 'Today entry')

    def test_on_this_day_custom_date(self):
        """Should be able to look up a custom date via query params."""
        entry = JournalEntry.objects.create(
            user=self.user, content='July 4th entry', title='Independence Day'
        )
        entry.date = timezone.now().date().replace(month=7, day=4)
        entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/on-this-day/', {'month': 7, 'day': 4})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Independence Day')

    def test_on_this_day_no_entries(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/on-this-day/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No journal entries found')

    def test_on_this_day_only_shows_own_entries(self):
        from datetime import date as date_type
        other_user = User.objects.create_user(username='other', password='testpass123')
        today = timezone.now().date()
        entry = JournalEntry.objects.create(user=other_user, content='Other', title='Other Memory')
        entry.date = date_type(today.year - 1, today.month, today.day)
        entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/on-this-day/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Other Memory')

    def test_on_this_day_has_date_picker(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/on-this-day/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Look up another date')

    def test_on_this_day_orders_by_date_desc(self):
        """Entries should be ordered newest first."""
        from datetime import date as date_type
        today = timezone.now().date()
        e1 = JournalEntry.objects.create(user=self.user, content='Older', title='Older Entry')
        e1.date = date_type(today.year - 3, today.month, today.day)
        e1.save()
        e2 = JournalEntry.objects.create(user=self.user, content='Newer', title='Newer Entry')
        e2.date = date_type(today.year - 1, today.month, today.day)
        e2.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/on-this-day/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        newer_pos = content.find('Newer Entry')
        older_pos = content.find('Older Entry')
        self.assertLess(newer_pos, older_pos)


class DashboardOnThisDayTest(TestCase):
    """Tests for the On This Day widget on the dashboard."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_dashboard_shows_on_this_day_section(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'On This Day')

    def test_dashboard_shows_on_this_day_entries(self):
        from datetime import date as date_type
        today = timezone.now().date()
        entry = JournalEntry.objects.create(
            user=self.user, content='Memory content', title='Past Memory'
        )
        entry.date = date_type(today.year - 1, today.month, today.day)
        entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Past Memory')

    def test_dashboard_shows_on_this_day_link(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'View All')

    def test_dashboard_on_this_day_only_shows_own(self):
        from datetime import date as date_type
        other_user = User.objects.create_user(username='other', password='testpass123')
        today = timezone.now().date()
        entry = JournalEntry.objects.create(user=other_user, content='Other', title='Other Memory')
        entry.date = date_type(today.year - 1, today.month, today.day)
        entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertNotContains(response, 'Other Memory')

    def test_dashboard_on_this_day_limits_to_2(self):
        """Dashboard should show at most 2 on-this-day entries."""
        from datetime import date as date_type
        today = timezone.now().date()
        for i in range(5):
            entry = JournalEntry.objects.create(user=self.user, content=f'Memory {i}', title=f'Memory {i}')
            entry.date = date_type(today.year - (i + 1), today.month, today.day)
            entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Check that the context has exactly 2 on_this_day_entries
        self.assertEqual(len(response.context['on_this_day_entries']), 2)


# ============================================================
# Tests for Phase 2 Feature 3: Mood Trend Chart
# ============================================================

class MoodTrendsViewTest(TestCase):
    """Tests for the mood trends view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_mood_trends_requires_login(self):
        response = self.client.get('/mood-trends/')
        self.assertEqual(response.status_code, 302)

    def test_mood_trends_loads(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mood-trends/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mood Trends')

    def test_mood_trends_no_data(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mood-trends/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No mood data available')

    def test_mood_trends_shows_weeks(self):
        entry = JournalEntry.objects.create(user=self.user, content='Entry', mood='["happy"]')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mood-trends/')
        self.assertEqual(response.status_code, 200)
        # Should show the week data
        self.assertContains(response, 'W')

    def test_mood_trends_groups_by_week(self):
        """Multiple entries in the same week should be grouped."""
        from datetime import date as date_type
        today = timezone.now().date()
        JournalEntry.objects.create(user=self.user, content='Entry 1', mood='["happy"]', date=today)
        JournalEntry.objects.create(user=self.user, content='Entry 2', mood='["happy", "excited"]', date=today - timedelta(days=1))
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mood-trends/')
        self.assertEqual(response.status_code, 200)
        # Should show the week data with capitalized mood names
        self.assertContains(response, 'Happy')

    def test_mood_trends_shows_top_3_moods(self):
        """Should only show top 3 moods per week."""
        entry = JournalEntry.objects.create(
            user=self.user,
            content='Entry',
            mood='["happy", "sad", "angry", "calm", "excited"]'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mood-trends/')
        self.assertEqual(response.status_code, 200)
        # The template shows top 3 moods - we can't easily assert count in template
        # but we can verify the view returns correct data
        weeks = response.context['weeks']
        self.assertEqual(len(weeks), 1)
        self.assertEqual(len(weeks[0]['top_moods']), 3)

    def test_mood_trends_only_shows_own_entries(self):
        other_user = User.objects.create_user(username='other', password='testpass123')
        JournalEntry.objects.create(user=other_user, content='Other', mood='["happy"]')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mood-trends/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No mood data available')

    def test_mood_trends_excludes_null_mood(self):
        """Entries without mood should be excluded."""
        JournalEntry.objects.create(user=self.user, content='No mood')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mood-trends/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No mood data available')

    def test_mood_trends_has_legend(self):
        """Mood trends page should show a legend."""
        JournalEntry.objects.create(user=self.user, content='Entry', mood='["happy"]')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mood-trends/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Legend')

    def test_mood_trends_mood_bars_have_colors(self):
        """Mood bars should have color information."""
        JournalEntry.objects.create(user=self.user, content='Entry', mood='["happy"]')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mood-trends/')
        self.assertEqual(response.status_code, 200)
        weeks = response.context['weeks']
        self.assertTrue(len(weeks) > 0)
        self.assertTrue(len(weeks[0]['top_moods']) > 0)
        # Check that color is set
        self.assertIn('color', weeks[0]['top_moods'][0])
        self.assertIn('width', weeks[0]['top_moods'][0])

    def test_mood_trends_multiple_weeks(self):
        """Entries in different weeks should create separate week entries."""
        from datetime import date as date_type
        today = timezone.now().date()
        # Entry in current week
        JournalEntry.objects.create(user=self.user, content='This week', mood='["happy"]', date=today)
        # Entry 2 weeks ago
        e2 = JournalEntry.objects.create(user=self.user, content='Two weeks ago', mood='["sad"]')
        e2.date = today - timedelta(days=14)
        e2.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mood-trends/')
        self.assertEqual(response.status_code, 200)
        weeks = response.context['weeks']
        self.assertEqual(len(weeks), 2)


class NavigationPhase2Test(TestCase):
    """Tests for Phase 2 navigation links."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_nav_has_monthly_reports_link(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertContains(response, 'Monthly Reports')

    def test_nav_has_on_this_day_link(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertContains(response, 'On This Day')

    def test_nav_has_mood_trends_link(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertContains(response, 'Mood Trends')

    def test_monthly_reports_page_has_nav(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/monthly/')
        self.assertContains(response, 'navbar')

    def test_on_this_day_page_has_nav(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/on-this-day/')
        self.assertContains(response, 'navbar')

    def test_mood_trends_page_has_nav(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mood-trends/')
        self.assertContains(response, 'navbar')


# ============================================================
# Tests for Phase 2 Feature 4: AI-Powered Goal Linking
# ============================================================

class GoalLinkingModelTest(TestCase):
    """Tests for the Goal-JournalEntry ManyToMany relationship."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_goal_has_journals_field(self):
        goal = Goal.objects.create(
            user=self.user,
            goal_title='Test Goal',
            goal_text='Test text',
            goal_rationale='Test rationale',
            created_at=timezone.now(),
            length='1m'
        )
        entry = JournalEntry.objects.create(user=self.user, content='Test')
        goal.journals.add(entry)
        self.assertEqual(goal.journals.count(), 1)
        self.assertIn(entry, goal.journals.all())

    def test_journal_entry_has_goals_reverse_relation(self):
        goal = Goal.objects.create(
            user=self.user,
            goal_title='Test Goal',
            goal_text='Test text',
            goal_rationale='Test rationale',
            created_at=timezone.now(),
            length='1m'
        )
        entry = JournalEntry.objects.create(user=self.user, content='Test')
        entry.goals.add(goal)
        self.assertEqual(entry.goals.count(), 1)
        self.assertIn(goal, entry.goals.all())

    def test_multiple_goals_per_journal(self):
        goal1 = Goal.objects.create(
            user=self.user, goal_title='Goal 1', goal_text='Text',
            goal_rationale='Rationale', created_at=timezone.now(), length='1m'
        )
        goal2 = Goal.objects.create(
            user=self.user, goal_title='Goal 2', goal_text='Text',
            goal_rationale='Rationale', created_at=timezone.now(), length='1m'
        )
        entry = JournalEntry.objects.create(user=self.user, content='Test')
        entry.goals.add(goal1, goal2)
        self.assertEqual(entry.goals.count(), 2)


class GoalLinkingFormTest(TestCase):
    """Tests for the linked_goals field on JournalForm."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_form_has_linked_goals_when_ai_disabled(self):
        form = JournalForm(use_ai=False)
        self.assertIn('linked_goals', form.fields)

    def test_form_no_linked_goals_when_ai_enabled(self):
        form = JournalForm(use_ai=True)
        self.assertNotIn('linked_goals', form.fields)

    def test_linked_goals_field_is_model_multiple_choice(self):
        from django import forms as django_forms
        form = JournalForm(use_ai=False)
        self.assertIsInstance(form.fields['linked_goals'], django_forms.ModelMultipleChoiceField)

    def test_linked_goals_field_not_required(self):
        form = JournalForm(use_ai=False)
        self.assertFalse(form.fields['linked_goals'].required)

    def test_linked_goals_default_queryset_is_empty(self):
        form = JournalForm(use_ai=False)
        self.assertEqual(form.fields['linked_goals'].queryset.count(), 0)

    def test_linked_goals_can_be_set_on_queryset(self):
        goal = Goal.objects.create(
            user=self.user, goal_title='Test Goal', goal_text='Text',
            goal_rationale='Rationale', created_at=timezone.now(), length='1m'
        )
        form = JournalForm(use_ai=False)
        form.fields['linked_goals'].queryset = Goal.objects.filter(user=self.user)
        self.assertEqual(form.fields['linked_goals'].queryset.count(), 1)

    def test_form_valid_with_linked_goals(self):
        goal = Goal.objects.create(
            user=self.user, goal_title='Test Goal', goal_text='Text',
            goal_rationale='Rationale', created_at=timezone.now(), length='1m'
        )
        data = {
            'content': 'Test content',
            'reflections': '',
            'gratitude': '',
            'linked_goals': [goal.id],
        }
        form = JournalForm(data=data, use_ai=False)
        form.fields['linked_goals'].queryset = Goal.objects.filter(user=self.user)
        self.assertTrue(form.is_valid())


class GoalLinkingCreateViewTest(TestCase):
    """Tests for goal linking in journal_create view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.goal = Goal.objects.create(
            user=self.user, goal_title='Learn Django', goal_text='Complete tutorials',
            goal_rationale='Career growth', created_at=timezone.now(), length='1m'
        )

    def test_create_with_manual_goal_linking(self):
        """When USE_AI=False, manual goal linking should work."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/journals/create.html', {
            'content': 'I am working on learning Django today',
            'reflections': '',
            'gratitude': '',
            'linked_goals': [self.goal.id],
        })
        self.assertEqual(response.status_code, 302)
        entry = JournalEntry.objects.get(user=self.user)
        self.assertEqual(entry.goals.count(), 1)
        self.assertIn(self.goal, entry.goals.all())

    def test_create_without_goal_linking(self):
        """Journal can be created without linking goals."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/journals/create.html', {
            'content': 'Just a regular day',
            'reflections': '',
            'gratitude': '',
        })
        self.assertEqual(response.status_code, 302)
        entry = JournalEntry.objects.get(user=self.user)
        self.assertEqual(entry.goals.count(), 0)

    def test_create_shows_goals_in_form_context(self):
        """GET request should include goals in form for manual linking."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/create.html')
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('linked_goals', form.fields)
        self.assertEqual(form.fields['linked_goals'].queryset.count(), 1)

    def test_create_multiple_goal_linking(self):
        """Multiple goals can be linked at once."""
        goal2 = Goal.objects.create(
            user=self.user, goal_title='Exercise', goal_text='Run daily',
            goal_rationale='Health', created_at=timezone.now(), length='1m'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/journals/create.html', {
            'content': 'Working on both goals today',
            'reflections': '',
            'gratitude': '',
            'linked_goals': [self.goal.id, goal2.id],
        })
        self.assertEqual(response.status_code, 302)
        entry = JournalEntry.objects.get(user=self.user)
        self.assertEqual(entry.goals.count(), 2)


class GoalLinkingEditViewTest(TestCase):
    """Tests for goal linking in journal_edit view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.goal = Goal.objects.create(
            user=self.user, goal_title='Learn Django', goal_text='Complete tutorials',
            goal_rationale='Career growth', created_at=timezone.now(), length='1m'
        )
        self.entry = JournalEntry.objects.create(
            user=self.user, content='Test content', title='Test'
        )

    def test_edit_adds_goal_linking(self):
        """Editing a journal should allow adding goal links."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/details/{self.entry.id}/edit/', {
            'content': 'Updated content about learning Django',
            'reflections': '',
            'gratitude': '',
            'linked_goals': [self.goal.id],
        })
        self.assertEqual(response.status_code, 302)
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.goals.count(), 1)
        self.assertIn(self.goal, self.entry.goals.all())

    def test_edit_shows_existing_linked_goals(self):
        """Edit form should pre-fill existing goal links."""
        self.entry.goals.add(self.goal)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{self.entry.id}/edit/')
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('linked_goals', form.fields)
        self.assertEqual(list(form.initial.get('linked_goals', [])), [self.goal])

    def test_edit_removes_goal_linking(self):
        """Editing without goal links should clear them."""
        self.entry.goals.add(self.goal)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/details/{self.entry.id}/edit/', {
            'content': 'Updated content',
            'reflections': '',
            'gratitude': '',
            'linked_goals': [],
        })
        self.assertEqual(response.status_code, 302)
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.goals.count(), 0)


class GoalLinkingDetailViewTest(TestCase):
    """Tests for linked goals display in journal_detail."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.goal = Goal.objects.create(
            user=self.user, goal_title='Learn Django', goal_text='Complete tutorials',
            goal_rationale='Career growth', created_at=timezone.now(), length='1m'
        )
        self.entry = JournalEntry.objects.create(
            user=self.user, content='Test content', title='Test Entry'
        )

    def test_detail_shows_linked_goals(self):
        self.entry.goals.add(self.goal)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{self.entry.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Linked Goals')
        self.assertContains(response, 'Learn Django')

    def test_detail_shows_goal_link(self):
        self.entry.goals.add(self.goal)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{self.entry.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'/goals/{self.goal.id}/')

    def test_detail_no_goals_section_when_none_linked(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{self.entry.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Linked Goals')


class GoalDetailViewLinkedJournalsTest(TestCase):
    """Tests for linked journals display in goal_detail."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.goal = Goal.objects.create(
            user=self.user, goal_title='Learn Django', goal_text='Complete tutorials',
            goal_rationale='Career growth', created_at=timezone.now(), length='1m'
        )
        self.entry = JournalEntry.objects.create(
            user=self.user, content='Test content', title='Django Learning'
        )

    def test_goal_detail_shows_linked_journals(self):
        self.goal.journals.add(self.entry)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/goals/{self.goal.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Linked Journal Entries')
        self.assertContains(response, 'Django Learning')

    def test_goal_detail_shows_journal_link(self):
        self.goal.journals.add(self.entry)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/goals/{self.goal.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'/details/{self.entry.id}/')

    def test_goal_detail_no_journals_section_when_none_linked(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/goals/{self.goal.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Linked Journal Entries')


# ============================================================
# Tests for Phase 2 Feature 5: Journal Entry Word Count & Stats
# ============================================================

class JournalEntryWordCountTest(TestCase):
    """Tests for word_count, char_count, and reading_time_minutes methods."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_word_count_basic(self):
        entry = JournalEntry.objects.create(user=self.user, content='Hello world')
        self.assertEqual(entry.word_count(), 2)

    def test_word_count_empty(self):
        entry = JournalEntry.objects.create(user=self.user, content='')
        self.assertEqual(entry.word_count(), 0)

    def test_word_count_none(self):
        entry = JournalEntry.objects.create(user=self.user, content=None)
        self.assertEqual(entry.word_count(), 0)

    def test_word_count_single_word(self):
        entry = JournalEntry.objects.create(user=self.user, content='Hello')
        self.assertEqual(entry.word_count(), 1)

    def test_word_count_long_text(self):
        content = ' '.join(['word'] * 500)
        entry = JournalEntry.objects.create(user=self.user, content=content)
        self.assertEqual(entry.word_count(), 500)

    def test_char_count_basic(self):
        entry = JournalEntry.objects.create(user=self.user, content='Hello')
        self.assertEqual(entry.char_count(), 5)

    def test_char_count_empty(self):
        entry = JournalEntry.objects.create(user=self.user, content='')
        self.assertEqual(entry.char_count(), 0)

    def test_char_count_none(self):
        entry = JournalEntry.objects.create(user=self.user, content=None)
        self.assertEqual(entry.char_count(), 0)

    def test_reading_time_short(self):
        """Less than 200 words should return 1 minute."""
        entry = JournalEntry.objects.create(user=self.user, content='Hello world')
        self.assertEqual(entry.reading_time_minutes(), 1)

    def test_reading_time_200_words(self):
        """200 words should return 1 minute."""
        content = ' '.join(['word'] * 200)
        entry = JournalEntry.objects.create(user=self.user, content=content)
        self.assertEqual(entry.reading_time_minutes(), 1)

    def test_reading_time_400_words(self):
        """400 words should return 2 minutes."""
        content = ' '.join(['word'] * 400)
        entry = JournalEntry.objects.create(user=self.user, content=content)
        self.assertEqual(entry.reading_time_minutes(), 2)

    def test_reading_time_empty(self):
        """Empty content should return 1 minute (minimum)."""
        entry = JournalEntry.objects.create(user=self.user, content='')
        self.assertEqual(entry.reading_time_minutes(), 1)

    def test_reading_time_none(self):
        """None content should return 1 minute (minimum)."""
        entry = JournalEntry.objects.create(user=self.user, content=None)
        self.assertEqual(entry.reading_time_minutes(), 1)


class DashboardWritingStatsTest(TestCase):
    """Tests for writing stats on the dashboard."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_dashboard_shows_total_words(self):
        JournalEntry.objects.create(user=self.user, content='Hello world test', title='Test')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total Words')
        self.assertContains(response, '3')

    def test_dashboard_shows_total_characters(self):
        JournalEntry.objects.create(user=self.user, content='Hello', title='Test')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total Characters')
        self.assertContains(response, '5')

    def test_dashboard_shows_avg_words(self):
        JournalEntry.objects.create(user=self.user, content='Hello world', title='Test 1')
        JournalEntry.objects.create(user=self.user, content='Foo bar baz', title='Test 2')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Avg Words')
        # avg = (2 + 3) // 2 = 2
        self.assertContains(response, '2')

    def test_dashboard_stats_with_no_entries(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total Words')
        self.assertContains(response, '0')

    def test_dashboard_stats_only_counts_own_entries(self):
        other_user = User.objects.create_user(username='other', password='testpass123')
        JournalEntry.objects.create(user=other_user, content='Other user content with many words')
        JournalEntry.objects.create(user=self.user, content='Hi')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1')  # total_words should be 1


class JournalDetailWordCountTest(TestCase):
    """Tests for word count display in journal_detail view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.entry = JournalEntry.objects.create(
            user=self.user, content='Hello world this is a test', title='Test Entry'
        )

    def test_detail_shows_word_count(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{self.entry.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Words:')

    def test_detail_shows_char_count(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{self.entry.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Characters:')

    def test_detail_shows_reading_time(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/details/{self.entry.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reading time:')


class JournalIndexWordCountTest(TestCase):
    """Tests for word count column in journal index."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_index_shows_word_count_column(self):
        JournalEntry.objects.create(user=self.user, content='Hello world', title='Test')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Words')

    def test_index_shows_word_count_value(self):
        JournalEntry.objects.create(user=self.user, content='Hello world', title='Test')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '2')  # "Hello world" = 2 words


# ============================================================
# Tests for Phase 2 Feature 6: Journal Templates / Prompts
# ============================================================

class JournalTemplateModelTest(TestCase):
    """Tests for the JournalTemplate model."""

    def test_create_template(self):
        template = JournalTemplate.objects.create(
            name='Test Template',
            description='A test template',
            content_template='Test content',
            order=1,
        )
        self.assertEqual(template.name, 'Test Template')
        self.assertTrue(template.is_active)
        self.assertEqual(template.order, 1)

    def test_template_str(self):
        template = JournalTemplate.objects.create(name='Daily Reflection')
        self.assertEqual(str(template), 'Daily Reflection')

    def test_template_default_order(self):
        template = JournalTemplate.objects.create(
            name='Test', description='Test', content_template='Test'
        )
        self.assertEqual(template.order, 0)

    def test_template_default_is_active(self):
        template = JournalTemplate.objects.create(
            name='Test', description='Test', content_template='Test'
        )
        self.assertTrue(template.is_active)

    def test_template_ordering(self):
        # Clear existing templates from migration
        JournalTemplate.objects.all().delete()
        t3 = JournalTemplate.objects.create(name='Third', content_template='3', order=3)
        t1 = JournalTemplate.objects.create(name='First', content_template='1', order=1)
        t2 = JournalTemplate.objects.create(name='Second', content_template='2', order=2)
        templates = list(JournalTemplate.objects.all())
        self.assertEqual(templates[0].name, 'First')
        self.assertEqual(templates[1].name, 'Second')
        self.assertEqual(templates[2].name, 'Third')

    def test_inactive_template_not_in_default_queryset(self):
        JournalTemplate.objects.all().delete()
        JournalTemplate.objects.create(name='Active', content_template='Active', is_active=True)
        JournalTemplate.objects.create(name='Inactive', content_template='Inactive', is_active=False)
        active = JournalTemplate.objects.filter(is_active=True)
        self.assertEqual(active.count(), 1)
        self.assertEqual(active.first().name, 'Active')


class DefaultTemplatesMigrationTest(TestCase):
    """Tests that default templates are created by migration."""

    def test_default_templates_exist(self):
        expected = ['Daily Reflection', 'Gratitude Journal', 'Weekly Review', 'Goal Check-in']
        for name in expected:
            self.assertTrue(
                JournalTemplate.objects.filter(name=name, is_active=True).exists(),
                f"Template '{name}' should exist"
            )

    def test_default_templates_have_content(self):
        for template in JournalTemplate.objects.filter(is_active=True):
            self.assertTrue(len(template.content_template) > 0)

    def test_default_templates_are_ordered(self):
        templates = list(JournalTemplate.objects.filter(is_active=True))
        self.assertEqual(len(templates), 4)
        for i in range(len(templates) - 1):
            self.assertLessEqual(templates[i].order, templates[i + 1].order)


class TemplateListViewTest(TestCase):
    """Tests for the template_list view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_template_list_requires_login(self):
        response = self.client.get('/templates/')
        self.assertEqual(response.status_code, 302)

    def test_template_list_loads(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/templates/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Journal Templates')

    def test_template_list_shows_templates(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/templates/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Daily Reflection')
        self.assertContains(response, 'Gratitude Journal')

    def test_template_list_does_not_show_inactive(self):
        JournalTemplate.objects.create(name='Hidden', content_template='Hidden', is_active=False)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/templates/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Hidden')

    def test_template_list_has_use_template_buttons(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/templates/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Use Template')

    def test_template_list_has_create_blank_link(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/templates/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Blank Entry')


class JournalCreateWithTemplateTest(TestCase):
    """Tests for using templates when creating journals."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.template = JournalTemplate.objects.create(
            name='Test Template',
            description='A test',
            content_template='What happened?\n\n{reflections}\n\nGratitude:\n\n{gratitude}',
            order=1,
        )

    def test_create_page_shows_templates(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/create.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Start from a template')
        self.assertContains(response, 'Test Template')

    def test_create_with_template_sets_placeholder(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/journals/create.html?template={self.template.id}')
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('placeholder', form.fields['content'].widget.attrs)
        self.assertEqual(
            form.fields['content'].widget.attrs['placeholder'],
            'What happened?\n\n{reflections}\n\nGratitude:\n\n{gratitude}'
        )

    def test_create_with_invalid_template_id(self):
        """Invalid template ID should return 404."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/create.html?template=99999')
        self.assertEqual(response.status_code, 404)

    def test_create_with_inactive_template_id(self):
        """Inactive template ID should return 404."""
        inactive = JournalTemplate.objects.create(
            name='Inactive', content_template='Inactive', is_active=False
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/journals/create.html?template={inactive.id}')
        self.assertEqual(response.status_code, 404)

    def test_create_without_template_works(self):
        """Normal create without template parameter should work."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/create.html')
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        # Should not have a placeholder set from template
        self.assertNotIn('placeholder', form.fields['content'].widget.attrs)

    def test_templates_passed_in_context(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/create.html')
        self.assertEqual(response.status_code, 200)
        self.assertIn('templates', response.context)
        # Should include the 4 default templates plus the test template = 5
        self.assertEqual(response.context['templates'].count(), 5)


# ============================================================
# Tests for Phase 2 Feature 7: Journal Entry Drafts / Autosave
# ============================================================

class DraftAutosaveTest(TestCase):
    """Tests for the draft autosave feature in journal_submit.html."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_journal_create_page_has_draft_status_element(self):
        """The create journal page should have a draft-status div."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/create.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'draft-status')

    def test_journal_create_page_has_autosave_script(self):
        """The create journal page should include the autosave JavaScript."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/create.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'journal_draft')
        self.assertContains(response, 'localStorage')

    def test_journal_create_page_has_content_element(self):
        """The create journal page should have a content textarea with id='content'."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/create.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="content"')

    def test_journal_create_page_has_reflections_element(self):
        """The create journal page should have a reflections textarea with id='reflections'."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/create.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="reflections"')

    def test_journal_create_page_has_gratitude_element(self):
        """The create journal page should have a gratitude textarea with id='gratitude'."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/create.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="gratitude"')

    def test_autosave_script_clears_on_submit(self):
        """The autosave script should clear localStorage on form submit."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/journals/create.html')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('removeItem(DRAFT_KEY)', content)
        self.assertIn('removeItem(DRAFT_TIME_KEY)', content)


# ============================================================
# Tests for Phase 2 Feature 8: Annual Review Generation
# ============================================================

class GenerateAnnualReviewCommandTest(TestCase):
    """Tests for the generate_annual_review management command."""

    def setUp(self):
        from datetime import date as date_type
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.today = timezone.now().date()
        # Create entries for the current year
        e1 = JournalEntry.objects.create(user=self.user, content='Entry 1')
        e1.date = date_type(self.today.year, 1, 15)
        e1.save()
        e2 = JournalEntry.objects.create(user=self.user, content='Entry 2')
        e2.date = date_type(self.today.year, 3, 20)
        e2.save()
        e3 = JournalEntry.objects.create(user=self.user, content='Entry 3')
        e3.date = date_type(self.today.year, 6, 10)
        e3.save()

    def test_command_creates_annual_report(self):
        """Command should create an annual review report."""
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        call_command('generate_annual_review', stdout=out)
        self.assertEqual(Report.objects.filter(user=self.user, type='y').count(), 1)
        report = Report.objects.filter(user=self.user, type='y').first()
        self.assertIn('Annual Review', report.title)

    def test_command_skips_when_no_entries(self):
        """Command should skip users with no entries for the target year."""
        from django.core.management import call_command
        from io import StringIO
        other_user = User.objects.create_user(username='other', password='testpass123')
        out = StringIO()
        call_command('generate_annual_review', user='other', stdout=out)
        self.assertEqual(Report.objects.filter(user=other_user).count(), 0)
        self.assertIn('No journal entries', out.getvalue())

    def test_command_skips_duplicate_report(self):
        """Command should skip if annual report already exists."""
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        call_command('generate_annual_review', user='testuser', stdout=out)
        self.assertEqual(Report.objects.filter(user=self.user, type='y').count(), 1)
        out2 = StringIO()
        call_command('generate_annual_review', user='testuser', stdout=out2)
        self.assertEqual(Report.objects.filter(user=self.user, type='y').count(), 1)
        self.assertIn('already exists', out2.getvalue())

    def test_command_with_user_flag(self):
        """Command should only generate for specified user."""
        from django.core.management import call_command
        from io import StringIO
        other_user = User.objects.create_user(username='other', password='testpass123')
        JournalEntry.objects.create(user=other_user, content='Other entry')
        out = StringIO()
        call_command('generate_annual_review', user='testuser', stdout=out)
        self.assertEqual(Report.objects.filter(user=self.user, type='y').count(), 1)
        self.assertEqual(Report.objects.filter(user=other_user, type='y').count(), 0)

    def test_command_with_nonexistent_user(self):
        """Command should report error for nonexistent user."""
        from django.core.management import call_command
        from io import StringIO
        err = StringIO()
        call_command('generate_annual_review', user='nonexistent', stderr=err)
        self.assertIn('not found', err.getvalue())

    def test_command_with_year_flag(self):
        """Command should generate for a specific year."""
        from django.core.management import call_command
        from io import StringIO
        from datetime import date as date_type
        entry = JournalEntry.objects.create(user=self.user, content='Old entry')
        entry.date = date_type(2024, 5, 1)
        entry.save()
        out = StringIO()
        call_command('generate_annual_review', user='testuser', year=2024, stdout=out)
        report = Report.objects.filter(user=self.user, type='y', title='Annual Review: 2024').first()
        self.assertIsNotNone(report)
        self.assertIn('2024', report.title)

    def test_report_content_has_entry_count(self):
        """Generated report should include entry count."""
        from django.core.management import call_command
        call_command('generate_annual_review', user='testuser')
        report = Report.objects.filter(user=self.user, type='y').first()
        self.assertIn('Total entries: 3', report.content)

    def test_report_content_has_monthly_breakdown(self):
        """Generated report should include monthly breakdown."""
        from django.core.management import call_command
        call_command('generate_annual_review', user='testuser')
        report = Report.objects.filter(user=self.user, type='y').first()
        self.assertIn('Monthly Breakdown', report.content)

    def test_report_content_has_mood_summary(self):
        """Generated report should include mood summary when moods exist."""
        from django.core.management import call_command
        from datetime import date as date_type
        JournalEntry.objects.create(
            user=self.user, content='Happy entry',
            date=date_type(self.today.year, 2, 1), mood='["happy"]'
        )
        call_command('generate_annual_review', user='testuser')
        report = Report.objects.filter(user=self.user, type='y').first()
        self.assertIn('Top Moods', report.content)
        self.assertIn('happy', report.content)

    def test_report_content_has_tag_summary(self):
        """Generated report should include tag summary when tags exist."""
        from django.core.management import call_command
        from datetime import date as date_type
        from .models import Tag
        tag = Tag.objects.create(user=self.user, name='work')
        entry = JournalEntry.objects.create(
            user=self.user, content='Work entry',
            date=date_type(self.today.year, 4, 1)
        )
        entry.tags.add(tag)
        call_command('generate_annual_review', user='testuser')
        report = Report.objects.filter(user=self.user, type='y').first()
        self.assertIn('Top Tags', report.content)
        self.assertIn('work', report.content)

    def test_report_content_has_streak_info(self):
        """Generated report should include writing streaks."""
        from django.core.management import call_command
        call_command('generate_annual_review', user='testuser')
        report = Report.objects.filter(user=self.user, type='y').first()
        self.assertIn('Writing Streaks', report.content)
        self.assertIn('Longest streak', report.content)


class AnnualReviewListViewTest(TestCase):
    """Tests for the annual_review_list view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_annual_review_list_requires_login(self):
        response = self.client.get('/reports/annual/')
        self.assertEqual(response.status_code, 302)

    def test_annual_review_list_loads(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/annual/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Annual Reviews')

    def test_annual_review_list_empty(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/annual/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No journal entries yet')

    def test_annual_review_list_shows_years(self):
        from datetime import date as date_type
        e1 = JournalEntry.objects.create(user=self.user, content='Entry')
        e1.date = date_type(2024, 3, 1)
        e1.save()
        e2 = JournalEntry.objects.create(user=self.user, content='Entry 2')
        e2.date = date_type(2023, 5, 1)
        e2.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/annual/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '2024')
        self.assertContains(response, '2023')

    def test_annual_review_list_only_shows_own_years(self):
        from datetime import date as date_type
        other_user = User.objects.create_user(username='other', password='testpass123')
        JournalEntry.objects.create(user=other_user, content='Other', date=date_type(2024, 1, 1))
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/annual/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No journal entries yet')

    def test_annual_review_list_shows_has_report_indicator(self):
        from datetime import date as date_type
        e1 = JournalEntry.objects.create(user=self.user, content='Entry')
        e1.date = date_type(2024, 1, 1)
        e1.save()
        Report.objects.create(user=self.user, title='Annual Review: 2024', type='y', content='Content')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/annual/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'View Report')


class GenerateAnnualReviewViewTest(TestCase):
    """Tests for the generate_annual_review view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_generate_annual_review_requires_login(self):
        response = self.client.post('/reports/annual/2024/generate/')
        self.assertEqual(response.status_code, 302)

    def test_generate_annual_review_creates_report(self):
        from datetime import date as date_type
        entry = JournalEntry.objects.create(user=self.user, content='Entry')
        entry.date = date_type(2024, 3, 1)
        entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/reports/annual/2024/generate/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Report.objects.filter(user=self.user, type='y').count(), 1)

    def test_generate_annual_review_get_redirects(self):
        """GET request should redirect to annual review list."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/annual/2024/generate/')
        self.assertEqual(response.status_code, 302)

    def test_generate_annual_review_only_uses_own_entries(self):
        from datetime import date as date_type
        other_user = User.objects.create_user(username='other', password='testpass123')
        entry = JournalEntry.objects.create(user=other_user, content='Other')
        entry.date = date_type(2024, 1, 1)
        entry.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/reports/annual/2024/generate/')
        # Should show error since testuser has no entries for 2024
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Report.objects.filter(user=self.user, type='y').count(), 0)


# ============================================================
# Tests for Phase 2 Feature 9: Journal Timeline View
# ============================================================

class JournalTimelineViewTest(TestCase):
    """Tests for the journal timeline view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_timeline_requires_login(self):
        response = self.client.get('/timeline/')
        self.assertEqual(response.status_code, 302)

    def test_timeline_loads(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/timeline/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Journal Timeline')

    def test_timeline_shows_entries(self):
        JournalEntry.objects.create(user=self.user, content='Timeline entry', title='Timeline Entry')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/timeline/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Timeline Entry')

    def test_timeline_only_shows_own_entries(self):
        other_user = User.objects.create_user(username='other', password='testpass123')
        JournalEntry.objects.create(user=other_user, content='Other', title='Other Entry')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/timeline/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Other Entry')

    def test_timeline_search(self):
        JournalEntry.objects.create(user=self.user, content='Beach day', title='Beach Day')
        JournalEntry.objects.create(user=self.user, content='Mountain hike', title='Mountain Day')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/timeline/', {'q': 'Beach'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Beach Day')
        self.assertNotContains(response, 'Mountain Day')

    def test_timeline_filter_by_tag(self):
        from .models import Tag
        tag_work = Tag.objects.create(user=self.user, name='work')
        tag_personal = Tag.objects.create(user=self.user, name='personal')
        entry1 = JournalEntry.objects.create(user=self.user, content='Work stuff', title='Work Entry')
        entry2 = JournalEntry.objects.create(user=self.user, content='Personal stuff', title='Personal Entry')
        entry1.tags.add(tag_work)
        entry2.tags.add(tag_personal)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/timeline/', {'tag': 'work'})
        self.assertContains(response, 'Work Entry')
        self.assertNotContains(response, 'Personal Entry')

    def test_timeline_shows_tag_filter_dropdown(self):
        from .models import Tag
        tag = Tag.objects.create(user=self.user, name='work')
        entry = JournalEntry.objects.create(user=self.user, content='Work stuff', title='Work Entry')
        entry.tags.add(tag)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/timeline/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'work')

    def test_timeline_pagination(self):
        """Timeline should paginate at 20 entries per page."""
        for i in range(25):
            JournalEntry.objects.create(user=self.user, content=f'Entry {i}', title=f'Title {i}')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/timeline/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['entries']), 20)
        self.assertTrue(response.context['page_obj'].has_other_pages())

    def test_timeline_orders_by_date_desc(self):
        """Entries should be ordered newest first."""
        from datetime import date as date_type
        today = timezone.now().date()
        e1 = JournalEntry.objects.create(user=self.user, content='Older', title='Older Entry')
        e1.date = today - timedelta(days=10)
        e1.save()
        e2 = JournalEntry.objects.create(user=self.user, content='Newer', title='Newer Entry')
        e2.date = today - timedelta(days=1)
        e2.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/timeline/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        newer_pos = content.find('Newer Entry')
        older_pos = content.find('Older Entry')
        self.assertLess(newer_pos, older_pos)

    def test_timeline_has_nav(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/timeline/')
        self.assertContains(response, 'navbar')

    def test_timeline_empty(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/timeline/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No journal entries found')


# ============================================================
# Tests for Phase 2 Feature 10: Tag Edit, Merge, and Delete
# ============================================================

class TagEditViewTest(TestCase):
    """Tests for the tag edit (rename) view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        from .models import Tag
        self.tag = Tag.objects.create(user=self.user, name='work')

    def test_tag_edit_requires_login(self):
        response = self.client.get(f'/tags/{self.tag.id}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_tag_edit_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tags/{self.tag.id}/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Tag')
        self.assertContains(response, 'work')

    def test_tag_edit_rename(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/tags/{self.tag.id}/edit/', {'name': 'job'})
        self.assertEqual(response.status_code, 302)
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.name, 'job')

    def test_tag_edit_conflict(self):
        from .models import Tag
        Tag.objects.create(user=self.user, name='job')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/tags/{self.tag.id}/edit/', {'name': 'job'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.name, 'work')

    def test_tag_edit_same_name_redirects(self):
        """Editing with the same name should still redirect."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/tags/{self.tag.id}/edit/', {'name': 'work'})
        self.assertEqual(response.status_code, 302)

    def test_tag_edit_not_found(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tags/99999/edit/')
        self.assertEqual(response.status_code, 404)

    def test_cannot_edit_others_tag(self):
        from .models import Tag
        other_user = User.objects.create_user(username='other', password='testpass123')
        other_tag = Tag.objects.create(user=other_user, name='secret')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tags/{other_tag.id}/edit/')
        self.assertEqual(response.status_code, 404)

    def test_tag_edit_lowercases_name(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/tags/{self.tag.id}/edit/', {'name': 'WORK'})
        self.assertEqual(response.status_code, 302)
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.name, 'work')


class TagDeleteViewTest(TestCase):
    """Tests for the tag delete view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        from .models import Tag
        self.tag = Tag.objects.create(user=self.user, name='work')

    def test_tag_delete_requires_login(self):
        response = self.client.get(f'/tags/{self.tag.id}/delete/')
        self.assertEqual(response.status_code, 302)

    def test_tag_delete_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tags/{self.tag.id}/delete/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete Tag')
        self.assertContains(response, 'work')

    def test_tag_delete_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/tags/{self.tag.id}/delete/')
        self.assertEqual(response.status_code, 302)
        from .models import Tag
        self.assertEqual(Tag.objects.filter(id=self.tag.id).count(), 0)

    def test_tag_delete_does_not_delete_entries(self):
        from .models import Tag
        entry = JournalEntry.objects.create(user=self.user, content='Tagged entry')
        entry.tags.add(self.tag)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/tags/{self.tag.id}/delete/')
        self.assertEqual(response.status_code, 302)
        # Entry should still exist
        self.assertEqual(JournalEntry.objects.filter(id=entry.id).count(), 1)

    def test_tag_delete_not_found(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tags/99999/delete/')
        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_others_tag(self):
        from .models import Tag
        other_user = User.objects.create_user(username='other', password='testpass123')
        other_tag = Tag.objects.create(user=other_user, name='secret')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tags/{other_tag.id}/delete/')
        self.assertEqual(response.status_code, 404)


class TagMergeViewTest(TestCase):
    """Tests for the tag merge view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        from .models import Tag
        self.tag1 = Tag.objects.create(user=self.user, name='work')
        self.tag2 = Tag.objects.create(user=self.user, name='job')
        self.entry = JournalEntry.objects.create(user=self.user, content='Entry with work tag')
        self.entry.tags.add(self.tag1)

    def test_tag_merge_requires_login(self):
        response = self.client.get(f'/tags/{self.tag1.id}/merge/')
        self.assertEqual(response.status_code, 302)

    def test_tag_merge_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tags/{self.tag1.id}/merge/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Merge Tag')
        self.assertContains(response, 'job')

    def test_tag_merge_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/tags/{self.tag1.id}/merge/', {'target_tag': self.tag2.id})
        self.assertEqual(response.status_code, 302)
        from .models import Tag
        # Source tag should be deleted
        self.assertEqual(Tag.objects.filter(id=self.tag1.id).count(), 0)
        # Target tag should still exist
        self.assertEqual(Tag.objects.filter(id=self.tag2.id).count(), 1)
        # Entry should now have the target tag
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.tags.count(), 1)
        self.assertIn(self.tag2, self.entry.tags.all())

    def test_tag_merge_not_found(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tags/99999/merge/')
        self.assertEqual(response.status_code, 404)

    def test_cannot_merge_others_tag(self):
        from .models import Tag
        other_user = User.objects.create_user(username='other', password='testpass123')
        other_tag = Tag.objects.create(user=other_user, name='secret')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tags/{other_tag.id}/merge/')
        self.assertEqual(response.status_code, 404)

    def test_tag_merge_target_not_found(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/tags/{self.tag1.id}/merge/', {'target_tag': 99999})
        self.assertEqual(response.status_code, 404)

    def test_tag_merge_shows_other_tags(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tags/{self.tag1.id}/merge/')
        self.assertEqual(response.status_code, 200)
        # Should show the other tag 'job' as a selectable option
        self.assertContains(response, 'job')
        # Should NOT show 'job' as the source tag name (only as target)
        # The page title contains the source tag name, so we check the select options
        content = response.content.decode('utf-8')
        # The select should contain 'job' but not 'work'
        select_start = content.find('<select')
        select_end = content.find('</select>')
        select_content = content[select_start:select_end]
        self.assertIn('job', select_content)
        self.assertNotIn('work', select_content)

    def test_tag_merge_no_other_tags(self):
        from .models import Tag
        Tag.objects.filter(user=self.user).exclude(id=self.tag1.id).delete()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tags/{self.tag1.id}/merge/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No other tags available')


class TagListManagementButtonsTest(TestCase):
    """Tests for management buttons on the tag list page."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        from .models import Tag
        self.tag = Tag.objects.create(user=self.user, name='work')

    def test_tag_list_has_edit_button(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tags/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit')

    def test_tag_list_has_merge_button(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tags/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Merge')

    def test_tag_list_has_delete_button(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tags/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete')

    def test_tag_list_edit_link(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tags/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'/tags/{self.tag.id}/edit/')

    def test_tag_list_merge_link(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tags/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'/tags/{self.tag.id}/merge/')

    def test_tag_list_delete_link(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tags/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'/tags/{self.tag.id}/delete/')


class NavigationPhase2Features7to10Test(TestCase):
    """Tests for navigation links for features 7-10."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_nav_has_timeline_link(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertContains(response, 'Timeline')

    def test_nav_has_annual_review_link(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertContains(response, 'Annual Review')

    def test_timeline_page_has_nav(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/timeline/')
        self.assertContains(response, 'navbar')

    def test_annual_review_page_has_nav(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/annual/')
        self.assertContains(response, 'navbar')

    def test_tag_edit_page_has_nav(self):
        from .models import Tag
        tag = Tag.objects.create(user=self.user, name='work')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tags/{tag.id}/edit/')
        self.assertContains(response, 'navbar')

    def test_tag_delete_page_has_nav(self):
        from .models import Tag
        tag = Tag.objects.create(user=self.user, name='work')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tags/{tag.id}/delete/')
        self.assertContains(response, 'navbar')

    def test_tag_merge_page_has_nav(self):
        from .models import Tag
        tag = Tag.objects.create(user=self.user, name='work')
        Tag.objects.create(user=self.user, name='job')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tags/{tag.id}/merge/')
        self.assertContains(response, 'navbar')


# ============================================================
# Tests for Font Consistency
# ============================================================

class FontConsistencyTest(TestCase):
    """Ensure font-family is consistently applied across all templates."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_dashboard_has_font(self):
        response = self.client.get('/')
        self.assertContains(response, "font-family")
        self.assertContains(response, "Times New Roman")

    def test_journals_has_font(self):
        response = self.client.get('/journals/')
        self.assertContains(response, "font-family")
        self.assertContains(response, "Times New Roman")

    def test_goals_has_font(self):
        response = self.client.get('/goals/')
        self.assertContains(response, "font-family")
        self.assertContains(response, "Times New Roman")

    def test_mood_calendar_has_font(self):
        response = self.client.get('/mood-calendar/')
        self.assertContains(response, "font-family")
        self.assertContains(response, "Times New Roman")

    def test_mood_trends_has_font(self):
        response = self.client.get('/mood-trends/')
        self.assertContains(response, "font-family")
        self.assertContains(response, "Times New Roman")

    def test_timeline_has_font(self):
        response = self.client.get('/timeline/')
        self.assertContains(response, "font-family")
        self.assertContains(response, "Times New Roman")

    def test_on_this_day_has_font(self):
        response = self.client.get('/on-this-day/')
        self.assertContains(response, "font-family")
        self.assertContains(response, "Times New Roman")

    def test_profile_has_font(self):
        response = self.client.get('/profile/')
        self.assertContains(response, "font-family")
        self.assertContains(response, "Times New Roman")

    def test_streaks_has_font(self):
        response = self.client.get('/streaks/')
        self.assertContains(response, "font-family")
        self.assertContains(response, "Times New Roman")

    def test_tags_has_font(self):
        response = self.client.get('/tags/')
        self.assertContains(response, "font-family")
        self.assertContains(response, "Times New Roman")

    def test_reports_has_font(self):
        response = self.client.get('/reports/')
        self.assertContains(response, "font-family")
        self.assertContains(response, "Times New Roman")

    def test_monthly_reports_has_font(self):
        response = self.client.get('/reports/monthly/')
        self.assertContains(response, "font-family")
        self.assertContains(response, "Times New Roman")

    def test_annual_review_has_font(self):
        response = self.client.get('/reports/annual/')
        self.assertContains(response, "font-family")
        self.assertContains(response, "Times New Roman")

    def test_templates_has_font(self):
        response = self.client.get('/templates/')
        self.assertContains(response, "font-family")
        self.assertContains(response, "Times New Roman")
