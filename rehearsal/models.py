from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from production.models import Production, ProdUser



class Rehearsal(models.Model):
    '''稽古の1コマ分のデータ
    
    2日以上にまたがる稽古は、日ごとにコマを分割する
    '''
    production = models.ForeignKey(Production, verbose_name='PLOJECT',
        on_delete=models.CASCADE)
    date = models.DateField('DEADLINE')
    note = models.TextField('TASK', blank=True)
    member = models.CharField('STAFF', blank=True,max_length=15)
    
    CHOICES={
        (' ', ' '),
        ('Started', 'Started'),
        ('DONE!!!', 'DONE!!!'),
    }

    prog = models.CharField(max_length=10, choices=CHOICES, default='0')
    
    
    
    #def __str__(self):
        # ex. '08/30,○○公民館,会議室1'
        #return '{},{}'.format(self.date.strftime('%m/%d'), self.place)








     


