# ComfyUI Workflow Management - CLEANED UP FOR CONSISTENCY
# Handles loading, modifying, and validating workflows
# Pure workflow operations with minimal output

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import copy
from backend.utils import print_error, print_warning

class WorkflowManager:
    """
    Manages ComfyUI workflow loading and modification
    Handles JSON workflow files and parameter injection
    """
    
    def __init__(self, workflows_dir: Optional[Path] = None):
        if workflows_dir is None:
            workflows_dir = Path(__file__).parent / 'workflows'
        
        self.workflows_dir = Path(workflows_dir)
        self._workflow_cache = {}  # Cache loaded workflows
    
    def load_workflow(self, workflow_name: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Load a workflow from JSON file
        
        Args:
            workflow_name (str): Name of workflow file (without .json)
            use_cache (bool): Whether to use cached version
            
        Returns:
            dict: Workflow definition or None if not found
        """
        # Check cache first
        if use_cache and workflow_name in self._workflow_cache:
            return copy.deepcopy(self._workflow_cache[workflow_name])
        
        try:
            workflow_path = self.workflows_dir / f"{workflow_name}.json"
            
            if not workflow_path.exists():
                print_error(f"Workflow file not found: {workflow_path}")
                return None
            
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow = json.load(f)
            
            # Cache the workflow
            self._workflow_cache[workflow_name] = workflow
            
            return copy.deepcopy(workflow)
            
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON in workflow {workflow_name}: {e}")
            return None
        except Exception as e:
            print_error(f"Error loading workflow {workflow_name}: {e}")
            return None
    
    def modify_workflow_prompt(self, workflow: Dict[str, Any],
                             positive_prompt: str,
                             negative_prompt: Optional[str] = None,
                             **kwargs) -> Dict[str, Any]:
        """
        Modify workflow with new prompts and parameters
        
        Args:
            workflow (dict): Base workflow definition
            positive_prompt (str): New positive prompt
            negative_prompt (str): Optional negative prompt override
            **kwargs: Additional parameters (seed, steps, cfg, etc.)
            
        Returns:
            dict: Modified workflow (new copy)
        """
        # Create deep copy to avoid modifying original
        modified = copy.deepcopy(workflow)
        
        # Update positive prompt (node 5 in monster_generation workflow)
        if "5" in modified and "inputs" in modified["5"]:
            modified["5"]["inputs"]["text"] = positive_prompt
        else:
            print_warning("No positive prompt node found (node 5)")
        
        # Update negative prompt if provided (node 6)
        if negative_prompt and "6" in modified and "inputs" in modified["6"]:
            modified["6"]["inputs"]["text"] = negative_prompt
        
        # Update KSampler parameters (node 2)
        if "2" in modified and "inputs" in modified["2"]:
            sampler_inputs = modified["2"]["inputs"]
            
            # Update parameters if provided
            if "seed" in kwargs:
                sampler_inputs["seed"] = kwargs["seed"]
            
            if "steps" in kwargs:
                sampler_inputs["steps"] = kwargs["steps"]
            
            if "cfg" in kwargs:
                sampler_inputs["cfg"] = kwargs["cfg"]
            
            if "denoise" in kwargs:
                sampler_inputs["denoise"] = kwargs["denoise"]
        
        # Update image dimensions (node 7)
        if "7" in modified and "inputs" in modified["7"]:
            latent_inputs = modified["7"]["inputs"]
            
            if "width" in kwargs:
                latent_inputs["width"] = kwargs["width"]
            
            if "height" in kwargs:
                latent_inputs["height"] = kwargs["height"]
            
            if "batch_size" in kwargs:
                latent_inputs["batch_size"] = kwargs["batch_size"]
        
        return modified
    
    def validate_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate workflow structure and required nodes
        
        Args:
            workflow (dict): Workflow to validate
            
        Returns:
            dict: Validation results with success status and issues
        """
        issues = []
        required_nodes = {}
        
        # Check for essential nodes in monster generation workflow
        essential_nodes = {
            "1": "CheckpointLoaderSimple",
            "2": "KSampler", 
            "3": "VAEDecode",
            "4": "SaveImage",
            "5": "CLIPTextEncode",  # Positive prompt
            "6": "CLIPTextEncode",  # Negative prompt
            "7": "EmptyLatentImage"
        }
        
        for node_id, expected_type in essential_nodes.items():
            if node_id not in workflow:
                issues.append(f"Missing node {node_id} ({expected_type})")
            else:
                node = workflow[node_id]
                if "class_type" not in node:
                    issues.append(f"Node {node_id} missing class_type")
                elif node["class_type"] != expected_type:
                    issues.append(f"Node {node_id} wrong type: {node['class_type']} (expected {expected_type})")
                else:
                    required_nodes[node_id] = node
        
        # Check node connections
        if "2" in required_nodes:  # KSampler
            inputs = required_nodes["2"].get("inputs", {})
            required_connections = ["model", "positive", "negative", "latent_image"]
            
            for connection in required_connections:
                if connection not in inputs:
                    issues.append(f"KSampler missing {connection} connection")
        
        return {
            "success": len(issues) == 0,
            "issues": issues,
            "nodes_found": len(required_nodes),
            "total_nodes": len(workflow)
        }
    
    def list_available_workflows(self) -> List[str]:
        """
        Get list of available workflow files
        
        Returns:
            list: Workflow names (without .json extension)
        """
        try:
            workflow_files = list(self.workflows_dir.glob("*.json"))
            return [f.stem for f in workflow_files]
        except Exception as e:
            print_error(f"Error listing workflows: {e}")
            return []
    

# Global instance
_workflow_manager = None

def get_workflow_manager() -> WorkflowManager:
    """Get global workflow manager instance"""
    global _workflow_manager
    
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager()
    
    return _workflow_manager