#from django.forms import ModelForm, TextField, ModelMultipleChoiceField, SelectMultiple
from django import forms
from django.contrib.auth.models import User
from .models import JournalEntry, Goal


MOOD_CHOICES = [
    ('happy', 'Happy'),
    ('sad', 'Sad'),
    ('angry', 'Angry'),
    ('afraid', 'Afraid'),
    ('excited', 'Excited'),
    ('calm', 'Calm'),
    ('worried', 'Worried'),
    ('in love', 'In Love'),
    ('surprised', 'Surprised'),
    ('proud', 'Proud'),
    ('ashamed', 'Ashamed'),
    ('frustrated', 'Frustrated'),
    ('guilty', 'Guilty'),
    ('curious', 'Curious'),
    ('nostalgic', 'Nostalgic'),
    ('hopeful', 'Hopeful'),
    ('disappointed', 'Disappointed'),
    ('embarrassed', 'Embarrassed'),
    ('envious', 'Envious'),
    ('grateful', 'Grateful'),
    ('longing', 'Longing'),
    ('relieved', 'Relieved'),
    ('optimistic', 'Optimistic'),
    ('pessimistic', 'Pessimistic'),
]

class JournalForm(forms.ModelForm):
    mood = forms.MultipleChoiceField(
        choices=MOOD_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="How are you feeling? (select all that apply)"
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'tag1, tag2, tag3'}),
        help_text='Comma-separated tags'
    )

    def __init__(self, *args, **kwargs):
        self.use_ai = kwargs.pop('use_ai', True)
        super().__init__(*args, **kwargs)
        if self.use_ai:
            # Remove the mood field when AI is enabled (AI handles it)
            self.fields.pop('mood', None)

    class Meta:
        model = JournalEntry
        fields = ['content', 'reflections', 'gratitude']



class AskJournalForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user')
        # This is unhinged.
        super().__init__(*args, **kwargs)
        self.fields['journals'].queryset = JournalEntry.objects.filter(user=self.user)

    question = forms.CharField(widget=forms.Textarea, max_length=960)
    journals = forms.ModelMultipleChoiceField(queryset=JournalEntry.objects.all(), widget=forms.SelectMultiple(attrs={"size": "40"}))

    class Meta:
        fields = ['user', 'question', 'journals'] 

    

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ('goal_title', 'goal_text', 'goal_rationale', 'length', 'parent_goal')

    def clean(self):
        cleaned_data = super().clean()
        parent_goal = cleaned_data.get('parent_goal')
        if parent_goal and parent_goal == self.instance:
            raise forms.ValidationError("A goal cannot be its own parent")
        return cleaned_data
