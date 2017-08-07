from pyparsing import *
from re import sub
from crowd.models import Stimulus

keywords = dict(stim="stimulus_block", answer="answer_block", mode_text="text", mode_acr="acr",
                mode_mc="multiple_choice")

stimulus = Group(OneOrMore(Suppress(Keyword(keywords['stim'])) + Group(OneOrMore(Word(printables + " "), stopOn=Keyword(keywords['stim']) ^ Keyword(keywords['answer'])))))
answer = Suppress(Keyword(keywords['answer'])) + (Keyword(keywords['mode_text']) ^ Keyword(keywords['mode_acr']) ^ (Keyword(keywords['mode_mc']) + Group(OneOrMore(Word(printables + " ")))))
validate = OneOrMore(Group(stimulus + answer))


def validate_dsl(dsl):
    return validate.parseString(dsl)


def is_quoted(str):
    return str[0] == '"' or str[0] == "'"


def getStimuli(dsl):
    #TODO Keyword random &| dynamic einbauen
    list = []
    for rating_block in dsl:
        rating_block_list = []
        tmp_list = []
        for stimulus_block in rating_block[0]:
            stimulus_block_list = []
            for stimulus in stimulus_block:
                stimulus_list = []
                if is_quoted(stimulus):
                    stimulus_list.append(Stimulus(type="txt", name=sub("['\"]", "", stimulus), path=""))
                else:
                    stimulus_list.append(Stimulus.objects.get(name=stimulus))
                stimulus_block_list.append(stimulus_list)
            tmp_list.append(stimulus_block_list)
        rating_block_list.append(tmp_list)
        rating_block_list.append(rating_block[1])
        list.append(rating_block_list)
    return list
