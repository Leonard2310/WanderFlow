"""
Workflow Management for WanderFlow Application

This module handles all interactions with Orkes Conductor workflows,
including workflow execution, task management, and state monitoring.
"""

import time
import streamlit as st
from typing import Dict, Any, Optional

from conductor.client.workflow.executor.workflow_executor import WorkflowExecutor
from conductor.client.orkes.orkes_task_client import OrkesTaskClient

from config.app_config import AppConfig
from utils.session_state import SessionState

class WorkflowManager:
    """
    Manages Orkes Conductor workflow operations for WanderFlow application.
    
    This class provides a high-level interface for workflow management,
    including starting workflows, completing tasks, and monitoring progress.
    """
    
    def __init__(self, executor: WorkflowExecutor, task_client: OrkesTaskClient):
        """
        Initialize the WorkflowManager with Conductor clients.
        
        Args:
            executor (WorkflowExecutor): Conductor workflow executor instance
            task_client (OrkesTaskClient): Conductor task client instance
        """
        self.executor = executor
        self.task_client = task_client
    
    def start_workflow(self, workflow_input: Dict[str, Any] = None) -> Optional[str]:
        """
        Start a new workflow instance and return its ID.
        
        Args:
            workflow_input (Dict[str, Any], optional): Input data for the workflow
            
        Returns:
            Optional[str]: Workflow ID if successful, None if failed
        """
        try:
            run = self.executor.execute(
                name=AppConfig.WORKFLOW_NAME,
                version=AppConfig.WORKFLOW_VERSION,
                workflow_input=workflow_input or {}
            )
            return run.workflow_id
        except Exception as e:
            st.error(f"Error starting workflow: {e}")
            return None
    
    def fetch_task_by_ref(self, wf_id: str, ref_name: str):
        """
        Fetch a task by its reference name from a workflow.
        
        This method looks for tasks in SCHEDULED, IN_PROGRESS, or PENDING states,
        which includes async completion tasks.
        
        Args:
            wf_id (str): Workflow ID
            ref_name (str): Task reference name
            
        Returns:
            Task object if found, None otherwise
        """
        try:
            wf = self.executor.get_workflow(workflow_id=wf_id, include_tasks=True)
            for task in wf.tasks:
                if task.reference_task_name == ref_name and task.status in ("SCHEDULED", "IN_PROGRESS", "PENDING"):
                    return task
        except Exception as e:
            st.error(f"Error fetching task {ref_name}: {e}")
        return None
    
    def complete_task(self, task_id: str, status: str = "COMPLETED", output: Dict[str, Any] = None) -> bool:
        """
        Complete a workflow task with the specified status and output.
        
        This method polls the task, updates it, and marks it as completed
        following the same pattern as the working dashboard implementation.
        
        Args:
            task_id (str): Task ID to complete
            status (str): Task completion status (default: "COMPLETED")
            output (Dict[str, Any], optional): Task output data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            task = self.task_client.get_task(task_id)
            task_type = task.task_type
            
            # Poll to acquire the task
            self.task_client.poll_task(task_type=task_type, worker_id="streamlit_ui")
            
            # Complete the task using direct access pattern
            self.task_client.update_task({
                "taskId": task_id,
                "workflowInstanceId": st.session_state.workflow_id,
                "workerId": "streamlit_ui",
                "status": status,
                "outputData": output or {}
            })
            
            return True
        except Exception as e:
            st.error(f"Error completing task: {e}")
            return False
    
    def wait_for_output_key(self, wf_id: str, key: str, msg: str) -> Optional[Any]:
        """
        Wait for a specific output key to appear in workflow output.
        
        This method continuously polls the workflow until the specified
        output key becomes available, using the same pattern as the
        working dashboard implementation.
        
        Args:
            wf_id (str): Workflow ID to monitor
            key (str): Output key to wait for
            msg (str): Spinner message to display
            
        Returns:
            Optional[Any]: Value of the output key when available, None if error
        """
        with st.spinner(msg):
            while True:
                try:
                    wf = self.executor.get_workflow(workflow_id=wf_id, include_tasks=False)
                    if wf.output and wf.output.get(key):
                        return wf.output[key]
                    time.sleep(2)
                except Exception as e:
                    print(f"Warning while waiting for output: {e}")
                    time.sleep(2)
                    continue
    
    def cache_task(self, ref_name: str, state_key: str):
        """
        Cache a task ID in session state for later use.
        
        This method fetches a task by reference name and stores its ID
        in the session state if it's different from the current cached value.
        
        Args:
            ref_name (str): Task reference name to fetch
            state_key (str): Session state key to store the task ID
        """
        if SessionState.get("workflow_id"):
            task = self.fetch_task_by_ref(SessionState.get("workflow_id"), ref_name)
            if task and SessionState.get(state_key) != task.task_id:
                SessionState.set(state_key, task.task_id)
    
    def wait_for_task_to_be_available(self, wf_id: str, ref_name: str, timeout: int = 30) -> Optional[str]:
        """
        Wait for a task to become available and return its task ID.
        
        Args:
            wf_id (str): Workflow ID to monitor
            ref_name (str): Task reference name to wait for
            timeout (int): Maximum wait time in seconds
            
        Returns:
            Optional[str]: Task ID if found within timeout, None otherwise
        """
        start_time = time.time()
        with st.spinner(f"Waiting for {ref_name} task..."):
            while time.time() - start_time < timeout:
                try:
                    task = self.fetch_task_by_ref(wf_id, ref_name)
                    if task:
                        return task.task_id
                    time.sleep(1)
                except Exception as e:
                    st.error(f"Error waiting for task {ref_name}: {e}")
                    return None
            st.warning(f"Timeout waiting for task {ref_name}")
            return None

    def cache_task_with_wait(self, ref_name: str, state_key: str, timeout: int = 30):
        """
        Cache a task ID in session state, waiting for it to become available.
        
        Args:
            ref_name (str): Task reference name to fetch
            state_key (str): Session state key to store the task ID
            timeout (int): Maximum wait time in seconds
            
        Returns:
            bool: True if task was cached successfully, False otherwise
        """
        if SessionState.get(state_key) is None and SessionState.get("workflow_id"):
            task_id = self.wait_for_task_to_be_available(SessionState.get("workflow_id"), ref_name, timeout)
            if task_id:
                SessionState.set(state_key, task_id)
                return True
            return False
        return SessionState.get(state_key) is not None
    
    def get_workflow_status(self, wf_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive workflow status information.
        
        Args:
            wf_id (str): Workflow ID to query
            
        Returns:
            Optional[Dict[str, Any]]: Status information dict or None if error
        """
        try:
            wf = self.executor.get_workflow(workflow_id=wf_id, include_tasks=False)
            return {
                "status": wf.status,
                "start_time": wf.start_time,
                "end_time": wf.end_time,
                "reason_for_incompletion": wf.reason_for_incompletion,
                "output": wf.output
            }
        except Exception as e:
            st.error(f"Error getting workflow status: {e}")
            return None
    
    def wait_for_itinerary_task(self, wf_id: str):
        """
        Wait for ShowItinerary task and return the itinerary data.
        
        This method continuously polls for the ShowItinerary task and
        extracts the itinerary data from its input when available.
        
        Args:
            wf_id (str): Workflow ID to monitor
            
        Returns:
            Itinerary data if found, None if error or timeout
        """
        with st.spinner("Processing itinerary..."):
            while True:
                try:
                    task = self.fetch_task_by_ref(wf_id, "ShowItinerary")
                    if task:
                        input_data = getattr(task, 'input_data', None) or getattr(task, 'inputData', None)
                        if input_data and "itinerary" in input_data:
                            return input_data["itinerary"]
                    time.sleep(2)
                except Exception as e:
                    st.error(f"Error waiting for itinerary task: {e}")
                    return None
    
    def wait_for_additional_info_task(self, wf_id: str) -> Optional[str]:
        """
        Wait for ShowMoreInformation task and return additional info data.
        
        Args:
            wf_id (str): Workflow ID to monitor
            
        Returns:
            Optional[str]: Additional information data if found, None otherwise
        """
        with st.spinner("Loading additional information..."):
            while True:
                try:
                    task = self.fetch_task_by_ref(wf_id, "ShowMoreInformation")
                    if task:
                        input_data = getattr(task, 'input_data', None) or getattr(task, 'inputData', None)
                        if input_data and "itinerary" in input_data:
                            return input_data["itinerary"]
                    time.sleep(2)
                except Exception as e:
                    st.error(f"Error waiting for additional info task: {e}")
                    return None
    
    def wait_for_choice_travel_city_task(self, wf_id: str) -> Optional[Dict[str, str]]:
        """
        Wait for ChoiceTravelCity task and return travel options for short trips.
        
        This method is used for trips of 3 days or fewer that offer multiple
        city tour options to choose from.
        
        Args:
            wf_id (str): Workflow ID to monitor
            
        Returns:
            Optional[Dict[str, str]]: Dictionary containing the 3 travel options
                                    and task ID, None if error or timeout
        """
        with st.spinner("Processing travel options..."):
            while True:
                try:
                    task = self.fetch_task_by_ref(wf_id, "ChoiceTravelCity")
                    if task:
                        input_data = getattr(task, 'input_data', None) or getattr(task, 'inputData', None)
                        if input_data and all(key in input_data for key in ["itinerary1", "itinerary2", "itinerary3"]):
                            return {
                                "itinerary1": input_data["itinerary1"],
                                "itinerary2": input_data["itinerary2"], 
                                "itinerary3": input_data["itinerary3"],
                                "task_id": task.task_id
                            }
                    time.sleep(2)
                except Exception as e:
                    st.error(f"Error waiting for choice travel city task: {e}")
                    return None
    
    def terminate_workflow(self, wf_id: str, reason: str = "User terminated") -> bool:
        """
        Terminate a running workflow.
        
        Args:
            wf_id (str): Workflow ID to terminate
            reason (str): Reason for termination
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.executor.terminate_workflow(workflow_id=wf_id, reason=reason)
            return True
        except Exception as e:
            st.error(f"Error terminating workflow: {e}")
            return False
    
    def is_workflow_completed(self, wf_id: str) -> bool:
        """
        Check if workflow has completed successfully.
        
        Args:
            wf_id (str): Workflow ID to check
            
        Returns:
            bool: True if completed, False otherwise
        """
        try:
            wf = self.executor.get_workflow(workflow_id=wf_id, include_tasks=False)
            return wf.status == "COMPLETED"
        except Exception as e:
            st.error(f"Error checking workflow completion: {e}")
            return False
    
    def is_workflow_failed(self, wf_id: str) -> bool:
        """
        Check if workflow has failed or been terminated.
        
        Args:
            wf_id (str): Workflow ID to check
            
        Returns:
            bool: True if failed/terminated/timed out, False otherwise
        """
        try:
            wf = self.executor.get_workflow(workflow_id=wf_id, include_tasks=False)
            return wf.status in ["FAILED", "TERMINATED", "TIMED_OUT"]
        except Exception as e:
            st.error(f"Error checking workflow failure: {e}")
            return False
    
    def get_workflow_debug_info(self, wf_id: str) -> Dict[str, Any]:
        """
        Get detailed workflow debug information for troubleshooting.
        
        This method provides comprehensive information about workflow state,
        including all tasks, their statuses, and timing information.
        
        Args:
            wf_id (str): Workflow ID to analyze
            
        Returns:
            Dict[str, Any]: Debug information dictionary containing workflow
                           and task details, or error information if failed
        """
        try:
            wf = self.executor.get_workflow(workflow_id=wf_id, include_tasks=True)
            
            tasks_info = []
            for task in wf.tasks:
                tasks_info.append({
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "reference_name": task.reference_task_name,
                    "status": task.status,
                    "start_time": getattr(task, 'start_time', None),
                    "end_time": getattr(task, 'end_time', None)
                })
            
            return {
                "workflow_id": wf.workflow_id,
                "status": wf.status,
                "start_time": wf.start_time,
                "end_time": wf.end_time,
                "output": wf.output,
                "tasks": tasks_info,
                "task_count": len(wf.tasks)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def debug_workflow_switch_logic(self, wf_id: str) -> Dict[str, Any]:
        """
        Debug the workflow switch logic to understand routing decisions.
        
        This method analyzes the workflow execution path, particularly
        focusing on the duration-based switching logic for short vs long trips.
        
        Args:
            wf_id (str): Workflow ID to analyze
            
        Returns:
            Dict[str, Any]: Analysis of workflow routing logic and decisions
        """
        try:
            wf = self.executor.get_workflow(workflow_id=wf_id, include_tasks=True)
            
            # Find UserPreferences output
            user_preferences_output = None
            trip_decision_branch = None
            
            for task in wf.tasks:
                if task.reference_task_name == "UserPreferences" and task.status == "COMPLETED":
                    user_preferences_output = getattr(task, 'output_data', None) or getattr(task, 'outputData', None)
                elif task.reference_task_name == "TripDecision":
                    trip_decision_branch = task.status
            
            # Analyze the duration logic
            duration_analysis = {}
            if user_preferences_output and 'durata' in user_preferences_output:
                duration = user_preferences_output['durata']
                duration_analysis = {
                    "duration_value": duration,
                    "duration_type": type(duration).__name__,
                    "is_number": isinstance(duration, (int, float)),
                    "number_duration": float(duration) if isinstance(duration, (int, float, str)) and str(duration).replace('.','').isdigit() else None
                }
                
                # Apply the same logic as workflow
                if isinstance(duration, (int, float)) or (isinstance(duration, str) and duration.replace('.','').isdigit()):
                    num_duration = float(duration)
                    if num_duration <= 3:
                        duration_analysis["expected_branch"] = "short_trip"
                    elif num_duration >= 5:
                        duration_analysis["expected_branch"] = "long_trip"
                    else:
                        duration_analysis["expected_branch"] = "unmanaged_duration (4 days)"
            
            return {
                "workflow_id": wf.workflow_id,
                "workflow_status": wf.status,
                "user_preferences_output": user_preferences_output,
                "trip_decision_status": trip_decision_branch,
                "duration_analysis": duration_analysis,
                "total_tasks": len(wf.tasks),
                "task_list": [{"ref": task.reference_task_name, "status": task.status} for task in wf.tasks]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def is_workflow_stuck(self, wf_id: str) -> Dict[str, Any]:
        """
        Analyze if workflow is stuck and determine the cause.
        
        This method identifies common workflow blocking scenarios,
        particularly the 4-day duration issue that isn't handled
        by the current workflow design.
        
        Args:
            wf_id (str): Workflow ID to analyze
            
        Returns:
            Dict[str, Any]: Analysis results indicating if workflow is stuck,
                           the reason, and suggested remediation
        """
        try:
            wf = self.executor.get_workflow(workflow_id=wf_id, include_tasks=True)
            
            # Check workflow task completion status
            completed_tasks = [task for task in wf.tasks if task.status == "COMPLETED"]
            scheduled_tasks = [task for task in wf.tasks if task.status == "SCHEDULED"]
            
            # Look for LogUnhandledDuration task (indicates 4-day duration problem)
            unhandled_duration_task = None
            for task in wf.tasks:
                if task.reference_task_name == "LogUnhandledDuration":
                    unhandled_duration_task = task
                    break
            
            analysis = {
                "workflow_status": wf.status,
                "total_tasks": len(wf.tasks),
                "completed_tasks": len(completed_tasks),
                "scheduled_tasks": len(scheduled_tasks),
                "has_unhandled_duration": unhandled_duration_task is not None,
                "is_stuck": False,
                "reason": None
            }
            
            # Determine if workflow is stuck
            if unhandled_duration_task:
                analysis["is_stuck"] = True
                analysis["reason"] = "Duration of 4 days is not handled by the workflow"
            elif len(completed_tasks) == 1 and completed_tasks[0].reference_task_name == "UserPreferences" and len(scheduled_tasks) == 0:
                analysis["is_stuck"] = True
                analysis["reason"] = "Workflow stopped after UserPreferences - check switch logic"
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}