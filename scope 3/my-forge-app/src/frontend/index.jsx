// import ForgeReconciler, {
//   useEffect,
//   useState,
//   Text,
//   Button,
//   Badge,
//   Spinner,
//   Stack,
//   SectionMessage,
//   Card,
//   Image,
//   Link,
//   useProductContext
// } from '@forge/react';
// import { requestJira } from '@forge/bridge';

// const statusColors = {
//   "To Do": "blue",
//   "In Progress": "yellow",
//   "Done": "green",
//   "Blocked": "red",
//   "Unknown": "gray"
// };

// function App() {
//   const context = useProductContext();
//   const [issue, setIssue] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState(null);

//   async function fetchIssueDetails() {
//     if (!context?.extension?.issue?.id) {
//       console.error("No issue ID found in context.");
//       return;
//     }

//     setLoading(true);
//     setError(null);

//     try {
//       const issueId = context.extension.issue.id;
//       console.log(`Fetching issue details for ID: ${issueId}`);

//       const response = await requestJira(`/rest/api/3/issue/${issueId}`);
//       const data = await response.json();

//       setIssue({
//         key: data.key,
//         summary: data.fields.summary || "No summary available",
//         description: data.fields.description?.content?.[0]?.content?.[0]?.text || "No description",
//         status: data.fields.status.name || "Unknown",
//         tags: data.fields.labels || []
//       });
//     } catch (err) {
//       console.error("Error fetching issue details:", err);
//       setError("❌ Failed to load issue details.");
//     } finally {
//       setLoading(false);
//     }
//   }

//   useEffect(() => {
//     // Fetch details once context is available
//     if (context) {
//       fetchIssueDetails();
//     }
//   }, [context]);

//   return (
//     <Stack>
//       <Text style={{ fontSize: "20px", fontWeight: "bold" }}>🚀 Jira Issue Details</Text>

//       <Button
//         text="🔄 Refresh Issue"
//         onClick={fetchIssueDetails}
//         appearance="primary"
//       />

//       {loading && <Spinner size="large" />}

//       {error && (
//         <SectionMessage appearance="error">
//           <Text>{error}</Text>
//         </SectionMessage>
//       )}

//       {!loading && issue && (
//         <Card>
//           <Stack>
//             <Image
//               src="https://developer.atlassian.com/platform/forge/images/icons/issue-panel-icon.svg"
//               alt="Issue Icon"
//               width="40px"
//             />
//             <Stack space="small">
//               <Link
//                 href={`https://your-jira-instance.atlassian.net/browse/${issue.key}`}
//                 openNewTab
//               >
//                 <Text style={{ fontWeight: "bold", fontSize: "16px" }}>
//                   {issue.key}
//                 </Text>
//               </Link>
//               <Text>{issue.summary}</Text>
//               <Text>Description: {issue.description}</Text>
//               <Badge
//                 text={issue.status}
//                 appearance={statusColors[issue.status] || "gray"}
//               />
//               <Stack space="small" direction="horizontal">
//                 {issue.tags.length > 0 ? (
//                   issue.tags.map((tag, index) => (
//                     <Badge key={index} text={tag} appearance="purple" />
//                   ))
//                 ) : (
//                   <Text>No tags available</Text>
//                 )}
//               </Stack>
//             </Stack>
//           </Stack>
//         </Card>
//       )}
//     </Stack>
//   );
// }

// ForgeReconciler.render(<App />);
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// import ForgeReconciler, {  //Used to render your app into the Forge environment.
//   useEffect,               //Standard React hooks and UI components provided by Forge’s UI kit.
//   useState,
//   Text,
//   Button,
//   Badge,
//   Spinner,
//   Stack,
//   SectionMessage,
//   Card,
//   Image,
//   Link,
//   useProductContext
// } from '@forge/react';
// import { requestJira } from '@forge/bridge';  //A helper function to make API requests to Jira (for fetching issue details)

// const statusColors = { //This object maps Jira issue statuses to color names used by the Badge component for visual cues
//   "To Do": "blue",
//   "In Progress": "yellow",
//   "Done": "green",
//   "Blocked": "red",
//   "Unknown": "gray"
// };

// function App() {
//   const context = useProductContext();  //Retrieves the context provided by Jira (e.g., the current issue ID)
//   const [issue, setIssue] = useState(null); //issue stores fetched issue data, loading indicates if data is being fetched, and error stores any error messages
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState(null); 
  
//   //Checks if the Jira context includes an issue ID
//   //Uses requestJira to fetch issue details from the Jira REST API
//   //Updates the state with the issue details (key, summary, description, status, tags).
//   //Calls sendTicketToBackend to send the collected data to your Django backend
//   async function fetchIssueDetails() {   
//     if (!context?.extension?.issue?.id) {
//       console.error("No issue ID found in context.");
//       return;
//     }

//     setLoading(true);
//     setError(null);

//     try {
//       const issueId = context.extension.issue.id;
//       console.log(`Fetching issue details for ID: ${issueId}`);

//       const response = await requestJira(`/rest/api/3/issue/${issueId}`);
//       const data = await response.json();

//       setIssue({
//         key: data.key,
//         summary: data.fields.summary || "No summary available",
//         description: data.fields.description?.content?.[0]?.content?.[0]?.text || "No description",
//         status: data.fields.status.name || "Unknown",
//         tags: data.fields.labels || []
//       });

//       // Send the ticket data to the backend for collection
//       await sendTicketToBackend(data);

//     } catch (err) {
//       console.error("Error fetching issue details:", err);
//       setError("❌ Failed to load issue details.");
//     } finally {
//       setLoading(false);
//     }
//   }

//   // Function to send collected ticket data to the backend
//   // It sends the ticket details in a JSON payload within a tickets array
//   // Logs the backend's response to the console.
//   const sendTicketToBackend = async (ticketData) => {
//     const response = await fetch('https://127.0.0.1:8000/api/collect-tickets/', {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({
//         tickets: [{
//           ticket_id: ticketData.key,
//           summary: ticketData.fields.summary,
//           description: ticketData.fields.description?.content?.[0]?.content?.[0]?.text || '',
//           tags: ticketData.fields.labels || []
//         }]
//       })
//     });

//     const result = await response.json();
//     console.log("Backend response:", result);
//   };


//   //This function sends a POST request to the Predict Labels endpoint using the issue details.
//   //The response, which should contain predicted labels, is logged.
//   const predictLabel = async () => {
//     if (!issue) return;

//     const response = await fetch('https://127.0.0.1:8000/api/predict-labels/', {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({
//         summary: issue.summary,
//         description: issue.description,
//         tags: issue.tags
//       }),
//     });

//     const prediction = await response.json();
//     console.log("Predicted labels:", prediction);
//   };

//   //When the context becomes available (i.e., when the issue page loads in Jira), it automatically calls fetchIssueDetails
  
//   useEffect(() => {
//     if (context) {
//       fetchIssueDetails();
//     }
//   }, [context]);
//   //The UI displays:
//   // A header with "Jira Issue Details".
//   // Buttons to refresh the issue data and trigger label prediction.
//   // A spinner during loading.
//   // An error message if there is an error.
//   // A card showing issue details (including key, summary, description, status, and tags) if the data is loaded.

//   return (
//     <Stack>
//       <Text style={{ fontSize: "20px", fontWeight: "bold" }}>🚀 Jira Issue Details</Text>

//       <Button
//         text="🔄 Refresh Issue"
//         onClick={fetchIssueDetails}
//         appearance="primary"
//       />
//       <Button
//         text="Predict Labels"
//         onClick={predictLabel}
//         appearance="primary"
//       />

//       {loading && <Spinner size="large" />}

//       {error && (
//         <SectionMessage appearance="error">
//           <Text>{error}</Text>
//         </SectionMessage>
//       )}

//       {!loading && issue && (
//         <Card>
//           <Stack>
//             <Image
//               src="https://developer.atlassian.com/platform/forge/images/icons/issue-panel-icon.svg"
//               alt="Issue Icon"
//               width="40px"
//             />
//             <Stack space="small">
//               <Link
//                 href={`https://your-jira-instance.atlassian.net/browse/${issue.key}`}
//                 openNewTab
//               >
//                 <Text style={{ fontWeight: "bold", fontSize: "16px" }}>
//                   {issue.key}
//                 </Text>
//               </Link>
//               <Text>{issue.summary}</Text>
//               <Text>Description: {issue.description}</Text>
//               <Badge
//                 text={issue.status}
//                 appearance={statusColors[issue.status] || "gray"}
//               />
//               <Stack space="small" direction="horizontal">
//                 {issue.tags.length > 0 ? (
//                   issue.tags.map((tag, index) => (
//                     <Badge key={index} text={tag} appearance="purple" />
//                   ))
//                 ) : (
//                   <Text>No tags available</Text>
//                 )}
//               </Stack>
//             </Stack>
//           </Stack>
//         </Card>
//       )}
//     </Stack>
//   );
// }

// ForgeReconciler.render(<App />); //This line renders App component into the Forge environment
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
import ForgeReconciler, {
  useEffect,               // Standard React hook for side effects.
  useState,                // Standard React hook for state management.
  Text,                    // UI component for displaying text.
  Button,                  // UI component for buttons.
  Badge,                   // UI component for badges.
  Spinner,                 // UI component for a loading spinner.
  Stack,                   // UI component for vertical/horizontal stacking.
  SectionMessage,          // UI component for messages (e.g., errors).
  Card,                    // UI component for card containers.
  Image,                   // UI component to display images.
  Link,                    // UI component for hyperlinks.
  useProductContext        // Hook to get context (e.g., current Jira issue).
} from '@forge/react';
import { requestJira } from '@forge/bridge'; // Helper to make API requests to Jira.

const statusColors = { // Maps Jira issue statuses to color names.
  "To Do": "blue",
  "In Progress": "yellow",
  "Done": "green",
  "Blocked": "red",
  "Unknown": "gray"
};

function App() {
  const context = useProductContext(); // Retrieves context provided by Jira.
  const [issue, setIssue] = useState(null); // Holds fetched issue data.
  const [loading, setLoading] = useState(false); // Indicates if data is loading.
  const [error, setError] = useState(null); // Holds error messages, if any.

  // Function to fetch issue details from Jira.
  async function fetchIssueDetails() {
    if (!context?.extension?.issue?.id) {
      console.error("No issue ID found in context.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const issueId = context.extension.issue.id;
      console.log(`Fetching issue details for ID: ${issueId}`);

      const response = await requestJira(`/rest/api/3/issue/${issueId}`);
      const data = await response.json();

      setIssue({
        key: data.key,
        summary: data.fields.summary || "No summary available",
        description: data.fields.description?.content?.[0]?.content?.[0]?.text || "No description",
        status: data.fields.status.name || "Unknown",
        tags: data.fields.labels || []
      });

      // Removed redundant call to send ticket data.
      // Ticket data is sent to the backend via issues-created.js.
      // await sendTicketToBackend(data);

    } catch (err) {
      console.error("Error fetching issue details:", err);
      setError("❌ Failed to load issue details.");
    } finally {
      setLoading(false);
    }
  }

  // Function to handle label prediction.
  // Sends a POST request to the Predict Labels endpoint using the issue details.
  // const predictLabel = async () => {
  //   if (!issue) return;

  //   const response = await fetch('http://127.0.0.1:8000/api/predict-labels/', {
  //     method: 'POST',
  //     headers: { 'Content-Type': 'application/json' },
  //     body: JSON.stringify({
  //       summary: issue.summary,
  //       description: issue.description,
  //       tags: issue.tags
  //     }),
  //   });

  //   const prediction = await response.json();
  //   console.log("Predicted labels:", prediction);
  // };

  // When the context becomes available (i.e., when the Jira issue page loads),
  // automatically fetch the issue details.
  useEffect(() => {
    if (context) {
      fetchIssueDetails();
    }
  }, [context]);

  // The UI displays:
  // - A header with "Jira Issue Details".
  // - Buttons to refresh the issue data and trigger label prediction.
  // - A spinner during loading.
  // - An error message if there is an error.
  // - A card showing issue details (key, summary, description, status, and tags) when data is loaded.
  return (
    <Stack>
      <Text style={{ fontSize: "20px", fontWeight: "bold" }}>🚀 Jira Issue Details</Text>

      <Button
        text="🔄 Refresh Issue"
        onClick={fetchIssueDetails}
        appearance="primary"
      />
      <Button
        text="Predict Labels"
        onClick={predictLabel}
        appearance="primary"
      />

      {loading && <Spinner size="large" />}

      {error && (
        <SectionMessage appearance="error">
          <Text>{error}</Text>
        </SectionMessage>
      )}

      {!loading && issue && (
        <Card>
          <Stack>
            <Image
              src="https://developer.atlassian.com/platform/forge/images/icons/issue-panel-icon.svg"
              alt="Issue Icon"
              width="40px"
            />
            <Stack space="small">
              <Link
                href={`https://your-jira-instance.atlassian.net/browse/${issue.key}`}
                openNewTab
              >
                <Text style={{ fontWeight: "bold", fontSize: "16px" }}>
                  {issue.key}
                </Text>
              </Link>
              <Text>{issue.summary}</Text>
              <Text>Description: {issue.description}</Text>
              <Badge
                text={issue.status}
                appearance={statusColors[issue.status] || "gray"}
              />
              <Stack space="small" direction="horizontal">
                {issue.tags.length > 0 ? (
                  issue.tags.map((tag, index) => (
                    <Badge key={index} text={tag} appearance="purple" />
                  ))
                ) : (
                  <Text>No tags available</Text>
                )}
              </Stack>
            </Stack>
          </Stack>
        </Card>
      )}
    </Stack>
  );
}

// This line renders the App component into the Forge environment.
ForgeReconciler.render(<App />);

