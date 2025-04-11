  # **Documentation for `collect-tickets API`**

### **Endpoint Overview**

* **Endpoint:** `/api/collect-tickets/`  
*  **Method:** `POST`  
* **Description:** This endpoint allows users to create a ticket with specific details (e.g., ID, title, description, priority, and tags) and saves it to the database.  
* **Authentication:** No authentication required (add if needed for production).

---

### **Request**

#### **Headers**

`Content-Type: application/json`

#### **Request Body**

| Field | Type | Description | Required |
| ----- | ----- | ----- | ----- |
| `ticket_id` | string | A unique identifier for the ticket. | Yes |
| `summary` | string | A short summary describing the ticket (max 255 characters). | Yes |
| `description` | string | A detailed description of the issue. | Yes |
| `priority` | string | Priority level: one of `Highest`, `High`, `Medium`, `Low`, or `Lowest`. | Yes |
| `status` | string | Current status of the ticket: `Open`, `In Progress`, `Done`, or `Closed`. | Yes |
| `assignee` | string | The user assigned to this ticket (optional). | No |
| `reporter` | string | The user who reported this ticket. | Yes |
| `tags` | array | A list of tags to categorize the ticket (optional). | No |
| `created_at` | datetime | Timestamp for when the ticket was created. Defaults to current timestamp. | No |
| `updated_at` | datetime | Timestamp for when the ticket was last updated. Auto-updates on changes. | No |

The request body should be in JSON format and contain the following fields:**Example Request**

`{`  
  `"ticket_id": "12345",`  
  `"summary": "Sample Ticket",`  
  `"description": "This is a sample description.",`  
  `"priority": "High",`  
  `"status": "Open",`  
  `"assignee": "john.doe",`  
  `"reporter": "jane.doe",`  
  `"tags": ["example", "bug"],`  
  `"created_at": "2025-01-24T10:00:00Z",`  
  `"updated_at": "2025-01-24T12:00:00Z"`  
`}`  
---

### **Response**

#### **Success Response**

**Status Code:** `200 OK`

**Response Body:**

| Field | Type | Description |
| ----- | ----- | ----- |
| `message` | `string` | A success message for ticket creation. |

#### **Example Success Response**

`{`  
    `"message": "Ticket successfully processed."`  
`}`

---

#### **Error Responses**

**Validation Error: Missing Required Fields** **Status Code:** `400 Bad Request`  
`{`  
    `"ticket_id": ["This field is required."],`  
    `"priority": ["This field is required."]`  
`}`  
**Validation Error: Invalid Priority Value** **Status Code:** `400 Bad Request`

`{`  
    `"priority": ["\"urgent\" is not a valid choice."]`  
`}`  
**Duplicate Ticket ID** **Status Code:** `409 Conflict`

`{`  
    `"error": "A ticket with this ID already exists."`  
`}`  
**Internal Server Error** **Status Code:** `500 Internal Server Error`  
`{`  
    `"error": "An error occurred during ticket processing: <error details>"`  
`}`  
---

### **Validation Rules**

* `ticket_id`: Required, unique, string.  
* `title`: Required, string, max length 255\.  
* `description`: Required, string.  
* `priority`: Required, string, must be one of the following:  
  * `low`  
  * `medium`  
  * `high`  
* `tags`: Optional, list of strings.

---

### **Unit Tests**

The following test cases ensure the endpoint is robust and handles various scenarios appropriately:

#### **Valid Submission**

* **Test:** Submitting a valid payload should create the ticket and return a success message.  
* **Expected Behavior:** Status code `200 OK`.

#### **Empty Fields**

* **Test:** Submitting an empty `ticket_id` or `priority` should return a validation error.  
* **Expected Behavior:** Status code `400 Bad Request` with appropriate error messages.

#### **Invalid Priority**

* **Test:** Submitting an invalid `priority` value (e.g., `"urgent"`) should return a validation error.  
* **Expected Behavior:** Status code `400 Bad Request` with an error message for `priority`.

#### **Duplicate Ticket**

* **Test:** Submitting the same `ticket_id` twice should return a conflict error.  
* **Expected Behavior:** Status code `409 Conflict` with an appropriate error message.

#### **Missing Required Fields**

* **Test:** Submitting a payload missing required fields (e.g., `description`) should return a validation error.  
* **Expected Behavior:** Status code `400 Bad Request` with an error message for the missing fields.

#### **Example Test Implementation**

`class CollectTicketsAPITest(TestCase):`  
    `def setUp(self):`  
        `self.client = APIClient()`  
        `self.valid_payload = {`  
            `"ticket_id": "12345",`  
            `"title": "Test Ticket",`  
            `"description": "This is a test ticket.",`  
            `"priority": "high",`  
            `"tags": ["bug", "urgent"]`  
        `}`

    `def test_valid_submission(self):`  
        `response = self.client.post('/api/collect-tickets/', self.valid_payload, format='json')`  
        `self.assertEqual(response.status_code, 200)`  
        `self.assertEqual(response.data, {"message": "Ticket successfully processed."})`

---

### **`Example Requests/Responses`**

**`Example 1: Successful Submission`** `Request:`

`{`  
  `"ticket_id": "12345",`  
  `"summary": "Sample Ticket",`  
  `"description": "This is a sample description.",`  
  `"priority": "High",`  
  `"status": "Open",`  
  `"assignee": "john.doe",`  
  `"reporter": "jane.doe",`  
  `"tags": ["example", "bug"],`  
  `"created_at": "2025-01-24T10:00:00Z",`  
  `"updated_at": "2025-01-24T12:00:00Z"`  
`}`

`Response:`

`{`  
  `"message": "Ticket successfully processed."`  
`}`

**`Example 2: Missing Required Fields Request`**

`{`  
  `"ticket_id": "12345",`  
  `"summary": "Sample Ticket",`  
  `"priority": "High"`  
`}`

`Response:`

`json`

`{`  
  `"description": ["This field is required."],`  
  `"reporter": ["This field is required."]`  
`}`

**`Example 3: Duplicate Ticket ID`** `Request:`

`{`  
  `"ticket_id": "12345",`  
  `"summary": "Another Ticket",`  
  `"description": "Another sample description.",`  
  `"priority": "Low",`  
  `"status": "Open",`  
  `"reporter": "jane.doe",`  
  `"tags": ["example"]`  
`}`

`Response:`

`{`  
  `"error": "A ticket with this ID already exists."`  
`}`  
---

### **Performance**

The database handles:

* **Unique constraints** on `ticket_id` to prevent duplicates.  
* Automatic management of `created_at` and `updated_at` timestamps.

---





  # **Documentation for  `predict-labels API`** 

### **Endpoint Overview**

* **Endpoint:** `/api/predict-labels/`  
*  **Method:** `POST`  
* **Description:** This endpoint predicts labels for a given ticket's title and description using zero-shot classification. It returns the most likely labels along with their confidence scores.  
* **Authentication:** No authentication required (add authentication if needed in production).

---

### **Request**

#### **Headers**

`Content-Type: application/json`

#### **Request Body**

The request body should be in  format and contain the following fields:

| Field | Type | Description | Required |
| ----- | ----- | ----- | ----- |
| `title` | `string` | The title of the ticket (max 255 characters). | Yes |
| `description` | `string` | A detailed description of the ticket. | Yes |
| `candidate_labels` | `array` | A list of strings representing potential labels. | Yes |

#### **Example Request**

`{`  
  `"title": "Bug in the login page",`  
  `"description": "The login button is not responding when clicked.",`  
  `"candidate_labels": ["bug", "feature request", "enhancement"]`  
`}`

---

### **Response**

#### **Success Response**

**Status Code:** `200 OK`

**Response Body:**

| Field | Type | Description |
| ----- | ----- | ----- |
| `message` | `string` | A success message indicating the operation was completed. |
| `predictions` | `array` | A list of predictions containing labels and confidence scores. |

**Each `prediction` object contains:**

| Field | Type | Description |
| ----- | ----- | ----- |
| `label` | `string` | The predicted label. |
| `confidence` | `float` | The confidence score for the prediction. |

#### **Example Success Response**

`{`  
    `"message": "Label prediction successful.",`  
    `"predictions": [`  
        `{`  
            `"label": "bug",`  
            `"confidence": 0.9927340149879456`  
        `},`  
        `{`  
            `"label": "feature request",`  
            `"confidence": 0.005501751787960529`  
        `},`  
        `{`  
            `"label": "enhancement",`  
            `"confidence": 0.001764180837199092`  
        `}`  
    `]`  
`}`

---

#### **Error Responses**

**Invalid Input: Missing Fields** **Status Code:** `400 Bad Request`

`{`  
    `"title": ["This field may not be blank."],`  
    `"candidate_labels": ["This field is required."]`  
`}`  
**Invalid Input: Empty Candidate Labels** **Status Code:** `400 Bad Request`

`{`  
    `"candidate_labels": ["This list may not be empty."]`  
`}`  
**Invalid Request Method** **Status Code:** `405 Method Not Allowed`

`{`  
    `"detail": "Method \"GET\" not allowed."`  
`}`  
**Internal Server Error** **Status Code:** `500 Internal Server Error`

`{`  
    `"error": "An error occurred during prediction: <error details>"`  
`}`  
---

### **Validation Rules**

* `title`: Required, string, max length of 255 characters.  
* `description`: Required, string, no specific max length enforced.  
* `candidate_labels`: Required, array of strings, must contain at least one element.

---

### **Unit Tests**

The following test cases ensure the robustness of the endpoint:

1. **Valid Payload:** Ensures a successful response with correct predictions.  
2. **Invalid Payload: Empty Title:** Verifies that the API handles missing or blank titles correctly.  
3. **Invalid Payload: Empty Candidate Labels:** Ensures proper validation for empty candidate labels.  
4. **Invalid Payload: Missing Required Fields:** Checks for appropriate error messages when fields are missing.  
5. **Invalid  Method:** Verifies the endpoint only accepts `POST`.

---

### **Performance**

The endpoint uses the HuggingFace `facebook/bart-large-mnli` model for zero-shot classification. To improve response times:

* The model is loaded globally in `utils.py` to prevent re-initialization on every request.  
* Future optimizations could include switching to a smaller model like `distilbert` if performance is critical.

---

### **Examples**

#### **Example 1: Predicting Labels**

**Request:**

`{`  
  `"title": "Unable to reset password",`  
  `"description": "The password reset link sent via email is not working.",`  
  `"candidate_labels": ["bug", "support request", "enhancement"]`  
`}`

**Response:**

`{`  
    `"message": "Label prediction successful.",`  
    `"predictions": [`  
        `{`  
            `"label": "support request",`  
            `"confidence": 0.9723458290100098`  
        `},`  
        `{`  
            `"label": "bug",`  
            `"confidence": 0.0254324814081192`  
        `},`  
        `{`  
            `"label": "enhancement",`  
            `"confidence": 0.002221689835190773`  
        `}`  
    `]`  
`}`

#### **Example 2: Missing `description`**

**Request:**

`{`  
  `"title": "Unable to reset password",`  
  `"candidate_labels": ["bug", "support request", "enhancement"]`  
`}`

**Response:**

`{`  
    `"description": ["This field is required."]`  
`}`

---



