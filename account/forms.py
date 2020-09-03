from django.forms import ModelForm
from .models import *

class CoachingForm(ModelForm):
    class Meta:
        model = Coaching
        fields = ['name', 'description', 'logo']


class BranchForm(ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'branch_type']


class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = '__all__'
        exclude = ['id', 'external_id']


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        exclude = ['id', 'external_id']


class CoachingFacultyMemberForm(ModelForm):
    class Meta:
        model = CoachingFacultyMember
        fields = '__all__'
        exclude = ['id', 'external_id', 'coaching']


class BatchForm(ModelForm):
    class Meta:
        fields = '__all__'
        exclude = ['id', 'external_id']


class CoachingReviewForm(ModelForm):
    class Meta:
        fields = '__all__'
        exclude = ['id', 'external_id']
