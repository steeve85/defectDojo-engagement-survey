'''
Created on Feb 16, 2015

@author: jay7958
'''
from django.contrib.auth import get_user_model
from django.db import models
from django_extensions.db.models import TimeStampedModel
from polymorphic.models import PolymorphicModel
from auditlog.registry import auditlog

from dojo.models import Engagement

User = get_user_model()


class Question(PolymorphicModel, TimeStampedModel):
    '''
        Represents a question.
    '''

    class Meta:
        ordering = ['order']

    order = models.PositiveIntegerField(default=1,
                                        help_text='The render order')

    optional = models.BooleanField(
        default=False,
        help_text="If selected, user doesn't have to answer this question")

    text = models.TextField(blank=False, help_text='The question text', default='')

    def __unicode__(self):
        return self.text

    def __str__(self):
        return self.text


class TextQuestion(Question):
    '''
    Question with a text answer
    '''

    def get_form(self):
        '''
        Returns the form for this model
        '''
        from .forms import TextQuestionForm
        return TextQuestionForm


class Choice(TimeStampedModel):
    '''
    Model to store the choices for multi choice questions
    '''

    order = models.PositiveIntegerField(default=1)

    label = models.TextField(default="")

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return self.label

    def __str__(self):
        return self.label


class ChoiceQuestion(Question):
    '''
    Question with answers that are chosen from a list of choices defined
    by the user.
    '''

    multichoice = models.BooleanField(default=False,
                                      help_text="Select one or more")

    choices = models.ManyToManyField(Choice)

    def get_form(self):
        '''
        Returns the form for this model
        '''

        from .forms import ChoiceQuestionForm
        return ChoiceQuestionForm


# meant to be a abstract survey, identified by name for purpose
class Engagement_Survey(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False,
                            editable=True, default='')
    description = models.TextField(editable=True, default='')
    questions = models.ManyToManyField(Question)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Engagement Survey"
        verbose_name_plural = "Engagement Surveys"
        ordering = ('-active', 'name',)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


# meant to be an answered survey tied to an engagement

class Answered_Survey(models.Model):
    # tie this to a specific engagement
    engagement = models.ForeignKey(Engagement, related_name='engagement+',
                                   null=True, blank=False, editable=True,
                                   on_delete=models.CASCADE)
    # what surveys have been answered
    survey = models.ForeignKey(Engagement_Survey, on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, related_name='assignee',
                                  null=True, blank=True, editable=True,
                                  default=None, on_delete=models.CASCADE)
    # who answered it
    responder = models.ForeignKey(User, related_name='responder',
                                  null=True, blank=True, editable=True,
                                  default=None, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    answered_on = models.DateField(null=True)

    class Meta:
        verbose_name = "Answered Engagement Survey"
        verbose_name_plural = "Answered Engagement Surveys"

    def __unicode__(self):
        return self.survey.name

    def __str__(self):
        return self.survey.name


class General_Survey(models.Model):
    survey = models.ForeignKey(Engagement_Survey, on_delete=models.CASCADE)
    num_repsonses = models.IntegerField(default=0)
    generated = models.DateField(null=False)
    expiration = models.DateField(null=False, blank=False)

    class Meta:
        verbose_name = "General Engagement Survey"
        verbose_name_plural = "General Engagement Surveys"

    def __unicode__(self):
        return self.survey.name

    def __str__(self):
        return self.survey.name


class Answer(PolymorphicModel, TimeStampedModel):
    ''' Base Answer model
    '''
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

#     content_type = models.ForeignKey(ContentType)
#     object_id = models.PositiveIntegerField()
#     content_object = generic.GenericForeignKey('content_type', 'object_id')
    answered_survey = models.ForeignKey(Answered_Survey,
                                        null=False,
                                        blank=False,
                                        on_delete=models.CASCADE)


class TextAnswer(Answer):
    answer = models.TextField(
        blank=False,
        help_text='The answer text',
        default='')

    def __unicode__(self):
        return self.answer


class ChoiceAnswer(Answer):
    answer = models.ManyToManyField(
        Choice,
        help_text='The selected choices as the answer')

    def __unicode__(self):
        if len(self.answer.all()):
            return str(self.answer.all()[0])
        else:
            return 'No Response'

# Causing issues in various places.
# auditlog.register(Answer)
# auditlog.register(Answered_Survey)
# auditlog.register(Question)
# auditlog.register(Engagement_Survey)
