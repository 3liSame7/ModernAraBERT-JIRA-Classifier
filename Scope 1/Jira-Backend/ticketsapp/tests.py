from django.test import TestCase
from rest_framework.test import APIClient
from django.conf import settings
from ticketsapp.models import Ticket
import os
import django 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JiraTicketClassifierApp.settings')
django.setup()

class CollectTicketsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            "ticket_id": "12345",
            "summary": "Test Ticket",
            "description": "This is a test ticket.",
            "priority": "High",
            "status": "Open",
            "assignee": "john.doe",
            "reporter": "jane.doe",
            "tags": ["bug", "urgent"],
            "created_at": "2025-01-24T10:00:00Z",
            "updated_at": "2025-01-24T12:00:00Z"
        }
        self.invalid_payload_empty_ticket_id = {
            "ticket_id": "",
            "summary": "Test Ticket",
            "description": "This is a test ticket.",
            "priority": "High",
            "status": "Open",
            "assignee": "john.doe",
            "reporter": "jane.doe",
            "tags": ["bug", "urgent"],
            "created_at": "2025-01-24T10:00:00Z",
            "updated_at": "2025-01-24T12:00:00Z"
        }
        self.invalid_payload_invalid_priority = {
            "ticket_id": "12346",
            "summary": "Another Test Ticket",
            "description": "This is another test ticket.",
            "priority": "Urgent",  
            "status": "Open",
            "assignee": "john.doe",
            "reporter": "jane.doe",
            "tags": ["bug", "urgent"],
            "created_at": "2025-01-24T10:00:00Z",
            "updated_at": "2025-01-24T12:00:00Z"
        }
        self.missing_fields_payload = {
            "ticket_id": "12347",
            "summary": "Missing Description",
            "priority": "High"
        }

    def test_valid_ticket_submission(self):
        response = self.client.post('/api/collect-tickets/', self.valid_payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "Ticket successfully processed."})

        ticket = Ticket.objects.get(ticket_id="12345")
        self.assertEqual(ticket.summary, "Test Ticket")
        self.assertEqual(ticket.status, "Open")
        self.assertEqual(ticket.priority, "High")
        self.assertEqual(ticket.tags, ["bug", "urgent"])

    def test_invalid_ticket_submission_empty_ticket_id(self):
        response = self.client.post('/api/collect-tickets/', self.invalid_payload_empty_ticket_id, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("ticket_id", response.data)
        self.assertEqual(response.data["ticket_id"], ["This field may not be blank."])

    def test_invalid_ticket_submission_invalid_priority(self):
        response = self.client.post('/api/collect-tickets/', self.invalid_payload_invalid_priority, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("priority", response.data)
        self.assertEqual(response.data["priority"], ['"Urgent" is not a valid choice.'])
        
    def test_duplicate_ticket_submission(self):
        # First submission
        self.client.post('/api/collect-tickets/', self.valid_payload, format='json')
        # Second submission with the same ticket_id
        response = self.client.post('/api/collect-tickets/', self.valid_payload, format='json')
        print("Duplicate Ticket Test Response:", response.status_code, response.data)  # Debug log
        self.assertEqual(response.status_code, 409)  # Expect 409 Conflict
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "A ticket with this ID already exists.")


    def test_missing_required_fields(self):
        response = self.client.post('/api/collect-tickets/', self.missing_fields_payload, format='json')
        self.assertEqual(response.status_code, 400)  # Expect 400 Bad Request
        self.assertIn("description", response.data)  # Check for missing description
        self.assertIn("reporter", response.data)  # Check for missing reporter
        self.assertEqual(response.data["description"], ["This field is required."])
        self.assertEqual(response.data["reporter"], ["This field is required."])






class PredictTicketLabelAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            "title": "Bug in login",
            "description": "The login button doesn't work.",
            "candidate_labels": ["bug", "feature request", "enhancement"]
        }
        self.invalid_payload_empty_title = {
            "title": "",
            "description": "The login button doesn't work.",
            "candidate_labels": ["bug", "feature request", "enhancement"]
        }
        self.invalid_payload_empty_candidate_labels = {
            "title": "Bug in login",
            "description": "The login button doesn't work.",
            "candidate_labels": []
        }
        self.invalid_payload_missing_fields = {
            "title": "Bug in login"
        }

    def test_valid_prediction(self):
        response = self.client.post('/api/predict-labels/', self.valid_payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("predictions", response.data)
        self.assertIsInstance(response.data["predictions"], list)
        self.assertGreater(len(response.data["predictions"]), 0)
        self.assertTrue(all("label" in pred and "confidence" in pred for pred in response.data["predictions"]))

    def test_invalid_prediction_empty_title(self):
        response = self.client.post('/api/predict-labels/', self.invalid_payload_empty_title, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.data)
        self.assertEqual(response.data["title"], ["This field may not be blank."])

    def test_invalid_prediction_empty_candidate_labels(self):
        response = self.client.post('/api/predict-labels/', self.invalid_payload_empty_candidate_labels, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("candidate_labels", response.data)
        self.assertEqual(response.data["candidate_labels"], ["This list may not be empty."])

    def test_invalid_prediction_missing_fields(self):
        response = self.client.post('/api/predict-labels/', self.invalid_payload_missing_fields, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("description", response.data)
        self.assertIn("candidate_labels", response.data)
        self.assertEqual(response.data["description"], ["This field is required."])
        self.assertEqual(response.data["candidate_labels"], ["This field is required."])

    def test_invalid_request_method(self):
        response = self.client.get('/api/predict-labels/')
        self.assertEqual(response.status_code, 405)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "Method \"GET\" not allowed.")
