from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest

from django import forms

from .dsl import getStimuli, keywords
from .models import Campaign, Task, Rating_block, Worker, Answer

from ast import literal_eval


def index(request):
    return HttpResponse("Hello, world. You're at the crowd's index.")


def setup(request, campaign_name):
    campaign_id = request.GET.get("campaignid")
    worker_id = request.GET.get("workerid")
    if not (campaign_id and worker_id):
        error = '<div align="center">BadRequest 400<br>'
        if not campaign_id:
            error = error + 'Expected argument "campaignid"<br>'
        if not worker_id:
            error = error + 'Expected argument "workerid"<br>'
        error = error + "</div>"
        return HttpResponseBadRequest(error)
    request.session["campaign_id"] = campaign_id
    request.session["worker_id"] = worker_id
    Worker.objects.get_or_create(name=worker_id)
    return render(request, "crowd/setup.html", {'campaign': campaign_name})


def finish(request, campaign_name):
    tasks = Task.objects.filter(campaign_id=Campaign.objects.get(name=campaign_name))
    tmp = []
    i = 0
    for task in tasks:
        rating_blocks = Rating_block.objects.filter(task_id=task)
        j = 0
        for rating_block in rating_blocks:
            #TODO multiple ratings sind möglich (was nicht erlaubt sein dürte), sollte schon in der view abgefangen werden
            answer = Answer.objects.get(rating_block_id=rating_block,
                                           worker_id=Worker.objects.get(name=request.session["worker_id"]))
            tmp.append({i: {j: answer}})
            j = j + 1
        i = i + 1
    print(tmp)
    return render(request, "crowd/finish.html", {"campaign": campaign_name, "ratings": tmp})


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
                for answer, rating_block in zip(form.cleaned_data, rating_blocks):
                    tmp = Answer(rating_block_id=rating_block, worker_id=Worker.objects.get(name=request.session["worker_id"]), answer=form.cleaned_data[answer])
                    tmp.save()
                if task_nr >= tasks.__len__() - 1:
                    return HttpResponseRedirect("/crowd/{}/finish/".format(campaign_name))
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
    return render(request, "crowd/stim_rate.html", {'campaign': campaign, 'instruction': tasks[task_nr].instruction, 'dsl': dsl, "form": form})
