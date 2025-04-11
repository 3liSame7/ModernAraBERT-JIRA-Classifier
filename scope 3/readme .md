# **Jira Forge App – Issue Panel & Backend Integration**

## **Project Overview**

This project is a Jira Forge App that:

* Creates an issue panel inside Jira.  
* Fetches historical issues from Jira.  
* Sends fetched issues to an external backend server.  
* Stores and manages issues in a backend Express.js server.

This readme provides a step-by-step guide to setting up, deploying, and debugging the application.

---

## **Project Structure**

`my-forge-app/`  
`│── forge-backend/`            
`│   ├── node_modules/`  
`│   ├── package.json`          
`│   ├── server.js`             
`│── node_modules/`  
`│── resolvers/`                
`│   ├── index.js`  
`│── src/`  
`│   ├── frontend/`             
`│   │   ├── index.jsx`  
`│   ├── index.js`              
`│── .gitignore`  
`│── manifest.yml`              
`│── package.json`              
`│── README.md`               

---

## 

## **How the Code Works**

### **Frontend (Jira Issue Panel)**

* **`src/frontend/index.jsx`**:  
  * Displays an issue panel inside Jira.  
  * Fetches issue details using **Jira API (`requestJira`)**.  
  * Shows issue title, description, and status.  
  * Uses a **Refresh Button** to manually reload issue data.

### **Backend (Express.js)**

* **`forge-backend/server.js`**:  
  * Runs an Express server.  
  * Stores fetched Jira issues in memory (`issues` array).  
  * Provides endpoints:  
    * `POST /issues` → Stores received issues.  
    * `GET /issues` → Returns stored issues.  
    * `GET /prediction` → Returns dummy predictions.

### **Resolvers (Bridge Between Frontend & Backend)**

* **`resolvers/index.js`**:  
  * Defines functions to:  
    * Fetch issue details from Jira.  
    * Send issues to the backend (`storeIssues`).  
  * Uses **Forge API (`api.asApp().requestJira`)** for Jira data.

### **Event Handling (Currently Not Used)**

* **`issues-created.js`** (Not actively used, but included):  
  * Listens for new issue creation (Forge Trigger).  
  * Sends new issues to backend via `fetch`.

### **Manifest File (Configuration)**

* **`manifest.yml`**:  
  * Defines Forge app settings.  
  * Specifies **permissions** for Jira API access.  
  * Allows external API calls (ngrok backend).

---

## 

## **Prerequisites**

Before proceeding, ensure you have:

* **Node.js (22.x)** 

**Atlassian Forge CLI** – Install with:

`npm install -g @forge/cli`

**Ngrok (for exposing backend)** – Install with:

`npm install -g ngrok`  
---

## **Setup Instructions**

### **Clone the Repository**

`git clone <your-repo-url>`  
`cd my-forge-app`

### **Install Dependencies**

Inside the Forge app directory:

`npm install`

Inside the backend directory:

`cd forge-backend`  
`npm install`

---

## **Backend Setup**

### **Start the Backend Server**

Run the Express server:

`cd forge-backend`  
`node server.js`

Expected output:

`Server running on http://localhost:5000`

### **Expose Backend via Ngrok**

Run:

`ngrok http 5000`

You will get an output like:

`https://your-ngrok-url.ngrok-free.app`

Update this URL in the following files:

**`resolvers/index.js`**

`const BACKEND_URL = "https://your-ngrok-url.ngrok-free.app";`  
**`issues-created.js`**

`const response = await api.fetch('https://your-ngrok-url.ngrok-free.app/infer', {`  
**`manifest.yml`**

`external:`  
  `fetch:`  
    `backend:`  
      `- "your-ngrok-url.ngrok-free.app"`

---

## **Deploying the Forge App**

### **Deploy to Atlassian**

`forge deploy`

If permission issues appear, run:

`forge install --upgrade`

### **Start the Forge Tunnel**

`forge tunnel`

This allows live debugging and logs API requests and responses in real time.

---

## **Testing the App**

1. Open Jira.  
2. Go to an issue page.  
3. Look for the Issue Panel.  
   * The panel should show issue details.  
4. Check backend logs (`server.js`).  
   * Verify if issues are stored correctly.

---

## **Debugging & Troubleshooting**

### **Common Issues & Fixes**

| Issue | Solution |
| ----- | ----- |
| `Error: Invalid ari string` | Ensure `app.id` in `manifest.yml` is correct. |
| `Ngrok Authentication Error` | Run `ngrok config add-authtoken YOUR_TOKEN` (from [Ngrok Dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)). |
| `Fetching issue details failed` | Check Jira API URL and Forge permissions (`read:jira-work`). |
| `Backend URL offline` | Restart Ngrok, then update the ngrok URL in project files. |

---

## **Contribution Guide**

### **How to Continue Development**

1. Ensure the backend (`server.js`) is running.  
2. Run ngrok and update the URLs in the required files.  
3. Deploy new changes using `forge deploy`.  
4. Use `forge tunnel` for debugging API requests.  
5. Check browser console (`F12 → Console`) for frontend errors.

### **Suggested Next Steps**

* Fix any console errors in Jira.  
* Ensure issues are stored correctly (`server.js` logs).  
* Improve UI and UX of the Jira issue panel.

