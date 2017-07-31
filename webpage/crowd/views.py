from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseRedirect

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
    def __init__(self, *args, **kwargs):
        mode = kwargs.pop("fields")
        super(RateForm, self).__init__(*args, **kwargs)
        i = 0
        for answer in mode:
            if answer == keywords['mode_acr']:
                acr = (("1", 1), ("2", 2), ("3", 3), ("4", 4), ("5", 5),)
                self.fields['answer_' + str(i)] = forms.ChoiceField(choices=acr, widget=forms.RadioSelect)
            elif answer == keywords['mode_text']:
                self.fields['answer_' + str(i)] = forms.CharField(max_length=255)
            i += 1


def rate(request, campaign_name, task_nr):
    try:
        task_nr = int(task_nr)
        campaign = Campaign.objects.get(name=campaign_name)
        # fetch Task to display | task_nr wird nicht als kontinuierlich enforced, daher sortieren (wird durch Meta class im Model erledigt) dann [task_nr] nehmen
        tasks = Task.objects.filter(campaign_id=campaign)
        rating_blocks = Rating_block.objects.filter(task_id=tasks[task_nr])
        # dsl ist als string gespeichert -> muss in Stimulus Objekte gewandelt werden
        dsl = getStimuli([[literal_eval(blocks.stimuli), blocks.answer_type] for blocks in rating_blocks])
        if request.method == "POST":
            form = RateForm(request.POST, fields=[rating_block[1] for rating_block in dsl])
            if form.is_valid():
                #TODO do something with cleaned_data
                print(form.cleaned_data)
                if task_nr >= tasks.__len__() - 1:
                    #TODO redirect to finish_view
                    return HttpResponseRedirect("/crowd/finish/")
                else:
                    return HttpResponseRedirect("/crowd/{}/rate/{}".format(campaign_name, task_nr + 1))
        else:
            form = RateForm(fields=[rating_block[1] for rating_block in dsl])
    except Campaign.DoesNotExist:
        raise Http404("Campaign %s does not exist" % campaign_name)
    except Task.DoesNotExist:
        raise Http404("Campaign %s does not exist" % campaign_name)
    except:
        raise Http404("Unknown Error")
    return render(request, "crowd/stim_rate.html", {'campaign': campaign, 'dsl': dsl, "form": form})
