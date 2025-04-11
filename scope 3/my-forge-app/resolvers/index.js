/*-->This file defines a resolver function to fetch issue details from Jira. It’s used if you need to call server-side functions from your Forge app.
 -->getIssueDetails: When invoked (with an issueId in the payload), it fetches the corresponding Jira issue details and returns a simplified object.
-->Error Handling: Logs errors and returns an error message if the request fails.*/
import Resolver from '@forge/resolver';
import api, { route } from '@forge/api';

const resolver = new Resolver();

resolver.define('getIssueDetails', async (req) => {
  const { issueId } = req.payload;

  if (!issueId) {
    return { error: "Missing issue ID" };
  }

  try {
    const response = await api.asApp().requestJira(
      // Note: Use template literal syntax correctly:
      route`/rest/api/3/issue/${issueId}`,
      {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      }
    );

    const data = await response.json();
    console.log("Jira API Response:", data);

    return {
      key: data.key,
      summary: data.fields.summary || "No summary available",
      description: data.fields.description?.content?.[0]?.content?.[0]?.text || "No description",
      status: data.fields.status.name || "Unknown"
    };
  } catch (error) {
    console.error("Failed to fetch Jira issue details:", error);
    return { error: "Failed to fetch Jira issue details" };
  }
});

export const handler = resolver.getDefinitions();
