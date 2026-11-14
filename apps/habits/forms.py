from django import forms
from .models import Habit
from apps.tasks.models import Category
from django.db.models import Q


class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'description', 'category', 'frequency', 'target_days_per_week', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Morning Meditation, Read 20 mins, Workout'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Why is this habit important to you?'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'target_days_per_week': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 7
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control form-control-color',
                'type': 'color'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(user__isnull=True)
            ).distinct()
        self.fields['category'].empty_label = 'Select Category (Optional)'
