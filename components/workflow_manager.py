"""
Workflow management for TripMatch application
"""

import time
import streamlit as st
from typing import Dict, Any, Optional

from conductor.client.workflow.executor.workflow_executor import WorkflowExecutor
from conductor.client.orkes.orkes_task_client import OrkesTaskClient

from config.app_config import AppConfig
from utils.session_state import SessionState

class WorkflowManager:
    """Manages Orkes Conductor workflow operations"""
    
    def __init__(self, executor: WorkflowExecutor, task_client: OrkesTaskClient):
        self.executor = executor
        self.task_client = task_client
    
    def start_workflow(self, workflow_input: Dict[str, Any] = None) -> Optional[str]:
        """Start a new workflow and return workflow ID"""
        try:
            # Usa la stessa configurazione del codice originale
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
        """Fetch a task by reference name - stessa logica del codice originale"""
        try:
            wf = self.executor.get_workflow(workflow_id=wf_id, include_tasks=True)
            for task in wf.tasks:
                if task.reference_task_name == ref_name and task.status in ("SCHEDULED", "IN_PROGRESS"):
                    return task
        except Exception as e:
            st.error(f"Error fetching task {ref_name}: {e}")
        return None
    
    def complete_task(self, task_id: str, status: str = "COMPLETED", output: Dict[str, Any] = None) -> bool:
        """Complete a task - stessa logica del codice originale"""
        try:
            # Stessa implementazione del codice originale funzionante
            task = self.task_client.get_task(task_id)
            task_type = task.task_type  # Usa l'attributo, non la chiave
            
            # Fai il poll per acquisire il task
            self.task_client.poll_task(task_type=task_type, worker_id="streamlit_ui")
            
            # Completa il task
            self.task_client.update_task({
                "taskId": task_id,
                "workflowInstanceId": SessionState.get("workflow_id"),
                "workerId": "streamlit_ui",
                "status": status,
                "outputData": output or {}
            })
            
            return True
        except Exception as e:
            st.error(f"Error completing task: {e}")
            return False
    
    def wait_for_output_key(self, wf_id: str, key: str, msg: str) -> Optional[Any]:
        """Wait for an output key - stessa logica del codice originale"""
        with st.spinner(msg):
            while True:
                try:
                    wf = self.executor.get_workflow(workflow_id=wf_id, include_tasks=False)
                    if wf.output and wf.output.get(key):
                        return wf.output[key]
                    time.sleep(2)
                except Exception as e:
                    st.error(f"Error while waiting for output: {e}")
                    return None
    
    def cache_task(self, ref_name: str, state_key: str):
        """Cache a task ID in session state - stessa logica del codice originale"""
        if SessionState.get(state_key) is None and SessionState.get("workflow_id"):
            task = self.fetch_task_by_ref(SessionState.get("workflow_id"), ref_name)
            if task:
                SessionState.set(state_key, task.task_id)
    
    def wait_for_task_to_be_available(self, wf_id: str, ref_name: str, timeout: int = 30) -> Optional[str]:
        """Wait for a task to become available and return its task_id"""
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
        """Cache a task ID in session state, waiting for it to become available"""
        if SessionState.get(state_key) is None and SessionState.get("workflow_id"):
            task_id = self.wait_for_task_to_be_available(SessionState.get("workflow_id"), ref_name, timeout)
            if task_id:
                SessionState.set(state_key, task_id)
                return True
            return False
        return SessionState.get(state_key) is not None
    
    def get_workflow_status(self, wf_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status"""
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
        """Wait for ShowItinerary task - stessa logica del codice originale"""
        with st.spinner("Elaboro itinerario…"):
            while True:
                try:
                    task = self.fetch_task_by_ref(wf_id, "ShowItinerary")
                    if task:
                        # Gestisce sia input_data che inputData per compatibilità
                        input_data = getattr(task, 'input_data', None) or getattr(task, 'inputData', None)
                        if input_data and "itinerary" in input_data:
                            return input_data["itinerary"]
                    time.sleep(2)
                except Exception as e:
                    st.error(f"Error waiting for itinerary task: {e}")
                    return None
    
    def terminate_workflow(self, wf_id: str, reason: str = "User terminated") -> bool:
        """Terminate a workflow"""
        try:
            self.executor.terminate_workflow(workflow_id=wf_id, reason=reason)
            return True
        except Exception as e:
            st.error(f"Error terminating workflow: {e}")
            return False
    
    def is_workflow_completed(self, wf_id: str) -> bool:
        """Check if workflow is completed"""
        try:
            wf = self.executor.get_workflow(workflow_id=wf_id, include_tasks=False)
            return wf.status == "COMPLETED"
        except Exception as e:
            st.error(f"Error checking workflow completion: {e}")
            return False
    
    def is_workflow_failed(self, wf_id: str) -> bool:
        """Check if workflow has failed"""
        try:
            wf = self.executor.get_workflow(workflow_id=wf_id, include_tasks=False)
            return wf.status in ["FAILED", "TERMINATED", "TIMED_OUT"]
        except Exception as e:
            st.error(f"Error checking workflow failure: {e}")
            return False
    
    def get_workflow_debug_info(self, wf_id: str) -> Dict[str, Any]:
        """Get detailed workflow debug information"""
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
        """Debug the workflow switch logic to understand which branch was taken"""
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
        """Check if workflow is stuck and why"""
        try:
            wf = self.executor.get_workflow(workflow_id=wf_id, include_tasks=True)
            
            # Check if workflow has only UserPreferences completed
            completed_tasks = [task for task in wf.tasks if task.status == "COMPLETED"]
            scheduled_tasks = [task for task in wf.tasks if task.status == "SCHEDULED"]
            
            # Look for LogUnhandledDuration task
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
            
            # Determine if stuck
            if unhandled_duration_task:
                analysis["is_stuck"] = True
                analysis["reason"] = "Duration of 4 days is not handled by the workflow"
            elif len(completed_tasks) == 1 and completed_tasks[0].reference_task_name == "UserPreferences" and len(scheduled_tasks) == 0:
                analysis["is_stuck"] = True
                analysis["reason"] = "Workflow stopped after UserPreferences - check switch logic"
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}