from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from journalmain.models import JournalEntry, Report, User
import json


class Command(BaseCommand):
    help = 'Generate weekly summary reports for all users'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, help='Generate report for specific username')
        parser.add_argument('--weeks', type=int, default=1, help='Number of weeks back to generate (default: 1)')

    def handle(self, *args, **options):
        weeks_back = options['weeks']
        target_user = options.get('user')

        if target_user:
            users = User.objects.filter(username=target_user)
            if not users.exists():
                self.stderr.write(f'User "{target_user}" not found.')
                return
        else:
            users = User.objects.all()

        for user in users:
            for week_offset in range(weeks_back):
                end_date = timezone.now().date() - timedelta(weeks=week_offset)
                start_date = end_date - timedelta(days=6)

                # Check if report already exists
                existing = Report.objects.filter(
                    user=user,
                    type='w',
                    title__contains=f'{start_date} to {end_date}'
                )
                if existing.exists():
                    self.stdout.write(f'Report already exists for {user.username} ({start_date} to {end_date}), skipping.')
                    continue

                entries = JournalEntry.objects.filter(
                    user=user,
                    date__gte=start_date,
                    date__lte=end_date
                ).order_by('date')

                if not entries.exists():
                    self.stdout.write(f'No journal entries for {user.username} ({start_date} to {end_date}), skipping.')
                    continue

                # Generate summary
                content = self.generate_summary(entries, start_date, end_date)

                report = Report.objects.create(
                    user=user,
                    title=f'Weekly Report: {start_date} to {end_date}',
                    type='w',
                    content=content,
                )

                # Link entries to report
                for entry in entries:
                    entry.week_report = report
                    entry.save()

                self.stdout.write(self.style.SUCCESS(
                    f'Created weekly report for {user.username} ({start_date} to {end_date}): {report.id}'
                ))

    def generate_summary(self, entries, start_date, end_date):
        """Generate a weekly summary. Uses AI if available, otherwise generates a simple text summary."""
        from django.conf import settings

        if settings.USE_AI:
            try:
                import requests
                journal_text = ""
                for entry in entries:
                    journal_text += f"Date: {entry.date}\nTitle: {entry.title}\nContent: {entry.content}\n\n"

                prompt = (
                    f"You are a helpful journaling assistant. Review the following journal entries from {start_date} to {end_date} "
                    f"and provide a concise weekly summary. Highlight key themes, notable events, and overall mood. "
                    f"Format your response in markdown.\n\n{journal_text}"
                )
                response = requests.post(
                    settings.OLLAMA_API_URL,
                    json={'model': settings.OLLAMA_MODEL, 'stream': False, 'options': {'num_ctx': 4096}, 'prompt': prompt},
                    timeout=120
                )
                return response.json()['response']
            except Exception as e:
                self.stderr.write(f'AI generation failed: {e}. Falling back to simple summary.')

        # Fallback: simple text summary
        summary = f"# Weekly Summary: {start_date} to {end_date}\n\n"
        summary += f"## Overview\n\n"
        summary += f"You wrote {entries.count()} journal entries this week.\n\n"

        # Collect moods
        all_moods = []
        for entry in entries:
            if entry.mood:
                try:
                    moods = json.loads(entry.mood.replace("'", '"'))
                    all_moods.extend(moods)
                except (json.JSONDecodeError, AttributeError):
                    pass

        if all_moods:
            from collections import Counter
            mood_counts = Counter(all_moods)
            summary += "## Mood Summary\n\n"
            for mood, count in mood_counts.most_common(5):
                summary += f"- **{mood}**: {count} time(s)\n"
            summary += "\n"

        summary += "## Entries\n\n"
        for entry in entries:
            title = entry.title or f"Entry for {entry.date}"
            summary += f"### {title} ({entry.date})\n\n"
            if entry.content:
                # First 200 chars as preview
                preview = entry.content[:200] + "..." if len(entry.content) > 200 else entry.content
                summary += f"{preview}\n\n"

        return summary
