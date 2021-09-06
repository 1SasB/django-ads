#from django.shortcuts import render
from ads.models import Ad,Comment,Fav
from ads.owner import OwnerListView,OwnerDetailView,OwnerCreateView,OwnerUpdateView,OwnerDeleteView
from ads.forms import CreateForm,CommentForm
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy,reverse
from django.db.models import Q
from django.contrib.humanize.templatetags.humanize import naturaltime
# Create your views here.

class AdListView(OwnerListView):
    model = Ad
    template_name = "ads/ad_list.html"

    # def get(self,request):
    #     ad_list = Ad.objects.all()
    #     favorites = list()
    #     if request.user.is_authenticated:
    #         rows = request.user.favourite_ads.values('id')
    #         favorites = [row['id'] for row in rows]
    #     ctx = {'ad_list':ad_list,'favorites':favorites}
    #     return render(request,self.template_name,ctx)

    def get(self, request) :
        strval =  request.GET.get("search", False)
        favorites = list()
        if request.user.is_authenticated:
            rows = request.user.favourite_ads.values('id')
            favorites = [row['id'] for row in rows]
        if strval :
            # Simple title-only search
            # objects = Post.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]

            # Multi-field search
            # __icontains for case-insensitive search
            query = Q(title__icontains=strval) 
            query.add(Q(text__icontains=strval), Q.OR)
            ad_list = Ad.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else :
            ad_list = Ad.objects.all().order_by('-updated_at')[:10]

        # Augment the post_list
        for obj in ad_list:
            obj.natural_updated = naturaltime(obj.updated_at)
        
        ctx = {'ad_list':ad_list,'favorites':favorites}
        return render(request,self.template_name,ctx)



class AdDetailView(View):
    template_name = 'ads/ad_details.html'
    def get(self,request,pk):
        x = get_object_or_404(Ad,id=pk)
        comments = Comment.objects.filter(ad=x).order_by('updated_at')
        print("got comments object")
        form = CommentForm()
        print("got comment form")
        context = {'comments':comments,'comment_form':form,'ad':x}
        return render(request,self.template_name,context)

class CommentCreateView(LoginRequiredMixin,View):
    def post(self,request,pk):
        # ad = get_object_or_404(Ad,id=pk)
        # form = CommentForm(request.POST or None)

        # form.save(commit=False)
        # form.owner = self.request.user
        # form.save()
        a = get_object_or_404(Ad, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, ad=a)
        comment.save()
        return redirect(reverse('ads:ad_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment


# class AdCreateView(OwnerCreateView):
#     model = Ad
#     fields = ['title','price','text']

# class AdUpdateView(OwnerUpdateView):
#     model = Ad
#     fields = ['title','price','text']

class AdCreateView(LoginRequiredMixin, View):
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:all')

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)
        print(request.POST)
        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        pic = form.save(commit=False)
        pic.owner = self.request.user
        pic.save()
        return redirect(self.success_url)


class AdUpdateView(LoginRequiredMixin, View):
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:all')

    def get(self, request, pk):
        ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(instance=ad)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk):
        ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=ad)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        pic = form.save(commit=False)
        pic.save()

        return redirect(self.success_url)



class AdDeleteView(OwnerDeleteView):
    model = Ad

def stream_file(request, pk):
    ad = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = ad.pic_content_type
    response['Content-Length'] = len(ad.picture)
    print(response)
    response.write(ad.picture)
    return response


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Ad, id=pk)
        fav = Fav(user=request.user, ad=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Ad, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, ad=t).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()