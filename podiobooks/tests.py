"""Tests for top-level items like management commands"""

# pylint: disable=C0103,C0111,R0902,R0904,W0401,W0614

from django.test import TestCase
from django.core.management import call_command
from django.conf import settings


class ManagementCommandsTestCase(TestCase):
    """Test the top level management commands"""

    fixtures = ['test_data.json', ]

    def setUp(self):
        pass

    def test_clear_cache(self):
        call_command('clear_cache')

    def test_resave_title_cats(self):
        call_command("resave_title_categories")

    def test_collectmedia(self):
        call_command("collectmedia")


class TopLevelUrlsTestCase(TestCase):
    """Tests for URLs defined at the podiobooks level"""

    fixtures = ['test_data.json', ]

    def setUp(self):
        pass

    def test_title_search_pb1(self):
        response = self.client.get('/podiobooks/search.php', {'keyword': 'sigler'}, follow=True)
        self.assertRedirects(response, '/search/?q=sigler', status_code=301)

    def test_title_category_search_pb1(self):
        response = self.client.get('/podiobooks/search.php', {'category': 1}, follow=True)
        self.assertRedirects(response, '/category/science-fiction/', status_code=301)

    def test_sitemap(self):
        response = self.client.get('/sitemap.xml')
        self.assertEquals(200, response.status_code)
        self.assertNotContains(response, 'error')

    def test_pb1_login_redirect(self):
        response = self.client.get('/login.php')
        self.assertEquals(301, response.status_code)

    def test_pb1_xlogin_redirect(self):
        response = self.client.get('/Xlogin.php')
        self.assertEquals(301, response.status_code)

    def test_pb1_charts_redirect(self):
        response = self.client.get('/charts.php')
        self.assertEquals(301, response.status_code)

    def test_pb1_authors_redirect(self):
        response = self.client.get('/authors.php')
        self.assertEquals(301, response.status_code)

    def test_pb1_pbpro_redirect(self):
        response = self.client.get('/authors/pbpro.php')
        self.assertEquals(301, response.status_code)

    def test_pb1_staff_redirect(self):
        response = self.client.get('/staff.php')
        self.assertEquals(301, response.status_code)

    def test_pb1_donate_redirect(self):
        response = self.client.get('/donate.php')
        self.assertEquals(301, response.status_code)

    def test_pb1_donate_redirect_2(self):
        response = self.client.get('/donate')
        self.assertEquals(301, response.status_code)

    def test_pb1_legal_redirect(self):
        response = self.client.get('/legal.php')
        self.assertEquals(301, response.status_code)

    def test_pb1_book_redirect(self):
        response = self.client.get('/podiobooks/book.php', {'ID': 24})
        self.assertRedirects(response, '/title/earthcore/', status_code=301)

    def test_pb1_xml_redirect(self):
        response = self.client.get('/index.xml')
        self.assertRedirects(response, '/rss/feeds/titles/recent/', status_code=301)

    def test_pb1_feed_redirect(self):
        response = self.client.get('/title/trader-tales-4-double-share/feed/')
        self.assertRedirects(response, '/rss/feeds/episodes/trader-tales-4-double-share/', status_code=301)

    def test_blog_redirect(self):
        response = self.client.get('/blog')
        self.assertEquals(301, response.status_code)

    def test_website_redirect(self):
        response = self.client.get('/website')
        self.assertEquals(301, response.status_code)

    def test_audible_redirect(self):
        response = self.client.get('/audible')
        self.assertEquals(301, response.status_code)

    def test_start_redirect(self):
        response = self.client.get('/start')
        self.assertEquals(301, response.status_code)

    def test_robots(self):
        response = self.client.get('/robots.txt')
        self.assertEquals(200, response.status_code)
        self.assertNotContains(response, 'error')

    def test_crossdomain(self):
        response = self.client.get('/crossdomain.xml')
        self.assertEquals(200, response.status_code)
        self.assertNotContains(response, 'error')

    def test_favicon(self):
        settings.ACCEL_REDIRECT = True
        response = self.client.get('/favicon.ico')
        self.assertEquals(200, response.status_code)
        self.assertTrue(response.has_header('X-Accel-Redirect'))
        self.assertNotContains(response, 'error')
        settings.ACCEL_REDIRECT = False
        response = self.client.get('/favicon.ico')
        self.assertEquals(302, response.status_code)
        self.assertFalse(response.has_header('X-Accel-Redirect'))

    def test_apple_touch_icon(self):
        settings.ACCEL_REDIRECT = True
        response = self.client.get('/apple-touch-icon.png')
        self.assertEquals(200, response.status_code)
        self.assertTrue(response.has_header('X-Accel-Redirect'))
        self.assertNotContains(response, 'error')
        settings.ACCEL_REDIRECT = False
        response = self.client.get('/apple-touch-icon.png')
        self.assertEquals(302, response.status_code)
        self.assertFalse(response.has_header('X-Accel-Redirect'))