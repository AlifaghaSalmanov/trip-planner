from django.db import models
from core.models import GenericModel
from django.utils.translation import gettext_lazy as _

# Create your models here.

class AIToken(GenericModel):
    input_token = models.PositiveIntegerField(null=True, blank=True)
    output_token = models.PositiveIntegerField(null=True, blank=True)

class AIPrompt(GenericModel):
    label = models.CharField(_('Label'), max_length=100, unique=True)
    prompt = models.CharField(_('Prompt'), max_length=300)
