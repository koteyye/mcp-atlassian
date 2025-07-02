"""
Builder pattern for constructing API requests to Jira and Confluence.
"""
from typing import Dict, Any, Optional, List


class RequestBuilder:
    """Base builder for API requests."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset the builder to initial state."""
        self._request = {}
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build and return the final request."""
        result = self._request.copy()
        self.reset()
        return result


class JiraIssueBuilder(RequestBuilder):
    """Builder for Jira issue creation and update requests."""
    
    def set_project(self, project_key: str):
        """Set project key."""
        if 'fields' not in self._request:
            self._request['fields'] = {}
        self._request['fields']['project'] = {'key': project_key}
        return self
    
    def set_summary(self, summary: str):
        """Set issue summary."""
        if 'fields' not in self._request:
            self._request['fields'] = {}
        self._request['fields']['summary'] = summary
        return self
    
    def set_description(self, description: str):
        """Set issue description."""
        if 'fields' not in self._request:
            self._request['fields'] = {}
        self._request['fields']['description'] = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": description
                        }
                    ]
                }
            ]
        }
        return self
    
    def set_issue_type(self, issue_type: str):
        """Set issue type."""
        if 'fields' not in self._request:
            self._request['fields'] = {}
        self._request['fields']['issuetype'] = {'name': issue_type}
        return self
    
    def set_assignee(self, assignee: str):
        """Set assignee."""
        if 'fields' not in self._request:
            self._request['fields'] = {}
        self._request['fields']['assignee'] = {'name': assignee}
        return self
    
    def set_labels(self, labels: List[str]):
        """Set labels."""
        if 'fields' not in self._request:
            self._request['fields'] = {}
        self._request['fields']['labels'] = labels
        return self
    
    def set_epic_link(self, epic_key: str):
        """Set epic link (parent epic)."""
        if 'fields' not in self._request:
            self._request['fields'] = {}
        self._request['fields']['customfield_10014'] = epic_key  # Epic Link field
        return self
    
    def set_parent(self, parent_key: str):
        """Set parent issue for sub-tasks."""
        if 'fields' not in self._request:
            self._request['fields'] = {}
        self._request['fields']['parent'] = {'key': parent_key}
        return self


class ConfluencePageBuilder(RequestBuilder):
    """Builder for Confluence page creation and update requests."""
    
    def set_space(self, space_key: str):
        """Set space key."""
        self._request['space'] = {'key': space_key}
        return self
    
    def set_title(self, title: str):
        """Set page title."""
        self._request['title'] = title
        return self
    
    def set_content(self, content: str, representation: str = 'storage'):
        """Set page content."""
        self._request['body'] = {
            representation: {
                'value': content,
                'representation': representation
            }
        }
        return self
    
    def set_parent(self, parent_id: str):
        """Set parent page."""
        if 'ancestors' not in self._request:
            self._request['ancestors'] = []
        self._request['ancestors'].append({'id': parent_id})
        return self
    
    def set_type(self, page_type: str = 'page'):
        """Set page type."""
        self._request['type'] = page_type
        return self


class JiraFilterBuilder(RequestBuilder):
    """Builder for Jira search queries."""
    
    def __init__(self):
        super().__init__()
        self._jql_parts = []
    
    def reset(self):
        """Reset the builder to initial state."""
        super().reset()
        self._jql_parts = []
        return self
    
    def add_project(self, project_key: str):
        """Add project filter."""
        self._jql_parts.append(f'project = "{project_key}"')
        return self
    
    def add_epic(self, epic_key: str):
        """Add epic filter."""
        self._jql_parts.append(f'"Epic Link" = "{epic_key}"')
        return self
    
    def add_assignee(self, assignee: str):
        """Add assignee filter."""
        self._jql_parts.append(f'assignee = "{assignee}"')
        return self
    
    def add_status(self, status: str):
        """Add status filter."""
        self._jql_parts.append(f'status = "{status}"')
        return self
    
    def add_issue_type(self, issue_type: str):
        """Add issue type filter."""
        self._jql_parts.append(f'issuetype = "{issue_type}"')
        return self
    
    def set_order_by(self, field: str, direction: str = 'ASC'):
        """Set order by clause."""
        self._request['orderBy'] = f'{field} {direction}'
        return self
    
    def set_max_results(self, max_results: int):
        """Set maximum number of results."""
        self._request['maxResults'] = max_results
        return self
    
    def set_start_at(self, start_at: int):
        """Set starting index."""
        self._request['startAt'] = start_at
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the final query."""
        if self._jql_parts:
            self._request['jql'] = ' AND '.join(self._jql_parts)
        
        result = self._request.copy()
        self.reset()
        return result
