from django import template

register = template.Library()

@register.filter(name='get_quiz_score')
def get_quiz_score(quiz_data_list, quiz_title):
    for quiz_data in quiz_data_list:
        if quiz_data.get(quiz_title):
            return quiz_data[quiz_title]
    return None  # or "N/A" or 0 depending on what you want to default to

@register.filter(name='get_quiz_score')
def get_quiz_score(quiz_data_list, quiz_title):
    for quiz_data in quiz_data_list:
        if quiz_data['title'] == quiz_title:
            return quiz_data['score']
    return None  # or "N/A" or 0 depending on what you want to default to
