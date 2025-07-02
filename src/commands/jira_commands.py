"""
Jira command implementations.
"""
from typing import Dict, Any
from .base import JiraCommand
from src.utils import logger, log_method_call


class CreateJiraIssueCommand(JiraCommand):
    """Command to create a Jira issue."""
    
    def __init__(self, jira_api):
        super().__init__(
            "create_jira_issue",
            "Create a new Jira issue",
            jira_api
        )
        
    @log_method_call
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create issue command."""
        self.validate_args(args, ['project', 'summary', 'issuetype'])
        
        try:
            result = self.jira_api.create(args)
            return {
                'success': True,
                'issue_key': result.get('key'),
                'issue_id': result.get('id'),
                'message': f"Issue {result.get('key')} created successfully"
            }
        except Exception as e:
            logger.error(f"Failed to create Jira issue: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class UpdateJiraIssueCommand(JiraCommand):
    """Command to update a Jira issue."""
    
    def __init__(self, jira_api):
        super().__init__(
            "update_jira_issue",
            "Update an existing Jira issue",
            jira_api
        )
    
    @log_method_call
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute update issue command."""
        self.validate_args(args, ['issue_key'])
        
        issue_key = args.pop('issue_key')
        
        try:
            result = self.jira_api.update(issue_key, args)
            return {
                'success': True,
                'issue_key': issue_key,
                'message': f"Issue {issue_key} updated successfully"
            }
        except Exception as e:
            logger.error(f"Failed to update Jira issue: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class DeleteJiraIssueCommand(JiraCommand):
    """Command to delete a Jira issue."""
    
    def __init__(self, jira_api):
        super().__init__(
            "delete_jira_issue",
            "Delete a Jira issue",
            jira_api
        )
    
    @log_method_call
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute delete issue command."""
        self.validate_args(args, ['issue_key'])
        
        try:
            success = self.jira_api.delete(args['issue_key'])
            if success:
                return {
                    'success': True,
                    'message': f"Issue {args['issue_key']} deleted successfully"
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to delete issue'
                }
        except Exception as e:
            logger.error(f"Failed to delete Jira issue: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class CreateJiraSubtaskCommand(JiraCommand):
    """Command to create a Jira subtask."""
    
    def __init__(self, jira_api):
        super().__init__(
            "create_jira_subtask",
            "Create a subtask for a parent issue",
            jira_api
        )
    
    @log_method_call
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create subtask command."""
        self.validate_args(args, ['parent_key', 'summary'])
        
        parent_key = args.pop('parent_key')
        
        try:
            result = self.jira_api.create_subtask(parent_key, args)
            return {
                'success': True,
                'issue_key': result.get('key'),
                'issue_id': result.get('id'),
                'parent_key': parent_key,
                'message': f"Subtask {result.get('key')} created for {parent_key}"
            }
        except Exception as e:
            logger.error(f"Failed to create Jira subtask: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class SearchJiraIssuesCommand(JiraCommand):
    """Command to search Jira issues."""
    
    def __init__(self, jira_api):
        super().__init__(
            "search_jira_issues",
            "Search for Jira issues with filters",
            jira_api
        )
    
    @log_method_call
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute search issues command."""
        try:
            issues = self.jira_api.search(args)
            return {
                'success': True,
                'issues': issues,
                'count': len(issues),
                'message': f"Found {len(issues)} issues"
            }
        except Exception as e:
            logger.error(f"Failed to search Jira issues: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class GetJiraDebugInfoCommand(JiraCommand):
    """Command to get Jira debug information."""
    
    def __init__(self, jira_api):
        super().__init__(
            "get_jira_debug_info",
            "Get Jira debug information (projects, issue types, etc.)",
            jira_api
        )
    
    @log_method_call
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get debug info command."""
        try:
            debug_info = self.jira_api.get_debug_info()
            return {
                'success': True,
                'debug_info': debug_info,
                'message': "Debug information retrieved successfully"
            }
        except Exception as e:
            logger.error(f"Failed to get Jira debug info: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
