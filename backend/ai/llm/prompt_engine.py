# Prompt Engine - Template Management
# Lean template loading and building system
print(f"🔍 Loading {__file__}")
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from backend.core.utils import print_success, print_error, print_warning

@dataclass
class PromptTemplate:
    """A single prompt template"""
    name: str
    description: str
    template: str
    max_tokens: int
    temperature: float
    parser_config: Dict[str, Any]
    category: str = "general"

class PromptEngine:
    """Manages prompt templates"""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        if templates_dir is None:
            templates_dir = Path(__file__).parent / 'prompts'
        
        self.templates_dir = Path(templates_dir)
        self._templates = {}  # name -> PromptTemplate
        self._loaded = False
    
    def load_templates(self) -> bool:
        """Load all templates from JSON files"""
        if self._loaded:
            return True
        
        self._templates.clear()
        
        try:
            if not self.templates_dir.exists():
                print_warning(f"Templates dir not found: {self.templates_dir}")
                return False
            
            # Load all JSON files
            for template_file in self.templates_dir.glob("*.json"):
                self._load_file(template_file)
            
            self._loaded = True
            print_success(f"Loaded {len(self._templates)} templates")
            return True
            
        except Exception as e:
            print_error(f"Error loading templates: {e}")
            return False
    
    def _load_file(self, file_path: Path):
        """Load templates from one JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        category = file_path.stem
        
        for name, config in data.items():
            template = PromptTemplate(
                name=name,
                description=config.get('description', 'No description'),
                template=config['prompt_template'],
                max_tokens=config.get('max_tokens', 256),
                temperature=config.get('temperature', 0.8),
                parser_config=config.get('parser', {}),
                category=category
            )
            
            self._templates[name] = template
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name"""
        if not self._loaded:
            self.load_templates()
        
        return self._templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List all template names"""
        if not self._loaded:
            self.load_templates()
        
        return list(self._templates.keys())
    
    def build_prompt(self, template_name: str, variables: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Build a prompt from template"""
        template = self.get_template(template_name)
        if not template:
            return None
        
        prompt = template.template
        
        if variables:
            try:
                prompt = prompt.format(**variables)
            except Exception as e:
                print_error(f"Error formatting template {template_name}: {e}")
                return None
        
        return prompt
    
    def get_template_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Get template as config dict"""
        template = self.get_template(name)
        if not template:
            return None
        
        return {
            'name': template.name,
            'description': template.description,
            'prompt_template': template.template,
            'max_tokens': template.max_tokens,
            'temperature': template.temperature,
            'parser': template.parser_config,
            'category': template.category
        }

# Global instance
_engine = None

def get_prompt_engine() -> PromptEngine:
    """Get global prompt engine"""
    global _engine
    
    if _engine is None:
        _engine = PromptEngine()
        _engine.load_templates()
    
    return _engine

def build_prompt(template_name: str, variables: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Build a prompt"""
    return get_prompt_engine().build_prompt(template_name, variables)

def get_template_config(name: str) -> Optional[Dict[str, Any]]:
    """Get template config"""
    return get_prompt_engine().get_template_config(name)