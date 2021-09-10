from datetime import datetime, timedelta, timezone
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from .view_func import *
from .models import Production, ProdUser, Invitation


class ProdList(LoginRequiredMixin, ListView):
    '''Production のリストビュー
    
    ログインユーザの課題のみ表示するため、モデルは ProdUser
    '''
    model = ProdUser
    template_name = 'production/production_list.html'
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 座組への招待を表示するため、ビューの属性にする
        now = datetime.now(timezone.utc)
        self.invitations = Invitation.objects.filter(invitee=self.request.user,
            exp_dt__gt=now)
        
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        '''リストに表示するレコードをフィルタする
        '''
        # 自分である ProdUser を取得する
        prod_users = ProdUser.objects.filter(user=self.request.user)
        return prod_users


class ProdCreate(LoginRequiredMixin, CreateView):
    '''Production の追加ビュー
    '''
    model = Production
    fields = ('name',)
    success_url = reverse_lazy('production:prod_list')
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        # 保存したレコードを取得する
        new_prod = form.save(commit=True)
        
        # 自分を owner として公演ユーザに追加する
        prod_user = ProdUser(production=new_prod, user=self.request.user,
            is_owner=True)
        prod_user.save()
        
        messages.success(self.request, str(new_prod) + " を作成しました。")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        '''追加に失敗した時
        '''
        messages.warning(self.request, "作成できませんでした。")
        return super().form_invalid(form)


class ProdUpdate(LoginRequiredMixin, UpdateView):
    '''Production の更新ビュー
    '''
    model = Production
    fields = ('name',)
    success_url = reverse_lazy('production:prod_list')
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 所有権を検査する
        test_owner_permission(self, kwargs['pk'])
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 所有権を検査する
        test_owner_permission(self, kwargs['pk'])
        
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


class ProdDelete(LoginRequiredMixin, DeleteView):
    '''Production の削除ビュー
    '''
    model = Production
    template_name_suffix = '_delete'
    success_url = reverse_lazy('production:prod_list')
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 所有権を検査する
        test_owner_permission(self, kwargs['pk'])
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 所有権を検査する
        test_owner_permission(self, kwargs['pk'])
        
        return super().post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        '''削除した時のメッセージ
        '''
        result = super().delete(request, *args, **kwargs)
        messages.success(
            self.request, str(self.object) + " を削除しました。")
        return result


class UsrList(LoginRequiredMixin, ListView):
    '''ProdUser のリストビュー
    '''
    model = ProdUser
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # アクセス情報からメンバーを取得しアクセス権を検査する
        prod_user = accessing_prod_user(self, kwargs['prod_id'])
        if not prod_user:
            raise PermissionDenied
        
        # テンプレートから参照できるよう、ビューの属性にしておく
        self.prod_user = prod_user
        
        # 招待中のメンバーを表示するため、ビューの属性にする
        self.invitations = Invitation.objects.filter(production=prod_user.production)
        
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        '''リストに表示するレコードをフィルタする
        '''
        prod_id=self.kwargs['prod_id']
        prod_users = ProdUser.objects.filter(production__pk=prod_id)
        return prod_users
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        
        # 戻るボタン用の prod_id をセット
        context['prod_id'] = self.kwargs['prod_id']
        
        return context


class UsrUpdate(LoginRequiredMixin, UpdateView):
    '''ProdUser の更新ビュー
    '''
    model = ProdUser
    fields = ('is_editor',)
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 所有権を検査してアクセス中の公演ユーザを取得する
        prod_id = self.get_object().production.id
        prod_user = test_owner_permission(self, prod_id)
        
        # テンプレートから参照できるよう、ビューの属性にしておく
        self.prod_user = prod_user
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 所有権を検査してアクセス中の公演ユーザを取得する
        prod_id = self.get_object().production.id
        prod_user = test_owner_permission(self, prod_id)
        
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        '''更新に成功した時の遷移先を動的に与える
        '''
        prod_id = self.object.production.id
        url = reverse_lazy('production:usr_list', kwargs={'prod_id': prod_id})
        return url
    
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


class UsrDelete(LoginRequiredMixin, DeleteView):
    '''ProdUser の削除ビュー
    '''
    model = ProdUser
    template_name_suffix = '_delete'
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 所有権を検査してアクセス中の公演ユーザを取得する
        prod_id = self.get_object().production.id
        prod_user = test_owner_permission(self, prod_id)

        # 自分自身を削除することはできない
        if self.get_object() == prod_user:
            raise PermissionDenied
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 所有権を検査してアクセス中の公演ユーザを取得する
        prod_id = self.get_object().production.id
        prod_user = test_owner_permission(self, prod_id)

        # 自分自身を削除することはできない
        if self.get_object() == prod_user:
            raise PermissionDenied
        
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        '''削除に成功した時の遷移先を動的に与える
        '''
        prod_id = self.object.production.id
        url = reverse_lazy('production:usr_list', kwargs={'prod_id': prod_id})
        return url
    
    def delete(self, request, *args, **kwargs):
        '''削除した時のメッセージ
        '''
        result = super().delete(request, *args, **kwargs)
        messages.success(
            self.request, str(self.object) + " を削除しました。")
        return result


class InvtCreate(LoginRequiredMixin, CreateView):
    '''Invitation の追加ビュー
    '''
    model = Invitation
    fields = ()
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 所有権を検査してアクセス中の公演ユーザを取得する
        prod_user = test_owner_permission(self)
        
        # production を view の属性として持っておく
        # テンプレートで固定要素として表示するため
        self.production = prod_user.production
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 所有権を検査してアクセス中の公演ユーザを取得する
        prod_user = test_owner_permission(self)
        
        # フォームで入力された「招待する人の ID」
        invitee_value = request.POST['invitee_id']
        
        # それに一致するユーザを view の属性として持っておく
        user_model = get_user_model()
        invitees = user_model.objects.filter(username=invitee_value)
        if len(invitees) > 0:
            self.invitee = invitees[0]
        
        # prod_user, production を view の属性として持っておく
        # バリデーションと保存時に使うため
        self.prod_user = prod_user
        self.production = prod_user.production
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        # POST ハンドラで招待するユーザを取得できていなかったら、追加失敗
        if not hasattr(self, 'invitee'):
            return self.form_invalid(form)
        
        # 公演ユーザのユーザ ID リスト
        prod_users = ProdUser.objects.filter(production=self.production)
        prod_user_user_ids = [prod_user.user.id for prod_user in prod_users]
        
        # 招待中のユーザの ID リスト
        invitations = Invitation.objects.filter(production=self.production)
        current_invitee_ids = [invt.invitee.id for invt in invitations]
        
        # 公演ユーザや招待中のユーザを招待することは出来ない。
        if self.invitee.id in prod_user_user_ids\
            or self.invitee.id in current_invitee_ids:
            return self.form_invalid(form)
        
        # 追加しようとするレコードの各フィールドをセット
        instance = form.save(commit=False)
        instance.production = self.production
        instance.inviter = self.prod_user.user
        instance.invitee = self.invitee
        # 期限は7日
        # デフォルトで UTC で保存されるが念の為 UTC を指定
        instance.exp_dt = datetime.now(timezone.utc) + timedelta(days=7)
        
        messages.success(self.request, str(instance.invitee) + " さんを招待しました。")
        return super().form_valid(form)
    
    def get_success_url(self):
        '''追加に成功した時の遷移先を動的に与える
        '''
        prod_id = self.prod_user.production.id
        url = reverse_lazy('production:usr_list', kwargs={'prod_id': prod_id})
        return url
    
    def form_invalid(self, form):
        '''追加に失敗した時
        '''
        messages.warning(self.request, "招待できませんでした。")
        return super().form_invalid(form)


class InvtDelete(LoginRequiredMixin, DeleteView):
    '''Invitation の削除ビュー
    '''
    model = Invitation
    template_name_suffix = '_delete'
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 公演の所有者または招待の invitee であることを検査する
        invt = self.get_object()
        prod_id = invt.production.id
        prod_user = accessing_prod_user(self, prod_id)
        
        is_owner = prod_user and prod_user.is_owner
        is_invitee = self.request.user == invt.invitee
        
        if not (is_owner or is_invitee):
            raise PermissionDenied
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 公演の所有者または招待の invitee であることを検査する
        invt = self.get_object()
        prod_id = invt.production.id
        prod_user = accessing_prod_user(self, prod_id)
        
        is_owner = prod_user and prod_user.is_owner
        is_invitee = self.request.user == invt.invitee
        
        if not (is_owner or is_invitee):
            raise PermissionDenied
        
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        '''削除に成功した時の遷移先を動的に与える
        '''
        if self.kwargs['from'] == 'usr_list':
            prod_id = self.object.production.id
            url = reverse_lazy('production:usr_list', kwargs={'prod_id': prod_id})
        else:
            url = reverse_lazy('production:prod_list')
        return url
    
    def delete(self, request, *args, **kwargs):
        '''削除した時のメッセージ
        '''
        result = super().delete(request, *args, **kwargs)
        messages.success(
            self.request, str(self.object) + " を削除しました。")
        return result


class ProdJoin(LoginRequiredMixin, CreateView):
    '''公演に参加するビュー
    '''
    model = ProdUser
    fields = ('production', 'user')
    template_name = 'production/production_join.html'
    success_url = reverse_lazy('production:prod_list')
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 招待されているか検査し、参加できる公演を取得
        self.production = self.production_to_join()
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 招待されているか検査し、参加できる公演を取得
        self.production = self.production_to_join()
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        # 招待を検査
        invt_id = self.kwargs['invt_id'];
        invts = Invitation.objects.filter(id=invt_id)
        if len(invts) < 1:
            return self.form_invalid(form)
        invt = invts[0]
        
        # 保存するレコードを取得する
        new_prod_user = form.save(commit=False)
        
        # 正しい公演がセットされているか
        if new_prod_user.production != invt.production:
            return self.form_invalid(form)
        
        # 正しいユーザがセットされているか
        if new_prod_user.user != invt.invitee:
            return self.form_invalid(form)
        
        # 招待を削除
        invt.delete()
        
        messages.success(self.request, str(invt.production) + " に参加しました。")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        '''参加に失敗した時
        '''
        messages.warning(self.request, "参加できませんでした。")
        return super().form_invalid(form)
    
    def production_to_join(self):
        '''招待されているか検査し、参加できる公演を返す
        '''
        # 招待がなければ 404 エラーを投げる
        invt_id = self.kwargs['invt_id'];
        invts = Invitation.objects.filter(id=invt_id)
        if len(invts) < 1:
            raise Http404
        invt = invts[0]
        
        # 招待が期限切れなら 404 エラーを投げる
        now = datetime.now(timezone.utc)
        if now > invt.exp_dt:
            raise Http404
        
        # アクセス中のユーザが invitee でなければ PermissionDenied
        user = self.request.user
        if user != invt.invitee:
            raise PermissionDenied
        
        return invt.production
