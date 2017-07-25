from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django import forms
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Campaign, Task, Rating_block, Stimulus
from .dsl import validate_dsl, keywords, is_quoted
from pyparsing import ParseException


# TODO Campaign -> inline task zeigen nicht bisherige DSL an
# TODO Task zeigt nicht bisherige DSL an


@admin.register(Stimulus)
class AdminStimulus(admin.ModelAdmin):
    pass


class AdminInlineRating_block(admin.TabularInline):
    model = Rating_block


@admin.register(Rating_block)
class AdminRating_block(admin.ModelAdmin):
    pass


class AdminTaskForm(forms.ModelForm):
    dsl_field = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Task
        fields = "__all__"

    def clean_dsl_field(self):
        dsl = self.cleaned_data["dsl_field"]
        # Check richtige Syntax
        try:
            dsl = validate_dsl(dsl)
        except ParseException as pe:
            raise forms.ValidationError("Parsing Error :" + pe.__str__())
        # Check ob referenzierte Stimuli existieren
        for blocks in dsl:
            # stimuliblocks = blocks[0] | answer_mode = blocks[1] | evtl answer_choices = blocks[2]
            for stimulus_block in blocks[0]:
                for stimuli in stimulus_block:
                    if not is_quoted(stimuli):
                        try:
                            Stimulus.objects.get(name=stimuli)
                        except ObjectDoesNotExist:
                            raise forms.ValidationError("Stimulus %s does not exist" % stimuli)
        self.cleaned_data["dsl_field"] = dsl
        return self.cleaned_data["dsl_field"]

    def save(self, commit=True):
        instance = super(AdminTaskForm, self).save(commit=commit)
        dsl = self.cleaned_data['dsl_field']
        instance.dsl = dsl
        return instance


class AdminInlineTask(admin.StackedInline):
    model = Task
    form = AdminTaskForm
    extra = 1


@admin.register(Task)
class AdminTask(admin.ModelAdmin):
    form = AdminTaskForm
    # inlines = (AdminInlineRating_block,)


@receiver(post_save, sender=Task)
def createRatingblockFromAdminTask(sender, **kwargs):
    instance = kwargs["instance"]
    if instance is not None:
        try:
            Rating_block.objects.filter(task_id=instance).delete()
            dsl = instance.dsl
            rating_block_nr = 0
            for ratingblock in dsl:
                rb = Rating_block(task_id=instance, block_nr=rating_block_nr)
                rating_block_nr += 1
                rb.stimuli = str(ratingblock[0])
                rb.answer_type = ratingblock[1]
                rb.save()
                # TODO answerChoices
        except AttributeError:
            pass


@admin.register(Campaign)
class AdminCampaign(admin.ModelAdmin):
    exclude = ("current_user_count",)
    inlines = (AdminInlineTask,)
