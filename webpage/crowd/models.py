from django.db import models


class Stimulus(models.Model):
    type_choices = (("img", "Image"),
                    ("aud", "Audio"),
                    ("vid", "Video"),
                    ("txt", "Text"))
    name = models.CharField(max_length=20)
    path = models.CharField(max_length=50)
    type = models.CharField(max_length=3, choices=type_choices)

    def __str__(self):
        return self.name


class Campaign(models.Model):
    name = models.CharField(max_length=20)
    # TODO meta-informationen
    # werte für Tasklock
    current_user_count = models.IntegerField(default=0)
    max_current_user_count = models.IntegerField(default=15)
    multi_processing = models.BooleanField(default=False)

    stimuli = models.ManyToManyField(Stimulus)

    def __str__(self):
        return self.name


class Task(models.Model):
    campaign_id = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    task_nr = models.IntegerField()
    instruction = models.CharField(max_length=255, default="", blank=True)

    class Meta:
        ordering = ["task_nr"]


class Rating_block(models.Model):
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE)
    block_nr = models.IntegerField()
    # Darzustellende Stimuli in DSL
    stimuli = models.TextField()
    type_choices = (("acr", "ACR"),
                    ("text", "Text"),
                    ("choice", "Multiple Choice"))
    answer_type = models.CharField(max_length=10, choices=type_choices)

    class Meta:
        ordering = ["block_nr"]


class AnswerChoices(models.Model):
    rating_block_id = models.ForeignKey(Rating_block, on_delete=models.CASCADE)
    # Darzustellende Multiple Choice Felder in DSL
    choice = models.TextField()


class Worker(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class Answer(models.Model):
    rating_block_id = models.ForeignKey(Rating_block, on_delete=models.CASCADE)
    worker_id = models.ForeignKey(Worker, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)


class WorkerProgress(models.Model):
    worker_id = models.ForeignKey(Worker, on_delete=models.CASCADE)
    campaign_id = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    current_task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=True)
    start_time = models.DateField()
    end_time = models.DateField(default=0, blank=True)
