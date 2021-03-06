from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.core.exceptions import ObjectDoesNotExist
from django import forms
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Campaign, Task, Rating_block, Stimulus, Answer, Worker, WorkerProgress, AnswerChoices
from .dsl import validate_dsl, is_quoted, keywords
from .views import statistic

from pyparsing import ParseException

from ast import literal_eval


class AdminStatisticSite(AdminSite):
    def get_urls(self):
        urls = super(AdminStatisticSite, self).get_urls()
        my_urls = [url(r'^statistic/$', self.admin_view(statistic)), ]
        return urls + my_urls


tmp = AdminStatisticSite(name="myadmin")


admin.site.register(Answer)
admin.site.register(Worker)
admin.site.register(WorkerProgress)
admin.site.register(AnswerChoices)


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

    def __init__(self, *args, **kwargs):
        super(AdminTaskForm, self).__init__(*args, **kwargs)
        if self.initial:
            rating_blocks = Rating_block.objects.filter(task_id=self.instance)
            self.fields['dsl_field'].initial = "\n".join(
                ("\n".join(
                    str(stimuli) for stimuli in literal_eval(block.stimuli)) + "\n" + block.answer_type + (
                 "" if AnswerChoices.objects.filter(rating_block_id=block).count() == 0 else "\n" + "\n".join(
                     choice.choice for choice in AnswerChoices.objects.filter(rating_block_id=block)))) for
                block in rating_blocks)

    def clean_dsl_field(self):
        dsl = self.cleaned_data["dsl_field"].replace("\r", "")
        # falls das Feld nicht geändert wurde -> keine neue überprüfung der Syntax
        if not self.fields['dsl_field'].has_changed(data=dsl, initial=self.fields['dsl_field'].initial):
            return self.cleaned_data["dsl_field"]
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
        self.cleaned_data["dsl_field"] = str(dsl)
        return self.cleaned_data["dsl_field"]

    def save(self, commit=True):
        instance = super(AdminTaskForm, self).save(commit=commit)
        # falls die DSL nicht geändert wurde -> keine Änderung der Rating_blocks
        dsl = self.cleaned_data['dsl_field'].replace("\r", "")
        if not self.fields['dsl_field'].has_changed(data=dsl, initial=self.fields['dsl_field'].initial):
            return instance
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
def create_rating_block_from_admin_task(sender, **kwargs):
    instance = kwargs["instance"]
    if instance is not None:
        try:
            dsl = literal_eval(instance.dsl)
            Rating_block.objects.filter(task_id=instance).delete()
            rating_block_nr = 0
            for ratingblock in dsl:
                rb = Rating_block(task_id=instance, block_nr=rating_block_nr)
                rating_block_nr += 1
                rb.stimuli = ratingblock[0]
                rb.answer_type = ratingblock[1]
                rb.save()
                if ratingblock[1] == keywords['mode_mc']:
                    for mc in ratingblock[2]:
                        ac = AnswerChoices(rating_block_id=rb, choice=mc)
                        ac.save()
        except AttributeError:
            pass


@admin.register(Campaign)
class AdminCampaign(admin.ModelAdmin):
    exclude = ("current_user_count",)
    inlines = (AdminInlineTask,)

    def save_formset(self, request, form, formset, change):
        instances = formset.save()
        for instance in instances:
            try:
                instance.dsl
                instance.save()
            except AttributeError:
                pass