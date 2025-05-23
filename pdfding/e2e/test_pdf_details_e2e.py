from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from helpers import PdfDingE2ETestCase
from pdf.models import Pdf, PdfComment, PdfHighlight, Tag
from playwright.sync_api import expect, sync_playwright
from users.models import Profile


class PdfDetailsE2ETestCase(PdfDingE2ETestCase):
    def setUp(self, login: bool = True) -> None:
        super().setUp()

        # create some pdfs
        pdf = Pdf.objects.create(
            owner=self.user.profile, name='pdf_1_1', description='this is number 1', notes='some notes'
        )

        tag = Tag.objects.create(name='tag', owner=self.user.profile)
        pdf.tags.set([tag])

    def test_details(self):
        pdf = self.user.profile.pdf_set.get(name='pdf_1_1')
        dummy_file = SimpleUploadedFile("simple.pdf", b"these are the file contents!")
        pdf.views = 1001
        pdf.number_of_pages = 10
        pdf.file = dummy_file
        pdf.save()

        with sync_playwright() as p:
            self.open(reverse('pdf_details', kwargs={'identifier': pdf.id}), p)

            expect(self.page.locator("content")).to_contain_text("pdf_1_1")
            expect(self.page.locator("#name")).to_contain_text("pdf_1_1")
            expect(self.page.locator("#description")).to_contain_text("this is number 1")
            expect(self.page.locator("#notes")).to_contain_text("some notes")
            expect(self.page.locator("#tags")).to_contain_text("#tag")
            expect(self.page.locator("#progress")).to_contain_text("10% - Page 1 of 10")
            expect(self.page.locator("#views")).to_contain_text("1001")

    def test_details_progress_not_visible(self):
        pdf = self.user.profile.pdf_set.get(name='pdf_1_1')
        pdf.views = 1001
        pdf.number_of_pages = -1
        pdf.save()

        with sync_playwright() as p:
            self.open(reverse('pdf_details', kwargs={'identifier': pdf.id}), p)

            expect(self.page.locator("content")).to_contain_text("pdf_1_1")
            expect(self.page.locator("#name")).to_contain_text("pdf_1_1")
            expect(self.page.locator("#description")).to_contain_text("this is number 1")
            expect(self.page.locator("#tags")).to_contain_text("#tag")
            expect(self.page.locator("#progress")).not_to_be_visible()
            expect(self.page.locator("content")).to_contain_text("1001")

    @patch('pdf.service.get_file_path', return_value='application/pdf')
    def test_change_details(self, mock_get_file_path):
        pdf = self.user.profile.pdf_set.get(name='pdf_1_1')
        pdf.notes = ''
        pdf.description = ''
        pdf.save()
        pdf.tags.set([])

        mock_get_file_path.return_value = pdf.file.name

        with sync_playwright() as p:
            self.open(reverse('pdf_details', kwargs={'identifier': pdf.id}), p)

            # edit name
            self.page.locator("#name-edit").click()
            self.page.locator("#id_name").dblclick()
            self.page.locator("#id_name").fill("other name")
            self.page.get_by_role("button", name="Submit").click()
            expect(self.page.locator("content")).to_contain_text("other name")
            expect(self.page.locator("#name")).to_contain_text("other name")

            # edit description
            expect(self.page.locator("#description")).to_contain_text("no description available")
            self.page.locator("#description-edit").click()
            self.page.locator("#id_description").click()
            self.page.locator("#id_description").fill("other description")
            self.page.get_by_role("button", name="Submit").click()
            expect(self.page.locator("#description")).to_contain_text("other description")

            # edit notes
            expect(self.page.locator("#notes")).to_contain_text("no notes available")
            self.page.locator("#notes-edit").click()
            self.page.locator("#id_notes").click()
            self.page.locator("#id_notes").fill("other notes")
            self.page.get_by_role("button", name="Submit").click()
            expect(self.page.locator("#notes")).to_contain_text("other notes")

            # edit tags
            expect(self.page.locator("#tags")).to_contain_text("no tags available")
            self.page.locator("#tags-edit").click()
            self.page.locator("#id_tag_string").click()
            self.page.locator("#id_tag_string").fill("other")
            self.page.get_by_role("button", name="Submit").click()
            expect(self.page.locator("#tags")).to_contain_text("#other")
            # also test setting empty tag
            self.page.locator("#tags-edit").click()
            self.page.locator("#id_tag_string").click()
            self.page.locator("#id_tag_string").fill("")
            self.page.get_by_role("button", name="Submit").click()
            expect(self.page.locator("#tags")).to_contain_text("no tags available")

            # edit file directory
            expect(self.page.locator("#file_directory")).to_contain_text("File directory not set")
            self.page.locator("#file_directory-edit").click()
            self.page.locator("#id_file_directory").click()
            self.page.locator("#id_file_directory").fill("sub/dir")
            self.page.get_by_role("button", name="Submit").click()
            expect(self.page.locator("#file_directory")).to_contain_text("sub/dir")

    def test_details_star_archive(self):
        pdf = self.user.profile.pdf_set.get(name='pdf_1_1')

        with sync_playwright() as p:
            self.open(reverse('pdf_details', kwargs={'identifier': pdf.id}), p)

            expect(self.page.locator("#starred_icon")).not_to_be_visible()
            self.page.locator("#star").click()
            expect(self.page.locator("#starred_icon")).to_be_visible()
            self.page.locator("#star").click()
            expect(self.page.locator("#starred_icon")).not_to_be_visible()

            expect(self.page.locator("#archived_icon")).not_to_be_visible()
            self.page.locator("#archive").click()
            expect(self.page.locator("#archived_icon")).to_be_visible()
            self.page.locator("#archive").click()
            expect(self.page.locator("#archived_icon")).not_to_be_visible()

    def test_cancel_change_details(self):
        pdf = self.user.profile.pdf_set.get(name='pdf_1_1')

        with sync_playwright() as p:
            self.open(reverse('pdf_details', kwargs={'identifier': pdf.id}), p)

            for edit_name in ['#name-edit', '#description-edit', '#notes-edit', '#tags-edit']:
                expect(self.page.locator(edit_name)).to_contain_text("Edit")
                self.page.locator(edit_name).click()
                expect(self.page.locator(edit_name)).to_contain_text("Cancel")
                self.page.locator(edit_name).click()
                expect(self.page.locator(edit_name)).to_contain_text("Edit")

    def test_details_delete(self):
        pdf = self.user.profile.pdf_set.get(name='pdf_1_1')

        with sync_playwright() as p:
            self.open(reverse('pdf_details', kwargs={'identifier': pdf.id}), p)

            expect(self.page.locator("body")).to_contain_text("pdf_1_1")
            self.page.get_by_text("Delete").click()
            self.page.get_by_text("Confirm").click()

            expect(self.page.locator("body")).not_to_have_text("pdf_1_1")

    def test_details_cancel_delete(self):
        pdf = self.user.profile.pdf_set.get(name='pdf_1_1')

        with sync_playwright() as p:
            self.open(reverse('pdf_details', kwargs={'identifier': pdf.id}), p)

            expect(self.page.get_by_text("Confirm")).not_to_be_visible()
            expect(self.page.get_by_text("Cancel")).not_to_be_visible()
            expect(self.page.get_by_text("Delete")).to_be_visible()
            self.page.get_by_text("Delete").click()
            expect(self.page.get_by_text("Confirm")).to_be_visible()
            expect(self.page.get_by_text("Cancel")).to_be_visible()
            expect(self.page.get_by_text("Delete")).not_to_be_visible()
            self.page.get_by_text("Cancel").click()
            expect(self.page.get_by_text("Confirm")).not_to_be_visible()
            expect(self.page.get_by_text("Cancel")).not_to_be_visible()
            expect(self.page.get_by_text("Delete")).to_be_visible()


class PdfDetailsHighlightsE2ETestCase(PdfDingE2ETestCase):
    def setUp(self, login: bool = True) -> None:
        super().setUp()

        self.pdf = Pdf.objects.create(owner=self.user.profile, name='some_pdf')

    def test_overview(self):
        PdfHighlight.objects.create(text='highlight_old', page=1, creation_date=self.pdf.creation_date, pdf=self.pdf)
        PdfHighlight.objects.create(
            text='highlight_new', page=2, creation_date=self.pdf.creation_date + timedelta(minutes=5), pdf=self.pdf
        )

        with sync_playwright() as p:
            self.open(f"{reverse('pdf_details_highlight_overview', kwargs={'identifier': self.pdf.id})}", p)
            expect(self.page.locator("#annotation-1")).to_contain_text("some_pdf")
            expect(self.page.locator("#annotation-text-1")).to_contain_text("highlight_new")
            expect(self.page.locator("#annotation-2")).to_contain_text("some_pdf")
            expect(self.page.locator("#annotation-text-2")).to_contain_text("highlight_old")

    def test_load_next_page(self):
        self.user.profile.annotation_sorting = Profile.AnnotationsSortingChoice.OLDEST
        self.user.profile.save()

        for i in range(12):
            PdfHighlight.objects.create(
                text=f'highlight_{i}', page=i, creation_date=self.pdf.creation_date, pdf=self.pdf
            )

        PdfHighlight.objects.create(
            text='highlight_page_2',
            page=13,
            creation_date=self.pdf.creation_date + timedelta(minutes=5),
            pdf=self.pdf,
        )

        with sync_playwright() as p:
            self.open(f"{reverse('pdf_details_highlight_overview', kwargs={'identifier': self.pdf.id})}", p)
            expect(self.page.locator("#annotation-12")).to_be_visible()
            expect(self.page.locator("#annotation-13")).not_to_be_visible()

            self.page.locator("#next_page_1_toggle").click()
            # since other is not visible #annotation-13 will contain highlight_page_2
            expect(self.page.locator("#annotation-13")).to_be_visible()
            expect(self.page.locator("#annotation-text-13")).to_contain_text("highlight_page_2")
            expect(self.page.locator("#next_page_2_toggle")).not_to_be_visible()

    def test_sort(self):
        self.user.profile.annotation_sorting = Profile.AnnotationsSortingChoice.OLDEST
        self.user.profile.save()

        PdfHighlight.objects.create(text='highlight_old', page=1, creation_date=self.pdf.creation_date, pdf=self.pdf)
        PdfHighlight.objects.create(
            text='highlight_new', page=2, creation_date=self.pdf.creation_date + timedelta(minutes=5), pdf=self.pdf
        )

        with sync_playwright() as p:
            self.open(f"{reverse('pdf_details_highlight_overview', kwargs={'identifier': self.pdf.id})}", p)
            expect(self.page.locator("#annotation-1")).to_contain_text("some_pdf")
            expect(self.page.locator("#annotation-text-1")).to_contain_text("highlight_old")
            expect(self.page.locator("#annotation-2")).to_contain_text("some_pdf")
            expect(self.page.locator("#annotation-text-2")).to_contain_text("highlight_new")

    def test_change_sorting(self):
        self.assertEqual(self.user.profile.annotation_sorting, Profile.AnnotationsSortingChoice.NEWEST)

        with sync_playwright() as p:
            self.open(f"{reverse('pdf_details_highlight_overview', kwargs={'identifier': self.pdf.id})}", p)

            self.page.locator("#sorting_settings").click()
            self.page.get_by_text("Oldest").click()

        changed_user = User.objects.get(id=self.user.id)

        self.assertEqual(changed_user.profile.annotation_sorting, Profile.AnnotationsSortingChoice.OLDEST)


class PdfDetailsCommentsE2ETestCase(PdfDingE2ETestCase):
    def setUp(self, login: bool = True) -> None:
        super().setUp()

        self.pdf = Pdf.objects.create(owner=self.user.profile, name='some_pdf')

    def test_overview(self):
        PdfComment.objects.create(text='comment_old', page=1, creation_date=self.pdf.creation_date, pdf=self.pdf)
        PdfComment.objects.create(
            text='comment_new', page=2, creation_date=self.pdf.creation_date + timedelta(minutes=5), pdf=self.pdf
        )

        with sync_playwright() as p:
            self.open(f"{reverse('pdf_details_comment_overview', kwargs={'identifier': self.pdf.id})}", p)
            expect(self.page.locator("#annotation-1")).to_contain_text("some_pdf")
            expect(self.page.locator("#annotation-text-1")).to_contain_text("comment_new")
            expect(self.page.locator("#annotation-2")).to_contain_text("some_pdf")
            expect(self.page.locator("#annotation-text-2")).to_contain_text("comment_old")

    def test_load_next_page(self):
        self.user.profile.annotation_sorting = Profile.AnnotationsSortingChoice.OLDEST
        self.user.profile.save()

        for i in range(12):
            PdfComment.objects.create(text=f'comment_{i}', page=i, creation_date=self.pdf.creation_date, pdf=self.pdf)

        PdfComment.objects.create(
            text='comment_page_2',
            page=13,
            creation_date=self.pdf.creation_date + timedelta(minutes=5),
            pdf=self.pdf,
        )

        with sync_playwright() as p:
            self.open(f"{reverse('pdf_details_comment_overview', kwargs={'identifier': self.pdf.id})}", p)
            expect(self.page.locator("#annotation-12")).to_be_visible()
            expect(self.page.locator("#annotation-13")).not_to_be_visible()

            self.page.locator("#next_page_1_toggle").click()
            # since other is not visible #annotation-13 will contain comment_page_2
            expect(self.page.locator("#annotation-13")).to_be_visible()
            expect(self.page.locator("#annotation-text-13")).to_contain_text("comment_page_2")
            expect(self.page.locator("#next_page_2_toggle")).not_to_be_visible()

    def test_sort(self):
        self.user.profile.annotation_sorting = Profile.AnnotationsSortingChoice.OLDEST
        self.user.profile.save()

        PdfComment.objects.create(text='comment_old', page=1, creation_date=self.pdf.creation_date, pdf=self.pdf)
        PdfComment.objects.create(
            text='comment_new', page=2, creation_date=self.pdf.creation_date + timedelta(minutes=5), pdf=self.pdf
        )

        with sync_playwright() as p:
            self.open(f"{reverse('pdf_details_comment_overview', kwargs={'identifier': self.pdf.id})}", p)
            expect(self.page.locator("#annotation-1")).to_contain_text("some_pdf")
            expect(self.page.locator("#annotation-text-1")).to_contain_text("comment_old")
            expect(self.page.locator("#annotation-2")).to_contain_text("some_pdf")
            expect(self.page.locator("#annotation-text-2")).to_contain_text("comment_new")

    def test_change_sorting(self):
        self.assertEqual(self.user.profile.annotation_sorting, Profile.AnnotationsSortingChoice.NEWEST)

        with sync_playwright() as p:
            self.open(f"{reverse('pdf_details_comment_overview', kwargs={'identifier': self.pdf.id})}", p)

            self.page.locator("#sorting_settings").click()
            self.page.get_by_text("Oldest").click()

        changed_user = User.objects.get(id=self.user.id)

        self.assertEqual(changed_user.profile.annotation_sorting, Profile.AnnotationsSortingChoice.OLDEST)
