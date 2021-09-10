from operator import attrgetter
from django.views.generic import ListView, TemplateView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from production.models import Production
from rehearsal.models import Rehearsal
from rehearsal.forms import RhslForm
from production.view_func import *


class ProdBaseListView(LoginRequiredMixin, ListView):
    '''アクセス権を検査する ListView の Base class
    '''
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # アクセス情報から公演ユーザを取得しアクセス権を検査する
        prod_user = accessing_prod_user(self)
        if not prod_user:
            raise PermissionDenied
        
        # アクセス中の ProdUser を view の属性として持っておく
        # テンプレートで追加ボタンの有無を決めるため
        self.prod_user = prod_user
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        
        # 戻るボタン, 追加ボタン用の prod_id をセット
        context['prod_id'] = self.kwargs['prod_id']
        
        return context


class ProdBaseCreateView(LoginRequiredMixin, CreateView):
    '''アクセス権を検査する CreateView の Base class
    '''
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 編集権を検査してアクセス中の公演ユーザを取得する
        prod_user = test_edit_permission(self)
        
        # production を view の属性として持っておく
        # テンプレートで固定要素として表示するため
        self.production = prod_user.production
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 編集権を検査してアクセス中の公演ユーザを取得する
        prod_user = test_edit_permission(self)
        
        # production を view の属性として持っておく
        # 保存時にインスタンスにセットするため
        self.production = prod_user.production
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        # 追加しようとするレコードの production をセット
        instance = form.save(commit=False)
        instance.production = self.production
        
        messages.success(self.request, str(instance) + " を追加しました。")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        '''追加に失敗した時
        '''
        messages.warning(self.request, "追加できませんでした。")
        return super().form_invalid(form)


class ProdBaseUpdateView(LoginRequiredMixin, UpdateView):
    '''アクセス権を検査する UpdateView の Base class
    '''
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # production を view の属性として持っておく
        # テンプレートで固定要素として表示するため
        self.production = self.get_object().production
        
        # 編集権を検査する
        test_edit_permission(self, self.production.id)
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # production を view の属性として持っておく
        # フォームに渡してバリデーションで使うため
        self.production = self.get_object().production

        # 編集権を検査してアクセス中の公演ユーザを取得する
        prod_user = test_edit_permission(self, self.production.id)
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        messages.success(self.request, str(form.instance) + " を更新しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        '''更新に失敗した時
        '''
        messages.warning(self.request, "更新できませんでした。")
        return super().form_invalid(form)


class ProdBaseDetailView(LoginRequiredMixin, DetailView):
    '''アクセス権を検査する DetailView の Base class
    '''
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # アクセス情報から公演ユーザを取得する
        prod_id = self.get_object().production.id
        prod_user = accessing_prod_user(self, prod_id=prod_id)
        if not prod_user:
            raise PermissionDenied
        
        # アクセス中の ProdUser を view の属性として持っておく
        # テンプレートで編集ボタンの有無を決めるため
        self.prod_user = prod_user
        
        return super().get(request, *args, **kwargs)


class ProdBaseDeleteView(LoginRequiredMixin, DeleteView):
    '''アクセス権を検査する DeleteView の Base class
    '''
    template_name_suffix = '_delete'
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 編集権を検査する
        test_edit_permission(self, self.get_object().production.id)
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 編集権を検査する
        test_edit_permission(self, self.get_object().production.id)
        
        return super().post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        '''削除した時のメッセージ
        '''
        result = super().delete(request, *args, **kwargs)
        messages.success(
            self.request, str(self.object) + " を削除しました。")
        return result


class RhslTop(LoginRequiredMixin, TemplateView):
    '''Rehearsal のトップページ
    '''
    template_name = 'rehearsal/top.html'
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けたハンドラ
        '''
        # アクセス情報から公演ユーザを取得しアクセス権を検査する
        prod_user = accessing_prod_user(self)
        if not prod_user:
            raise PermissionDenied
        
        # production を view の属性として持っておく
        self.production = prod_user.production
        
        return super().get(request, *args, **kwargs)


class RhslList(ProdBaseListView):
    '''Rehearsal のリストビュー

    Template 名: rehearsal_list (default)
    '''
    model = Rehearsal
    
    def get_queryset(self):
        '''リストに表示するレコードをフィルタする
        '''
        prod_id=self.kwargs['prod_id']
        return Rehearsal.objects.filter(production__pk=prod_id)


class RhslCreate(ProdBaseCreateView):
    '''Rehearsal の追加ビュー
    '''
    model = Rehearsal
    form_class = RhslForm
    
    def get_form_kwargs(self):
        '''フォームに渡す情報を改変する
        '''
        kwargs = super().get_form_kwargs()
        
        # フォーム側でバリデーションに使うので production を渡す
        kwargs['production'] = self.production
        
        return kwargs
    
    def get_success_url(self):
        '''追加に成功した時の遷移先を動的に与える
        '''
        prod_id = self.production.id
        url = reverse_lazy('rehearsal:rhsl_list', kwargs={'prod_id': prod_id})
        return url


class RhslUpdate(ProdBaseUpdateView):
    '''Rehearsal の更新ビュー
    '''
    model = Rehearsal
    form_class = RhslForm
    
    def get_form_kwargs(self):
        '''フォームに渡す情報を改変する
        '''
        kwargs = super().get_form_kwargs()
        
        # フォーム側でバリデーションに使うので production を渡す
        kwargs['production'] = self.production
        
        return kwargs
    
    def get_success_url(self):
        '''更新に成功した時の遷移先を動的に与える
        '''
        prod_id = self.object.production.id
        url = reverse_lazy('rehearsal:rhsl_list', kwargs={'prod_id': prod_id})
        return url


class RhslDetail(ProdBaseDetailView):
    '''Rehearsal の詳細ビュー
    '''
    model = Rehearsal


class RhslDelete(ProdBaseDeleteView):
    '''Rehearsal の削除ビュー
    '''
    model = Rehearsal
    
    def get_success_url(self):
        '''削除に成功した時の遷移先を動的に与える
        '''
        prod_id = self.object.production.id
        url = reverse_lazy('rehearsal:rhsl_list', kwargs={'prod_id': prod_id})
        return url



   


















