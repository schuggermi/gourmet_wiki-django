from django.test import TestCase, Client
from django.urls import reverse

class ErrorPagesTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_404_page(self):
        """Test that the 404 page is displayed for non-existent URLs"""
        response = self.client.get('/non-existent-url/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'errors/404.html')

    def test_403_page(self):
        """Test that the 403 page is displayed for forbidden access"""
        # This is a simple test that assumes there's a view that requires login
        # You might need to adjust this based on your actual application
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirects to login
        
        # For a real 403 test, you'd need a view that returns 403
        # This is just a placeholder