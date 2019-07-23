'''
Created on Feb 18, 2015

@author: jay7958
'''
from django import template
from django.contrib.auth import get_user_model
from ..models import Answered_Survey, Engagement_Survey

Users = get_user_model
register = template.Library()


@register.inclusion_tag('defectDojo-engagement-survey/surveys.html')
def show_surveys(engagement):
    surveys = Answered_Survey.objects.filter(engagement=engagement)
    users = Users.objects.all()
    return {'surveys': surveys,
            'users': users}


@register.inclusion_tag('defectDojo-engagement-survey/add_surveys.html')
def add_surveys(engagement):
    ids = [survey.survey.id for survey in
           Answered_Survey.objects.filter(engagement=engagement)]
    surveys = Engagement_Survey.objects.exclude(
        id__in=ids)
    return {'surveys': surveys,
            'eng': engagement}
