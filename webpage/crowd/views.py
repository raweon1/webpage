from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from django import forms
from django.utils.timezone import now

from .dsl import getStimuli, keywords
from .models import Campaign, Task, Rating_block, Worker, Answer, WorkerProgress, AnswerChoices

from ast import literal_eval


def index(request):
    return HttpResponse("Hello, world. You're at the crowd's index.")


def setup(request):
    #TODO max_current_user_count einbeziehen, wann wird current_user_count reduziert?
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
    campaign = None
    try:
        campaign = Campaign.objects.get(name=campaign_id)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("Campaign {} does not exist".format(campaign_id))
    worker, created = Worker.objects.get_or_create(name=worker_id)
    request.session["campaign"] = campaign_id
    request.session["worker"] = worker_id
    progress = WorkerProgress.objects.filter(worker_id=worker, campaign_id=campaign)
    if progress.count() == 0:
        progress = WorkerProgress(worker_id=worker, campaign_id=campaign)
        progress.save()
        request.session["task_nr"] = 0
        return render(request, "crowd/setup.html", {'campaign': campaign_id})
    elif not campaign.multi_processing and not progress[0].finished:
        request.session["task_nr"] = progress[0].current_task
        return HttpResponseRedirect("/crowd/rate/")
    elif campaign.multi_processing:
        for tmp in progress:
            if not tmp.finished:
                request.session["task_nr"] = tmp.current_task
                return HttpResponseRedirect("/crowd/rate/")
        progress = WorkerProgress(worker_id=worker, campaign_id=campaign)
        progress.save()
        request.session["task_nr"] = 0
        return render(request, "crowd/setup.html", {'campaign': campaign_id})
    request.session.flush()
    return HttpResponse("You already finished this campaign")


def finish(request):
    #TODO was passiert wenn eine Trap falsch beantwortet worden ist
    #TODO Seite schön machen, MW-Proof ausgeben
    tasks = Task.objects.filter(campaign_id=Campaign.objects.get(name=request.session["campaign"]))
    tmp = []
    i = 0
    progress = WorkerProgress.objects.get(worker_id=Worker.objects.get(name=request.session["worker"]),
                                          campaign_id=Campaign.objects.get(
                                              name=request.session["campaign"]),
                                          finished=False)
    progress.finished = True
    progress.end_time = now()
    progress.save()
    for task in tasks:
        rating_blocks = Rating_block.objects.filter(task_id=task)
        j = 0
        for rating_block in rating_blocks:
            answer = Answer.objects.get(rating_block_id=rating_block,
                                        worker_progress=progress)
            tmp.append({i: {j: answer}})
            j = j + 1
        i = i + 1
    trap = ""
    for task in tasks:
        if task.trap:
            rating_blocks = Rating_block.objects.filter(task_id=task)
            j = 0
            for rating_block in rating_blocks:
                answer = Answer.objects.get(rating_block_id=rating_block,
                                            worker_progress=progress)
                if not task.trap_answer == answer.answer:
                    trap = "YOU FAILED"
    request.session.flush()
    return render(request, "crowd/finish.html", {"ratings": tmp, "trap" : trap})


class HorizontalRadioSelect(forms.RadioSelect):
    template_name = "horizontal_select.html"


class RateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        mode = kwargs.pop("fields")
        mc = kwargs.pop("mc")
        super(RateForm, self).__init__(*args, **kwargs)
        i = 0
        for answer in mode:
            if answer == keywords['mode_acr']:
                acr = (("1", 1), ("2", 2), ("3", 3), ("4", 4), ("5", 5),)
                self.fields['answer_' + str(i)] = forms.ChoiceField(choices=acr, widget=HorizontalRadioSelect)
            elif answer == keywords['mode_text']:
                self.fields['answer_' + str(i)] = forms.CharField(max_length=255)
            elif answer == keywords['mode_mc']:
                self.fields['answer_' + str(i)] = forms.ModelChoiceField(queryset=AnswerChoices.objects.filter(rating_block_id=mc.pop(0)), empty_label=None)
            i += 1


def rate(request):
    try:
        task_nr = int(request.session["task_nr"])
        campaign = Campaign.objects.get(name=request.session["campaign"])
        # fetch Task to display | task_nr wird nicht als kontinuierlich enforced, daher sortieren (wird durch Meta class im Model erledigt) dann [task_nr] nehmen
        tasks = Task.objects.filter(campaign_id=campaign)
        rating_blocks = Rating_block.objects.filter(task_id=tasks[task_nr])
        # dsl ist als string gespeichert -> muss in Stimulus Objekte gewandelt werden
        dsl = getStimuli([[literal_eval(blocks.stimuli), blocks.answer_type] for blocks in rating_blocks])
        if request.method == "POST":
            form = RateForm(request.POST, fields=[rating_block[1] for rating_block in dsl], mc=[block for block in rating_blocks.filter(answer_type="multiple_choice")])
            if form.is_valid():
                progress = WorkerProgress.objects.get(worker_id=Worker.objects.get(name=request.session["worker"]),
                                                      campaign_id=Campaign.objects.get(
                                                          name=request.session["campaign"]),
                                                      finished=False)
                for answer, rating_block in zip(form.cleaned_data, rating_blocks):
                    tmp = Answer(rating_block_id=rating_block,
                                 worker_progress=progress,
                                 answer=form.cleaned_data[answer])
                    tmp.save()
                if task_nr >= tasks.__len__() - 1:
                    return HttpResponseRedirect("/crowd/finish/")
                else:
                    request.session["task_nr"] = task_nr + 1
                    progress.current_task = task_nr + 1
                    progress.save()
                    return HttpResponseRedirect("/crowd/rate/")
        else:
            form = RateForm(fields=[rating_block[1] for rating_block in dsl], mc=[block for block in rating_blocks.filter(answer_type="multiple_choice")])
    except Campaign.DoesNotExist:
        raise Http404("Campaign %s does not exist" % request.session["campaign"])
    except Task.DoesNotExist:
        raise Http404("Campaign %s does not exist" % request.session["campaign"])
    except KeyError as e:
        raise Http404("Start with setup" + str(e))
    return render(request, "crowd/stim_rate.html",
                  {'campaign': campaign, 'instruction': tasks[task_nr].instruction, 'dsl': dsl, "form": form})


def statistic(request):
    #TODO everything
    return HttpResponse("Hello")