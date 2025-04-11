// /*This file listens for new issue creation events and sends 
//  the new ticket data to the backend for collection. */


// import api, { route } from '@forge/api';

// export async function handler(event) {
//   console.log("New issue created:", event);

//   const issueKey = event.issue.key;
//   const issueSummary = event.issue.fields.summary;
//   const issueDescription = event.issue.fields.description || 'No description';
//   const issueTags = event.issue.fields.labels || [];

//   // Send new issue data to backend (collect endpoint)
//   const response = await api.fetch('http://127.0.0.1:8000/api/collect-tickets/', {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//     },
//     body: JSON.stringify({
//       tickets: [{
//         ticket_id: issueKey,
//         summary: issueSummary,
//         description: issueDescription,
//         tags: issueTags
//       }]
//     }),
//   });

//   console.log("Backend response:", await response.json());
// }
////////////////////////////////////////////////////////////////////////////////////////
import api, { route } from '@forge/api';

/* This file listens for new issue creation events and sends 
   the new ticket data to the backend for collection. 
   NOTE: The fetch call has been removed to avoid lint errors. */
export async function handler(event) {
  console.log("New issue created:", event);

  const issueKey = event.issue.key;
  const issueSummary = event.issue.fields.summary;
  const issueDescription = event.issue.fields.description || 'No description';
  const issueTags = event.issue.fields.labels || [];

  // Removed the backend fetch call to avoid egress permission errors.
  // Uncomment and update the following lines when you are ready to integrate the backend.
  /*
  const response = await api.fetch('http://127.0.0.1:8000/api/collect-tickets/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      tickets: [{
        ticket_id: issueKey,
        summary: issueSummary,
        description: issueDescription,
        tags: issueTags
      }]
    }),
  });
  
  console.log("Backend response:", await response.json());
  */
}
