import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from apps.users.models import Profile
from .models import Wallet
from .forms import WalletForm


class WalletPanelView(LoginRequiredMixin, TemplateView):
    template_name = "wallets/panel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user=self.request.user)
        context["wallets"] = Wallet.objects.filter(owner=profile)
        context["form"] = WalletForm()
        return context


class WalletCreateView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            data = json.loads(request.body)
            form = WalletForm(data)

            if not form.is_valid():
                return JsonResponse({
                    "success": False,
                    "errors": form.errors
                }, status=400)

            wallet = form.save(commit=False)
            wallet.owner = profile
            wallet.save()

            return JsonResponse({
                "success": True,
                "message": "Portfel utworzony.",
                "wallet_id": wallet.id,
                "wallet_name": wallet.name,
            }, status=201)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "errors": {"non_field": [str(e)]}
            }, status=400)


class WalletDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            profile = Profile.objects.get(user=request.user)
            wallet = get_object_or_404(Wallet, pk=pk, owner=profile)
            wallet.delete()

            return JsonResponse({
                "success": True,
                "message": "Portfel usunięty."
            })

        except Exception as e:
            return JsonResponse({
                "success": False,
                "errors": {"non_field": [str(e)]}
            }, status=400)