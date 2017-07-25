from ast import literal_eval
from .dsl import getStimuli

from django.shortcuts import render
from django.http import Http404
from .models import Campaign, Stimulus, Task, Rating_block

from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the crowd's index.")


def setup(request):
    return HttpResponse("Hello, world. You're at the crowd's index.")


def finish(request):
    return HttpResponse("Hello, world. You're at the crowd's index.")

def rate(request, campaign_name, task_nr):
    try:
        task_nr = int(task_nr)
        #fetch Campaign
        campaign = Campaign.objects.get(name=campaign_name)
        #fetch Task to display | task_nr wird nicht als kontinuierlich enforced, daher sortieren dann [task_nr] nehmen
        task = Task.objects.filter(campaign_id=campaign)[task_nr]
        # fetch RatingBlocks to display
        rating_blocks = Rating_block.objects.filter(task_id=task)
        dsl = getStimuli([[literal_eval(blocks.stimuli), blocks.answer_type] for blocks in rating_blocks])
    except Campaign.DoesNotExist:
        raise Http404("Campaign %s does not exist" % campaign_name)
    except Task.DoesNotExist:
        raise Http404("Campaign %s does not exist" % campaign_name)
    except:
        raise Http404("Unknown Error")
    return render(request, "crowd/stim_rate.html", {'campaign': campaign, 'dsl' : dsl})
