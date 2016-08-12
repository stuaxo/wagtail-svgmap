from django.contrib.contenttypes.models import ContentType
from django.core.files import File

import pytest
from wagtail.wagtailcore.models import Collection, Page, Site
from wagtail.wagtaildocs.models import Document
from wagtail_svgmap.tests.utils import EXAMPLE_SVG_PATH


@pytest.fixture()
def root_page():
    """
    Get the global Wagtail root page (cleared of any subpages it might have)
    :return: Root page
    :rtype: wagtail.wagtailcore.models.Page
    """
    try:
        page = Page.objects.get(slug="root", depth=1)
    except Page.DoesNotExist:  # pragma: no cover
        page = Page.objects.create(
            title="Root",
            slug='root',
            content_type=ContentType.objects.get_for_model(Page),
            path='0001',
            depth=1,
            numchild=1,
            url_path='/',
        )

    for child in page.get_children():  # pragma: no cover
        child.delete()
    page.numchild = 0
    page.save(update_fields=("numchild",))

    site = Site.objects.first()
    if not site:  # pragma: no cover
        site = Site()
    site.root_page = page
    site.is_default_site = True
    site.save()

    return page


@pytest.fixture
def example_svg_doc(request):
    if not Collection.objects.exists():  # pragma: no cover
        Collection.add_root()

    doc = Document(title='hello')
    with open(EXAMPLE_SVG_PATH, 'rb') as infp:
        doc.file.save('example.svg', File(infp))
    doc.save()
    doc = Document.objects.get(pk=doc.pk)  # Reload to ensure the upload took

    def nuke():
        try:  # Try cleaning up so `/var/media` isn't full of SVGen
            doc.file.delete()
            doc.delete()
        except:
            pass

    request.addfinalizer(nuke)
    return doc
