from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from journalmain.models import JournalEntry, Report, User
import json
import calendar
from collections import Counter


class Command(BaseCommand):
    help = 'Generate weekly summary reports for all users'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, help='Generate report for specific username')
        parser.add_argument('--weeks', type=int, default=1, help='Number of weeks back to generate (default: 1)')
        parser.add_argument('--monthly', action='store_true', help='Generate monthly reports instead of weekly')

    def handle(self, *args, **options):
        target_user = options.get('user')

        if target_user:
            users = User.objects.filter(username=target_user)
            if not users.exists():
                self.stderr.write(f'User "{target_user}" not found.')
                return
        else:
            users = User.objects.all()

        if options['monthly']:
            for user in users:
                self.generate_monthly_reports(user)
        else:
            weeks_back = options['weeks']
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

    def generate_monthly_reports(self, user):
        """Generate monthly reports for all months that have journal entries."""
        entries = JournalEntry.objects.filter(user=user).order_by('date')
        if not entries.exists():
            self.stdout.write(f'No journal entries for {user.username}, skipping monthly reports.')
            return

        # Get unique year-month combinations
        year_months = set()
        for entry in entries:
            year_months.add((entry.date.year, entry.date.month))

        for year, month in sorted(year_months):
            month_name = calendar.month_name[month]
            title = f'Monthly Report: {month_name} {year}'

            # Check if report already exists
            existing = Report.objects.filter(
                user=user,
                type='m',
                title=title
            )
            if existing.exists():
                self.stdout.write(f'Monthly report already exists for {user.username} ({month_name} {year}), skipping.')
                continue

            # Get entries for this month
            start = date(year, month, 1)
            if month == 12:
                end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end = date(year, month + 1, 1) - timedelta(days=1)

            month_entries = entries.filter(date__gte=start, date__lte=end)
            if not month_entries.exists():
                continue

            # Generate summary
            content = self.generate_monthly_summary(month_entries, month_name, year)

            report = Report.objects.create(
                user=user,
                title=title,
                type='m',
                content=content,
            )

            # Link entries to report
            for entry in month_entries:
                entry.month_report = report
                entry.save()

            self.stdout.write(self.style.SUCCESS(
                f'Created monthly report for {user.username} ({month_name} {year}): {report.id}'
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

    def generate_monthly_summary(self, entries, month_name, year):
        """Generate a monthly summary."""
        summary = f"# Monthly Report: {month_name} {year}\n\n"
        summary += f"You wrote {entries.count()} journal entries this month.\n\n"

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
            mood_counts = Counter(all_moods)
            summary += "## Mood Summary\n\n"
            for mood, count in mood_counts.most_common(5):
                summary += f"- **{mood}**: {count} time(s)\n"
            summary += "\n"

        # Word count
        total_words = sum(len(e.content.split()) for e in entries if e.content)
        summary += "## Writing Stats\n\n"
        summary += f"- Total words written: {total_words}\n"
        summary += f"- Average words per entry: {total_words // max(entries.count(), 1)}\n\n"

        # Tag summary
        all_tags = Counter()
        for entry in entries:
            for tag in entry.tags.all():
                all_tags[tag.name] += 1
        if all_tags:
            summary += "## Top Tags\n\n"
            for tag, count in all_tags.most_common(5):
                summary += f"- **{tag}**: {count} entries\n"
            summary += "\n"

        summary += "## Entries\n\n"
        for entry in entries:
            title = entry.title or f"Entry for {entry.date}"
            summary += f"### {title} ({entry.date})\n\n"
            if entry.content:
                preview = entry.content[:200] + "..." if len(entry.content) > 200 else entry.content
                summary += f"{preview}\n\n"

        return summary
