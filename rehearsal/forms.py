from django import forms
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget
from production.models import Production, ProdUser
from .models import Rehearsal

class RhslForm(forms.ModelForm):
    '''稽古の追加・更新フォーム
    '''
    class Meta:
        model = Rehearsal
        fields = ('date', 'note','member','prog')
        widgets = {
            'date': AdminDateWidget(),
        }
    
    def __init__(self, *args, **kwargs):
        # view で追加したパラメタを抜き取る
        production = kwargs.pop('production')
        
        super().__init__(*args, **kwargs)
        
        # 稽古場は、同じ公演の稽古場のみ選択可能
        #facilities = Facility.objects.filter(production=production)
        # その施設を含む稽古場
        #places = Place.objects.filter(facility__in=facilities)
        #self.fields['place'].queryset = places
    
   

  