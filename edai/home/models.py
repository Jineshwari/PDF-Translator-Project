from django.db import models

class Dictionary(models.Model):
    name = models.CharField(max_length=255)
    # Other fields if necessary

    def __str__(self):
        return self.name


class WordPair(models.Model):
    dictionary = models.ForeignKey(Dictionary, related_name='word_pairs', on_delete=models.CASCADE)
    find_word = models.CharField(max_length=255)
    replace_word = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.find_word} -> {self.replace_word}"
