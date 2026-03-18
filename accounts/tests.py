from django.test import TestCase
from django.urls import reverse


class ApiRoutingTests(TestCase):
	def test_root_endpoint_returns_ok(self):
		response = self.client.get(reverse("api_root"))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["mensaje"], "API de CoffeU activa")

	def test_login_get_returns_usage_metadata(self):
		response = self.client.get(reverse("login"))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["mensaje"], "Usa POST para iniciar sesión")
