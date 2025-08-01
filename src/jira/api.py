"""
Jira API implementation using Strategy pattern.
"""
from typing import Dict, Any, List, Optional
from src.utils.api_strategy import APIStrategy
from src.utils import logger, log_method_call, validate_required_fields, JiraIssueBuilder, JiraFilterBuilder


class JiraAPI(APIStrategy):
    """Jira API implementation."""
    
    def __init__(self, base_url: str, username: str, api_token: str, auth_type: str = 'basic'):
        super().__init__(base_url, username, api_token, auth_type)
        self.api_version = '3'
        self.api_base = f"/rest/api/{self.api_version}"
    
    @log_method_call
    @validate_required_fields(['project', 'summary', 'issuetype'])
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Jira issue."""
        builder = JiraIssueBuilder()
        
        # Required fields
        builder.set_project(data['project'])
        builder.set_summary(data['summary'])
        builder.set_issue_type(data['issuetype'])
        
        # Optional fields
        if 'description' in data:
            builder.set_description(data['description'])
        
        if 'assignee' in data:
            builder.set_assignee(data['assignee'])
        
        if 'labels' in data:
            builder.set_labels(data['labels'])
        
        if 'epic' in data:
            builder.set_epic_link(data['epic'])
        
        if 'parent' in data:
            builder.set_parent(data['parent'])
        
        request_data = builder.build()
        response = self._make_request('POST', f'{self.api_base}/issue', request_data)
        return response.json()
    
    @log_method_call
    def get(self, issue_key: str) -> Dict[str, Any]:
        """Get a Jira issue by key."""
        response = self._make_request('GET', f'{self.api_base}/issue/{issue_key}')
        return response.json()
    
    @log_method_call
    def update(self, issue_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Jira issue."""
        builder = JiraIssueBuilder()
        
        # Build update data
        if 'summary' in data:
            builder.set_summary(data['summary'])
        
        if 'description' in data:
            builder.set_description(data['description'])
        
        if 'assignee' in data:
            builder.set_assignee(data['assignee'])
        
        if 'labels' in data:
            builder.set_labels(data['labels'])
        
        if 'issuetype' in data:
            builder.set_issue_type(data['issuetype'])
        
        request_data = builder.build()
        response = self._make_request('PUT', f'{self.api_base}/issue/{issue_key}', request_data)
        
        # PUT returns 204 No Content on success
        return {'success': True, 'issue_key': issue_key}
    
    @log_method_call
    def delete(self, issue_key: str) -> bool:
        """Delete a Jira issue."""
        response = self._make_request('DELETE', f'{self.api_base}/issue/{issue_key}')
        return response.status_code == 204
    
    @log_method_call
    def search(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for Jira issues with filters."""
        builder = JiraFilterBuilder()
        
        if 'project' in filters:
            builder.add_project(filters['project'])
        
        if 'epic' in filters:
            builder.add_epic(filters['epic'])
        
        if 'assignee' in filters:
            builder.add_assignee(filters['assignee'])
        
        if 'status' in filters:
            builder.add_status(filters['status'])
        
        if 'issuetype' in filters:
            builder.add_issue_type(filters['issuetype'])
        
        if 'maxResults' in filters:
            builder.set_max_results(filters['maxResults'])
        else:
            builder.set_max_results(50)  # Default limit
        
        if 'startAt' in filters:
            builder.set_start_at(filters['startAt'])
        
        search_data = builder.build()
        response = self._make_request('POST', f'{self.api_base}/search', search_data)
        result = response.json()
        
        return result.get('issues', [])
    
    @log_method_call
    def create_subtask(self, parent_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a subtask for a parent issue."""
        # Get parent issue to inherit project
        parent_issue = self.get(parent_key)
        project_key = parent_issue['fields']['project']['key']
        
        # Add required fields for subtask
        subtask_data = data.copy()
        subtask_data['project'] = project_key
        subtask_data['parent'] = parent_key
        subtask_data['issuetype'] = 'Sub-task'  # Default subtask type
        
        return self.create(subtask_data)
    
    @log_method_call
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information - projects, issue types, etc."""
        debug_info = {}
        
        try:
            # Get projects
            projects_response = self._make_request('GET', f'{self.api_base}/project')
            debug_info['projects'] = [
                {'key': p['key'], 'name': p['name']} 
                for p in projects_response.json()
            ]
        except Exception as e:
            debug_info['projects_error'] = str(e)
        
        try:
            # Get issue types
            issuetypes_response = self._make_request('GET', f'{self.api_base}/issuetype')
            debug_info['issue_types'] = [
                {'name': it['name'], 'description': it.get('description', '')}
                for it in issuetypes_response.json()
            ]
        except Exception as e:
            debug_info['issue_types_error'] = str(e)
        
        try:
            # Get current user info
            user_response = self._make_request('GET', f'{self.api_base}/myself')
            debug_info['current_user'] = user_response.json()
        except Exception as e:
            debug_info['user_error'] = str(e)
        
        return debug_info
