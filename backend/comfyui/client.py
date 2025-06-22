# ComfyUI Client - API Communication
# Handles all HTTP communication with ComfyUI server
# No business logic, just clean API calls

import requests
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path

class ComfyUIClient:
    """
    Pure API client for ComfyUI server communication
    Handles requests, responses, and error handling
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8188"):
        self.base_url = base_url
        self.client_id = str(uuid.uuid4())
        self.timeout = 30
    
    def is_server_running(self) -> bool:
        """
        Test if ComfyUI server is accessible
        
        Returns:
            bool: True if server responds to queue check
        """
        try:
            response = requests.get(f"{self.base_url}/queue", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def queue_prompt(self, workflow: Dict[str, Any]) -> Optional[str]:
        """
        Queue a workflow for generation
        
        Args:
            workflow (dict): Complete workflow definition
            
        Returns:
            str: Prompt ID if successful, None if failed
            
        Raises:
            requests.RequestException: On connection errors
            ValueError: On invalid response
        """
        payload = {
            "prompt": workflow,
            "client_id": self.client_id
        }
        
        response = requests.post(
            f"{self.base_url}/prompt",
            json=payload,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            prompt_id = result.get("prompt_id")
            if not prompt_id:
                raise ValueError("No prompt_id in response")
            return prompt_id
        else:
            raise requests.RequestException(
                f"Queue failed: {response.status_code} - {response.text}"
            )
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current queue status
        
        Returns:
            dict: Queue status with running and pending items
            
        Raises:
            requests.RequestException: On connection errors
        """
        response = requests.get(f"{self.base_url}/queue", timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def get_history(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        Get generation history for a specific prompt
        
        Args:
            prompt_id (str): Prompt ID to check
            
        Returns:
            dict: History data or None if not found
            
        Raises:
            requests.RequestException: On connection errors
        """
        response = requests.get(
            f"{self.base_url}/history/{prompt_id}", 
            timeout=self.timeout
        )
        response.raise_for_status()
        
        history_data = response.json()
        return history_data.get(prompt_id)
    
    def download_image(self, filename: str, subfolder: str = "", 
                      img_type: str = "output") -> bytes:
        """
        Download an image from ComfyUI
        
        Args:
            filename (str): Image filename
            subfolder (str): Subfolder path
            img_type (str): Image type (output, input, temp)
            
        Returns:
            bytes: Image data
            
        Raises:
            requests.RequestException: On download errors
        """
        params = {
            "filename": filename,
            "type": img_type
        }
        if subfolder:
            params["subfolder"] = subfolder
        
        response = requests.get(
            f"{self.base_url}/view", 
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        return response.content
    
    def free_memory(self) -> bool:
        """
        Request ComfyUI to free GPU memory
        
        Returns:
            bool: True if request was successful
        """
        try:
            response = requests.post(f"{self.base_url}/free", timeout=self.timeout)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def interrupt_generation(self) -> bool:
        """
        Interrupt current generation
        
        Returns:
            bool: True if request was successful
        """
        try:
            response = requests.post(f"{self.base_url}/interrupt", timeout=self.timeout)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def wait_for_completion(self, prompt_id: str, 
                          timeout: int = 300,
                          poll_interval: float = 2.0) -> Dict[str, Any]:
        """
        Wait for a prompt to complete generation
        
        Args:
            prompt_id (str): Prompt ID to wait for
            timeout (int): Maximum wait time in seconds
            poll_interval (float): Time between status checks
            
        Returns:
            dict: Completion status and results
            
        Raises:
            TimeoutError: If generation takes longer than timeout
            requests.RequestException: On communication errors
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check if prompt is still in queue
            queue_status = self.get_queue_status()
            
            running = any(item[1] == prompt_id for item in queue_status.get("queue_running", []))
            pending = any(item[1] == prompt_id for item in queue_status.get("queue_pending", []))
            
            # If not in queue, check history for completion
            if not running and not pending:
                history = self.get_history(prompt_id)
                
                if history and "outputs" in history:
                    # Extract image information
                    images = []
                    outputs = history["outputs"]
                    
                    for node_id, node_output in outputs.items():
                        if "images" in node_output:
                            for img_info in node_output["images"]:
                                images.append({
                                    "filename": img_info["filename"],
                                    "subfolder": img_info.get("subfolder", ""),
                                    "type": img_info.get("type", "output")
                                })
                    
                    return {
                        "success": True,
                        "completed": True,
                        "images": images,
                        "execution_time": time.time() - start_time
                    }
                elif history:
                    # Completed but no outputs (likely an error)
                    return {
                        "success": False,
                        "completed": True,
                        "error": "Generation completed but produced no outputs",
                        "execution_time": time.time() - start_time
                    }
                else:
                    # Not found in history yet, continue waiting
                    pass
            
            # Still processing, wait and check again
            time.sleep(poll_interval)
        
        # Timeout reached
        raise TimeoutError(f"Generation timed out after {timeout} seconds")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get ComfyUI system statistics (if available)
        
        Returns:
            dict: System stats or empty dict if not available
        """
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        
        return {}