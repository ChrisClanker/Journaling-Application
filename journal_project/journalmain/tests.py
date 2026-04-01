from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
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
