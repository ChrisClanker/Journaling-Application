from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from journalmain.models import JournalEntry, Report, User, Goal
from collections import Counter
import json
import calendar


class Command(BaseCommand):
    help = 'Generate annual review reports for all users'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, help='Generate report for specific username')
        parser.add_argument('--year', type=int, help='Year to generate report for (default: current year)')

    def handle(self, *args, **options):
        target_year = options.get('year') or timezone.now().year
        target_user = options.get('user')

        if target_user:
            users = User.objects.filter(username=target_user)
            if not users.exists():
                self.stderr.write(f'User "{target_user}" not found.')
                return
        else:
            users = User.objects.all()

        for user in users:
            title = f'Annual Review: {target_year}'
            existing = Report.objects.filter(user=user, type='y', title=title)
            if existing.exists():
                self.stdout.write(f'Report already exists for {user.username} ({target_year}), skipping.')
                continue

            entries = JournalEntry.objects.filter(
                user=user,
                date__year=target_year
            ).order_by('date')

            if not entries.exists():
                self.stdout.write(f'No journal entries for {user.username} in {target_year}, skipping.')
                continue

            content = self.generate_annual_summary(entries, target_year, user)

            report = Report.objects.create(
                user=user,
                title=title,
                type='y',
                content=content,
            )

            self.stdout.write(self.style.SUCCESS(
                f'Created annual review for {user.username} ({target_year}): {report.id}'
            ))

    def generate_annual_summary(self, entries, year, user):
        from datetime import timedelta

        content = f"# Annual Review: {year}\n\n"
        content += f"## Overview\n\n"
        content += f"- Total entries: {entries.count()}\n"

        total_words = sum(len(e.content.split()) for e in entries if e.content)
        content += f"- Total words written: {total_words}\n"
        content += f"- Average words per entry: {total_words // max(entries.count(), 1)}\n\n"

        # Monthly breakdown
        content += "## Monthly Breakdown\n\n"
        monthly_counts = Counter()
        for entry in entries:
            monthly_counts[entry.date.month] += 1
        for month_num in range(1, 13):
            count = monthly_counts.get(month_num, 0)
            bar = '#' * count
            content += f"- {calendar.month_name[month_num]}: {count} entries {bar}\n"
        content += "\n"

        # Mood summary
        all_moods = []
        for entry in entries:
            if entry.mood:
                try:
                    moods = json.loads(entry.mood.replace("'", '"'))
                    all_moods.extend(moods)
                except (json.JSONDecodeError, AttributeError):
                    pass

        if all_moods:
            content += "## Top Moods\n\n"
            for mood, count in Counter(all_moods).most_common(10):
                content += f"- **{mood}**: {count} time(s)\n"
            content += "\n"

        # Tag summary
        all_tags = Counter()
        for entry in entries:
            for tag in entry.tags.all():
                all_tags[tag.name] += 1
        if all_tags:
            content += "## Top Tags\n\n"
            for tag, count in all_tags.most_common(10):
                content += f"- **{tag}**: {count} entries\n"
            content += "\n"

        # Streak info
        dates = sorted(set(entries.values_list('date', flat=True)))
        longest = 1
        current = 1
        for i in range(1, len(dates)):
            if dates[i] - dates[i-1] == timedelta(days=1):
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        content += f"## Writing Streaks\n\n"
        content += f"- Longest streak: {longest} days\n\n"

        # Goal progress
        goals = Goal.objects.filter(
            user=user,
            created_at__year=year
        )
        if goals.exists():
            content += "## Goals Set This Year\n\n"
            for goal in goals:
                content += f"- **{goal.goal_title}**: {goal.progress}% complete\n"
            content += "\n"

        return content
