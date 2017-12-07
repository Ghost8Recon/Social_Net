from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse_lazy

import markdown
from articles.forms import ArticleForm
from articles.models import Article, ArticleComment
from social_net.decorators import ajax_required


def _articles(request, articles):
    paginator = Paginator(articles, 10)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)

    except PageNotAnInteger:
        articles = paginator.page(1)

    except EmptyPage:   # pragma: no cover
        articles = paginator.page(paginator.num_pages)

    popular_tags = Article.get_counted_tags()

    return render(request, 'articles/articles.html', {
        'articles': articles,
        'popular_tags': popular_tags
    })


class CreateArticle(LoginRequiredMixin, CreateView):
    """
    """
    template_name = 'articles/write.html'
    form_class = ArticleForm
    success_url = reverse_lazy('articles')

    def form_valid(self, form):
        form.instance.create_user = self.request.user
        return super(CreateArticle, self).form_valid(form)


class EditArticle(LoginRequiredMixin, UpdateView):
    template_name = 'articles/edit.html'
    model = Article
    form_class = ArticleForm
    success_url = reverse_lazy('articles')


@login_required
def articles(request):
    all_articles = Article.get_published()
    return _articles(request, all_articles)


@login_required
def article(request, slug):
    article = get_object_or_404(Article, slug=slug, status=Article.PUBLISHED)
    return render(request, 'articles/article.html', {'article': article})


@login_required
def tag(request, tag_name):
    articles = Article.objects.filter(tags__name=tag_name).filter(status='P')
    return _articles(request, articles)


@login_required
def drafts(request):
    drafts = Article.objects.filter(create_user=request.user,
                                    status=Article.DRAFT)
    return render(request, 'articles/drafts.html', {'drafts': drafts})


@login_required
@ajax_required
def preview(request):
    try:
        if request.method == 'POST':
            content = request.POST.get('content')
            html = 'Nothing to display :('
            if len(content.strip()) > 0:
                html = markdown.markdown(content, safe_mode='escape')

            return HttpResponse(html)

        else:   # pragma: no cover
            return HttpResponseBadRequest()

    except Exception:   # pragma: no cover
        return HttpResponseBadRequest()


@login_required
@ajax_required
def comment(request):
    try:
        if request.method == 'POST':
            article_id = request.POST.get('article')
            article = Article.objects.get(pk=article_id)
            comment = request.POST.get('comment')
            comment = comment.strip()
            if len(comment) > 0:
                article_comment = ArticleComment(user=request.user,
                                                 article=article,
                                                 comment=comment)
                article_comment.save()
            html = ''
            for comment in article.get_comments():
                html = '{0}{1}'.format(html, render_to_string(
                    'articles/partial_article_comment.html',
                    {'comment': comment}))

            return HttpResponse(html)

        else:   # pragma: no cover
            return HttpResponseBadRequest()

    except Exception:   # pragma: no cover
        return HttpResponseBadRequest()


# def articlce_image(request):
#     uploaded_image = False
#     try:
#         if request.GET.get('upload_image') == 'uploaded':
#             uploaded_image = True
#
#     except Exception:  # pragma: no cover
#         pass
#
#     return render(request, 'core/picture.html',
#                   {'uploaded_picture': uploaded_image})
#
# def upload_picture(request):
#     try:
#         profile_pictures = django_settings.MEDIA_ROOT + '/profile_pictures/'
#         if not os.path.exists(profile_pictures):
#             os.makedirs(profile_pictures)
#         f = request.FILES['picture']
#         filename = profile_pictures + request.user.username + '_tmp.jpg'
#         with open(filename, 'wb+') as destination:
#             for chunk in f.chunks():
#                 destination.write(chunk)
#         im = Image.open(filename)
#         width, height = im.size
#         if width > 350:
#             new_width = 350
#             new_height = (height * 350) / width
#             new_size = new_width, new_height
#             im.thumbnail(new_size, Image.ANTIALIAS)
#             im.save(filename)
#
#         return redirect('/settings/picture/?upload_picture=uploaded')
#
#     except Exception as e:
#         return redirect('/settings/picture/')
#
#
# @login_required
# def save_uploaded_picture(request):
#     try:
#         x = int(request.POST.get('x'))
#         y = int(request.POST.get('y'))
#         w = int(request.POST.get('w'))
#         h = int(request.POST.get('h'))
#         tmp_filename = django_settings.MEDIA_ROOT + '/profile_pictures/' +\
#             request.user.username + '_tmp.jpg'
#         filename = django_settings.MEDIA_ROOT + '/profile_pictures/' +\
#             request.user.username + '.jpg'
#         im = Image.open(tmp_filename)
#         cropped_im = im.crop((x, y, w+x, h+y))
#         cropped_im.thumbnail((200, 200), Image.ANTIALIAS)
#         cropped_im.save(filename)
#         os.remove(tmp_filename)
#
#     except Exception:
#         pass
#
#     return redirect('/settings/picture/')