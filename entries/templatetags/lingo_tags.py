# Template tags for translations
from django import template
from ..translations import get_translation, get_user_language

register = template.Library()

@register.simple_tag(takes_context=True)
def translate(context, key, country=None, **kwargs):
    """Translate a key based on user's language preference."""
    request = context.get('request')
    if request:
        language = get_user_language(request)
        return get_translation(key, language, country, **kwargs)
    return key

@register.simple_tag(takes_context=True)
def country_description(context, country):
    """Get country description in user's language."""
    request = context.get('request')
    if request:
        language = get_user_language(request)
        return get_translation('country_descriptions', language, country)
    return ''

@register.simple_tag(takes_context=True)
def example_sentence(context, country, example_type, term):
    """Generate example sentence for a term in user's language."""
    request = context.get('request')
    if request:
        language = get_user_language(request)
        template_key = f'example_templates.{country}.{example_type}'
        template = get_translation(template_key, language)
        if isinstance(template, str):
            return template.format(term)
    return f'Example with {term}'

@register.filter
def user_language(request):
    """Get user's language preference."""
    return get_user_language(request)
