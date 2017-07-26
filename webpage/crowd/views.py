from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse

from django import forms

from .dsl import getStimuli, keywords
from .models import Campaign, Stimulus, Task, Rating_block

from ast import literal_eval


def index(request):
    return HttpResponse("Hello, world. You're at the crowd's index.")


def setup(request):
    return HttpResponse("Hello, world. You're at the crowd's index.")


def finish(request):
    return HttpResponse("Hello, world. You're at the crowd's index.")


class RateForm(forms.Form):
    def __init__(self, answer_types, *args, **kwargs):
        super(RateForm, self).__init__(*args, **kwargs)
        i = 0
        for answer in answer_types:
            if answer == keywords['mode_acr']:
                acr = (("a1", 1), ("b2", 2), ("c3", 3), ("d4", 4), ("e5", 5),)
                self.fields["answer_" + str(i)] = forms.ChoiceField(choices=acr, widget=forms.RadioSelect)
            elif answer == keywords['mode_text']:
                self.fields['answer_' + str(i)] = forms.CharField(max_length=255)
            i += 1


def rate(request, campaign_name, task_nr):
    try:
        task_nr = int(task_nr)
        # fetch Campaign
        campaign = Campaign.objects.get(name=campaign_name)
        # fetch Task to display | task_nr wird nicht als kontinuierlich enforced, daher sortieren (wird durch Meta class im Model erledigt) dann [task_nr] nehmen
        task = Task.objects.filter(campaign_id=campaign)[task_nr]
        rating_blocks = Rating_block.objects.filter(task_id=task)
        # dsl ist als string gespeichert -> muss in Stimulus Objekte gewandelt werden
        dsl = getStimuli([[literal_eval(blocks.stimuli), blocks.answer_type] for blocks in rating_blocks])
        form = RateForm([rating_block[1] for rating_block in dsl])
    except Campaign.DoesNotExist:
        raise Http404("Campaign %s does not exist" % campaign_name)
    except Task.DoesNotExist:
        raise Http404("Campaign %s does not exist" % campaign_name)
    except:
        raise Http404("Unknown Error")
    return render(request, "crowd/stim_rate.html", {'campaign': campaign, 'dsl': dsl, "form": form})
