"""
Documentation Service for Whysper

This service provides comprehensive code analysis and documentation generation
capabilities, supporting multiple programming languages and documentation formats.
"""

import os
import re
import ast
import json
import uuid
import zipfile
import tempfile
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import logging

from common.logger import get_logger
from common.ai import create_ai_processor
from app.services.file_service import file_service
from security_utils import SecurityUtils

logger = get_logger(__name__)


@dataclass
class CodeStructure:
    """Represents the analyzed structure of code files"""
    file_path: str
    language: str
    imports: List[str] = field(default_factory=list)
    classes: List[Dict[str, Any]] = field(default_factory=list)
    functions: List[Dict[str, Any]] = field(default_factory=list)
    variables: List[Dict[str, Any]] = field(default_factory=list)
    constants: List[Dict[str, Any]] = field(default_factory=list)
    docstrings: List[Dict[str, Any]] = field(default_factory=list)
    comments: List[Dict[str, Any]] = field(default_factory=list)
    relationships: Dict[str, List[str]] = field(default_factory=dict)
    complexity_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentationRequest:
    """Request structure for documentation generation"""
    file_paths: List[str]
    documentation_type: str  # api, readme, architecture, examples, all
    output_format: str = "markdown"  # markdown, html, pdf, jsdoc, sphinx
    template: Optional[str] = None
    include_examples: bool = True
    include_diagrams: bool = True
    target_audience: str = "developers"  # developers, users, mixed
    language: Optional[str] = None  # Force specific documentation language


@dataclass
class DocumentationResult:
    """Result structure for documentation generation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    diagrams: List[Dict[str, Any]] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    processing_time: float = 0.0
    token_usage: Dict[str, int] = field(default_factory=dict)


class DocumentationService:
    """
    Service for analyzing code structure and generating comprehensive documentation.
    
    This service provides the core functionality for the Documentation Generator
    feature, including code parsing, structure analysis, and AI-powered documentation
    generation.
    """
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.DocumentationService")
        self.supported_languages = {
            'python': self._analyze_python,
            'javascript': self._analyze_javascript,
            'typescript': self._analyze_typescript,
            'java': self._analyze_java,
            'go': self._analyze_go,
            'rust': self._analyze_rust,
            'cpp': self._analyze_cpp,
            'c': self._analyze_c,
        }
        
        # Load templates
        self.templates = self._load_templates()
        
        # Initialize AI processor
        self.ai_processor = None
        self.cache = {}
    
    def _initialize_ai_processor(self):
        """Initialize AI processor with current settings"""
        try:
            from app.core.config import load_env_defaults
            env_config = load_env_defaults()
            api_key = env_config.get("api_key", "")
            provider = env_config.get("provider", "openrouter")
            
            if api_key:
                self.ai_processor = create_ai_processor(api_key=api_key, provider=provider)
                self.logger.info("AI processor initialized for documentation generation")
            else:
                self.logger.warning("API key not configured, documentation generation will be limited")
        except Exception as e:
            self.logger.error(f"Failed to initialize AI processor: {e}")
    
    def analyze_code_structure(self, file_paths: List[str]) -> List[CodeStructure]:
        """
        Analyze the structure of the provided code files.
        
        Args:
            file_paths: List of file paths to analyze
            
        Returns:
            List of CodeStructure objects representing analyzed files
        """
        self.logger.info(f"Analyzing code structure for {len(file_paths)} files")
        
        structures = []
        env_vars = env_manager.load_env_file()
        code_path = env_vars.get("CODE_PATH", os.getcwd())
        
        for file_path in file_paths:
            try:
                # Determine language from file extension
                language = self._detect_language(file_path)
                
                if language in self.supported_languages:
                    # Read file content
                    safe_path = SecurityUtils.safe_path_resolve(code_path, file_path)
                    if not safe_path:
                        self.logger.error(f"Path resolution failed for {file_path}")
                        continue
                    content = file_service.read_file(safe_path)
                    
                    # Analyze based on language
                    analyzer = self.supported_languages[language]
                    structure = analyzer(file_path, content)
                    
                    structures.append(structure)
                    self.logger.debug(f"Analyzed {file_path} ({language})")
                else:
                    self.logger.warning(f"Unsupported language for file: {file_path}")
                    
            except Exception as e:
                self.logger.error(f"Error analyzing file {file_path}: {e}")
                continue
        
        self.logger.info(f"Successfully analyzed {len(structures)} files")
        return structures
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        extension = Path(file_path).suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.cxx': 'cpp',
            '.cc': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
        }
        
        return language_map.get(extension, 'unknown')
    
    def _analyze_python(self, file_path: str, content: str) -> CodeStructure:
        """Analyze Python code structure"""
        try:
            tree = ast.parse(content)
            
            structure = CodeStructure(
                file_path=file_path,
                language='python',
                imports=self._extract_python_imports(tree),
                classes=self._extract_python_classes(tree),
                functions=self._extract_python_functions(tree),
                variables=self._extract_python_variables(tree),
                constants=self._extract_python_constants(tree),
                docstrings=self._extract_python_docstrings(tree),
                comments=self._extract_python_comments(content),
                relationships=self._analyze_python_relationships(tree),
                complexity_metrics=self._calculate_python_complexity(tree)
            )
            
            return structure
            
        except SyntaxError as e:
            self.logger.error(f"Syntax error in Python file {file_path}: {e}")
            return CodeStructure(file_path=file_path, language='python')
    
    def _extract_python_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements from Python AST"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)
        
        return imports
    
    def _extract_python_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract class definitions from Python AST"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                attributes = []
                
                # Extract methods
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method = {
                            'name': item.name,
                            'line_number': item.lineno,
                            'args': [arg.arg for arg in item.args.args],
                            'returns': ast.unparse(item.returns) if hasattr(ast, 'unparse') and item.returns else None,
                            'docstring': ast.get_docstring(item),
                            'is_async': isinstance(item, ast.AsyncFunctionDef),
                            'decorators': [ast.unparse(d) for d in item.decorator_list] if hasattr(ast, 'unparse') else []
                        }
                        methods.append(method)
                
                # Extract attributes (class variables)
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                attributes.append({
                                    'name': target.id,
                                    'line_number': item.lineno
                                })
                
                class_info = {
                    'name': node.name,
                    'line_number': node.lineno,
                    'base_classes': [base.id for base in node.bases if isinstance(base, ast.Name)],
                    'methods': methods,
                    'attributes': attributes,
                    'docstring': ast.get_docstring(node),
                    'decorators': [ast.unparse(d) for d in node.decorator_list] if hasattr(ast, 'unparse') else []
                }
                
                classes.append(class_info)
        
        return classes
    
    def _extract_python_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract function definitions from Python AST"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip methods (they're extracted with classes)
                parent_classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                is_method = False
                for parent in parent_classes:
                    if node in parent.body:
                        is_method = True
                        break
                
                if not is_method:
                    function_info = {
                        'name': node.name,
                        'line_number': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'returns': ast.unparse(node.returns) if hasattr(ast, 'unparse') and node.returns else None,
                        'docstring': ast.get_docstring(node),
                        'is_async': isinstance(node, ast.AsyncFunctionDef),
                        'decorators': [ast.unparse(d) for d in node.decorator_list] if hasattr(ast, 'unparse') else []
                    }
                    
                    functions.append(function_info)
        
        return functions
    
    def _extract_python_variables(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract variable assignments from Python AST"""
        variables = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and not target.id.isupper():
                        variables.append({
                            'name': target.id,
                            'line_number': node.lineno,
                            'type': ast.unparse(node.value) if hasattr(ast, 'unparse') else None
                        })
        
        return variables
    
    def _extract_python_constants(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract constant assignments from Python AST"""
        constants = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        constants.append({
                            'name': target.id,
                            'line_number': node.lineno,
                            'value': ast.unparse(node.value) if hasattr(ast, 'unparse') else None
                        })
        
        return constants
    
    def _extract_python_docstrings(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract docstrings from Python AST"""
        docstrings = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                docstring = ast.get_docstring(node)
                if docstring:
                    docstrings.append({
                        'content': docstring,
                        'line_number': node.lineno if not isinstance(node, ast.Module) else 1,
                        'type': type(node).__name__
                    })
        
        return docstrings
    
    def _extract_python_comments(self, content: str) -> List[Dict[str, Any]]:
        """Extract comments from Python code"""
        comments = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('#'):
                comments.append({
                    'content': stripped[1:].strip(),
                    'line_number': i,
                    'type': 'comment'
                })
        
        return comments
    
    def _analyze_python_relationships(self, tree: ast.AST) -> Dict[str, List[str]]:
        """Analyze relationships between Python code elements"""
        relationships = {
            'imports': [],
            'inheritance': [],
            'dependencies': []
        }
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    relationships['imports'].append(name.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for name in node.names:
                    relationships['imports'].append(f"{module}.{name.name}" if module else name.name)
        
        # Extract inheritance relationships
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        relationships['inheritance'].append(f"{node.name} -> {base.id}")
        
        return relationships
    
    def _calculate_python_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        """Calculate complexity metrics for Python code"""
        metrics = {
            'lines_of_code': len(tree.body),
            'functions': 0,
            'classes': 0,
            'complexity_score': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics['functions'] += 1
                # Simple complexity calculation based on control structures
                complexity = 1
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                        complexity += 1
                metrics['complexity_score'] += complexity
            elif isinstance(node, ast.ClassDef):
                metrics['classes'] += 1
        
        return metrics
    
    def _analyze_javascript(self, file_path: str, content: str) -> CodeStructure:
        """Analyze JavaScript code structure"""
        structure = CodeStructure(
            file_path=file_path,
            language='javascript',
            imports=self._extract_js_imports(content),
            classes=self._extract_js_classes(content),
            functions=self._extract_js_functions(content),
            variables=self._extract_js_variables(content),
            constants=self._extract_js_constants(content),
            docstrings=self._extract_js_docstrings(content),
            comments=self._extract_js_comments(content),
            relationships=self._analyze_js_relationships(content),
            complexity_metrics=self._calculate_js_complexity(content)
        )
        
        return structure
    
    def _extract_js_imports(self, content: str) -> List[str]:
        """Extract import statements from JavaScript code"""
        imports = []
        
        # Match ES6 imports
        import_pattern = r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1))
        
        # Match CommonJS requires
        require_pattern = r'(?:const|let|var)\s+.*?\s*=\s*require\([\'"]([^\'"]+)[\'"]\)'
        for match in re.finditer(require_pattern, content):
            imports.append(match.group(1))
        
        return imports
    
    def _extract_js_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract class definitions from JavaScript code"""
        classes = []
        
        # Match ES6 classes
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            base_class = match.group(2) if match.group(2) else None
            
            # Find methods within the class
            class_start = match.start()
            brace_count = 0
            in_class = False
            class_end = class_start
            
            for i, char in enumerate(content[class_start:], class_start):
                if char == '{':
                    brace_count += 1
                    in_class = True
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0 and in_class:
                        class_end = i
                        break
            
            class_content = content[class_start:class_end]
            
            # Extract methods
            methods = []
            method_pattern = r'(?:async\s+)?(?:\w+\s+)?(\w+)\s*\([^)]*\)\s*\{'
            for method_match in re.finditer(method_pattern, class_content):
                method_name = method_match.group(1)
                if method_name != 'class':  # Skip the class declaration itself
                    methods.append({
                        'name': method_name,
                        'line_number': content[:class_start + method_match.start()].count('\n') + 1
                    })
            
            classes.append({
                'name': class_name,
                'base_classes': [base_class] if base_class else [],
                'methods': methods,
                'line_number': content[:class_start].count('\n') + 1
            })
        
        return classes
    
    def _extract_js_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function definitions from JavaScript code"""
        functions = []
        
        # Match function declarations
        func_pattern = r'(?:async\s+)?function\s+(\w+)\s*\([^)]*\)'
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1)
            functions.append({
                'name': func_name,
                'line_number': content[:match.start()].count('\n') + 1,
                'is_async': 'async' in content[:match.start()].split()[-5:]  # Check if async is nearby
            })
        
        # Match arrow functions assigned to variables
        arrow_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>'
        for match in re.finditer(arrow_pattern, content):
            func_name = match.group(1)
            functions.append({
                'name': func_name,
                'line_number': content[:match.start()].count('\n') + 1,
                'is_arrow': True
            })
        
        return functions
    
    def _extract_js_variables(self, content: str) -> List[Dict[str, Any]]:
        """Extract variable declarations from JavaScript code"""
        variables = []
        
        # Match variable declarations
        var_pattern = r'(?:const|let|var)\s+(\w+)\s*='
        for match in re.finditer(var_pattern, content):
            var_name = match.group(1)
            if not var_name.isupper():  # Skip constants
                variables.append({
                    'name': var_name,
                    'line_number': content[:match.start()].count('\n') + 1
                })
        
        return variables
    
    def _extract_js_constants(self, content: str) -> List[Dict[str, Any]]:
        """Extract constant declarations from JavaScript code"""
        constants = []
        
        # Match constant declarations
        const_pattern = r'const\s+(\w+)\s*='
        for match in re.finditer(const_pattern, content):
            const_name = match.group(1)
            if const_name.isupper():  # Only include uppercase constants
                constants.append({
                    'name': const_name,
                    'line_number': content[:match.start()].count('\n') + 1
                })
        
        return constants
    
    def _extract_js_docstrings(self, content: str) -> List[Dict[str, Any]]:
        """Extract JSDoc comments from JavaScript code"""
        docstrings = []
        
        # Match JSDoc comments
        jsdoc_pattern = r'/\*\*\s*\n(.*?)\s*\*/'
        for match in re.finditer(jsdoc_pattern, content, re.DOTALL):
            doc_content = match.group(1)
            # Clean up the docstring
            doc_lines = [line.strip().lstrip('*') for line in doc_content.split('\n')]
            cleaned_doc = '\n'.join(doc_lines).strip()
            
            docstrings.append({
                'content': cleaned_doc,
                'line_number': content[:match.start()].count('\n') + 1,
                'type': 'jsdoc'
            })
        
        return docstrings
    
    def _extract_js_comments(self, content: str) -> List[Dict[str, Any]]:
        """Extract comments from JavaScript code"""
        comments = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                comments.append({
                    'content': stripped[2:].strip(),
                    'line_number': i,
                    'type': 'line_comment'
                })
        
        return comments
    
    def _analyze_js_relationships(self, content: str) -> Dict[str, List[str]]:
        """Analyze relationships between JavaScript code elements"""
        relationships = {
            'imports': self._extract_js_imports(content),
            'inheritance': [],
            'dependencies': []
        }
        
        # Extract inheritance relationships
        extends_pattern = r'class\s+(\w+)\s+extends\s+(\w+)'
        for match in re.finditer(extends_pattern, content):
            child_class = match.group(1)
            parent_class = match.group(2)
            relationships['inheritance'].append(f"{child_class} -> {parent_class}")
        
        return relationships
    
    def _calculate_js_complexity(self, content: str) -> Dict[str, Any]:
        """Calculate complexity metrics for JavaScript code"""
        lines = content.split('\n')
        
        metrics = {
            'lines_of_code': len([line for line in lines if line.strip() and not line.strip().startswith('//')]),
            'functions': len(self._extract_js_functions(content)),
            'classes': len(self._extract_js_classes(content)),
            'complexity_score': 0
        }
        
        # Simple complexity calculation based on control structures
        control_patterns = [
            r'\bif\b',
            r'\bfor\b',
            r'\bwhile\b',
            r'\bswitch\b',
            r'\btry\b',
            r'\bcatch\b'
        ]
        
        complexity = 0
        for pattern in control_patterns:
            complexity += len(re.findall(pattern, content))
        
        metrics['complexity_score'] = complexity
        
        return metrics
    
    def _analyze_typescript(self, file_path: str, content: str) -> CodeStructure:
        """Analyze TypeScript code structure"""
        # For now, use JavaScript analysis with TypeScript extensions
        structure = self._analyze_javascript(file_path, content)
        structure.language = 'typescript'
        
        # Add TypeScript-specific analysis
        structure.interfaces = self._extract_ts_interfaces(content)
        structure.types = self._extract_ts_types(content)
        
        return structure
    
    def _extract_ts_interfaces(self, content: str) -> List[Dict[str, Any]]:
        """Extract interface definitions from TypeScript code"""
        interfaces = []
        
        # Match interface declarations
        interface_pattern = r'interface\s+(\w+)(?:\s+extends\s+([^{]+))?\s*\{'
        for match in re.finditer(interface_pattern, content):
            interface_name = match.group(1)
            extends_clause = match.group(2) if match.group(2) else None
            
            interfaces.append({
                'name': interface_name,
                'extends': extends_clause.split(',') if extends_clause else [],
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        return interfaces
    
    def _extract_ts_types(self, content: str) -> List[Dict[str, Any]]:
        """Extract type definitions from TypeScript code"""
        types = []
        
        # Match type declarations
        type_pattern = r'type\s+(\w+)\s*=\s*([^;]+);'
        for match in re.finditer(type_pattern, content):
            type_name = match.group(1)
            type_definition = match.group(2)
            
            types.append({
                'name': type_name,
                'definition': type_definition.strip(),
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        return types
    
    def _analyze_java(self, file_path: str, content: str) -> CodeStructure:
        """Analyze Java code structure"""
        structure = CodeStructure(
            file_path=file_path,
            language='java',
            imports=self._extract_java_imports(content),
            classes=self._extract_java_classes(content),
            functions=self._extract_java_methods(content),
            variables=self._extract_java_variables(content),
            constants=self._extract_java_constants(content),
            docstrings=self._extract_java_docstrings(content),
            comments=self._extract_java_comments(content),
            relationships=self._analyze_java_relationships(content),
            complexity_metrics=self._calculate_java_complexity(content)
        )
        
        return structure
    
    def _extract_java_imports(self, content: str) -> List[str]:
        """Extract import statements from Java code"""
        imports = []
        
        # Match import statements
        import_pattern = r'import\s+([^;]+);'
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1).strip())
        
        return imports
    
    def _extract_java_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract class definitions from Java code"""
        classes = []
        
        # Match class declarations
        class_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+|final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            extends_class = match.group(2) if match.group(2) else None
            implements_interfaces = match.group(3).split(',') if match.group(3) else []
            
            classes.append({
                'name': class_name,
                'base_classes': [extends_class] if extends_class else [],
                'interfaces': [iface.strip() for iface in implements_interfaces],
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        return classes
    
    def _extract_java_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract method definitions from Java code"""
        methods = []
        
        # Match method declarations
        method_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:final\s+)?(?:abstract\s+)?(?:\w+\s+)?(\w+)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{'
        for match in re.finditer(method_pattern, content):
            method_name = match.group(1)
            
            # Skip common non-method keywords
            if method_name in ['class', 'interface', 'enum', 'if', 'for', 'while', 'switch', 'try', 'catch', 'finally']:
                continue
            
            methods.append({
                'name': method_name,
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        return methods
    
    def _extract_java_variables(self, content: str) -> List[Dict[str, Any]]:
        """Extract variable declarations from Java code"""
        variables = []
        
        # Match variable declarations
        var_pattern = r'(?:final\s+)?(?:\w+(?:<[^>]+>)?\s+)(\w+)\s*=;'
        for match in re.finditer(var_pattern, content):
            var_name = match.group(1)
            
            # Skip common keywords
            if var_name in ['class', 'interface', 'enum', 'if', 'for', 'while', 'switch', 'try', 'catch', 'finally']:
                continue
            
            variables.append({
                'name': var_name,
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        return variables
    
    def _extract_java_constants(self, content: str) -> List[Dict[str, Any]]:
        """Extract constant declarations from Java code"""
        constants = []
        
        # Match constant declarations (static final)
        const_pattern = r'(?:public\s+|private\s+|protected\s+)?static\s+final\s+(?:\w+(?:<[^>]+>)?\s+)(\w+)\s*=;'
        for match in re.finditer(const_pattern, content):
            const_name = match.group(1)
            constants.append({
                'name': const_name,
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        return constants
    
    def _extract_java_docstrings(self, content: str) -> List[Dict[str, Any]]:
        """Extract Javadoc comments from Java code"""
        docstrings = []
        
        # Match Javadoc comments
        javadoc_pattern = r'/\*\*\s*\n(.*?)\s*\*/'
        for match in re.finditer(javadoc_pattern, content, re.DOTALL):
            doc_content = match.group(1)
            # Clean up the docstring
            doc_lines = [line.strip().lstrip('*') for line in doc_content.split('\n')]
            cleaned_doc = '\n'.join(doc_lines).strip()
            
            docstrings.append({
                'content': cleaned_doc,
                'line_number': content[:match.start()].count('\n') + 1,
                'type': 'javadoc'
            })
        
        return docstrings
    
    def _extract_java_comments(self, content: str) -> List[Dict[str, Any]]:
        """Extract comments from Java code"""
        comments = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                comments.append({
                    'content': stripped[2:].strip(),
                    'line_number': i,
                    'type': 'line_comment'
                })
        
        return comments
    
    def _analyze_java_relationships(self, content: str) -> Dict[str, List[str]]:
        """Analyze relationships between Java code elements"""
        relationships = {
            'imports': self._extract_java_imports(content),
            'inheritance': [],
            'dependencies': []
        }
        
        # Extract inheritance relationships
        extends_pattern = r'class\s+(\w+)\s+extends\s+(\w+)'
        for match in re.finditer(extends_pattern, content):
            child_class = match.group(1)
            parent_class = match.group(2)
            relationships['inheritance'].append(f"{child_class} -> {parent_class}")
        
        # Extract interface implementation relationships
        implements_pattern = r'class\s+(\w+)\s+implements\s+([^{]+)'
        for match in re.finditer(implements_pattern, content):
            class_name = match.group(1)
            interfaces = [iface.strip() for iface in match.group(2).split(',')]
            for interface in interfaces:
                relationships['dependencies'].append(f"{class_name} -> {interface}")
        
        return relationships
    
    def _calculate_java_complexity(self, content: str) -> Dict[str, Any]:
        """Calculate complexity metrics for Java code"""
        lines = content.split('\n')
        
        metrics = {
            'lines_of_code': len([line for line in lines if line.strip() and not line.strip().startswith('//')]),
            'functions': len(self._extract_java_methods(content)),
            'classes': len(self._extract_java_classes(content)),
            'complexity_score': 0
        }
        
        # Simple complexity calculation based on control structures
        control_patterns = [
            r'\bif\b',
            r'\bfor\b',
            r'\bwhile\b',
            r'\bswitch\b',
            r'\btry\b',
            r'\bcatch\b'
        ]
        
        complexity = 0
        for pattern in control_patterns:
            complexity += len(re.findall(pattern, content))
        
        metrics['complexity_score'] = complexity
        
        return metrics
    
    def _analyze_go(self, file_path: str, content: str) -> CodeStructure:
        """Analyze Go code structure"""
        structure = CodeStructure(
            file_path=file_path,
            language='go',
            imports=self._extract_go_imports(content),
            classes=[],  # Go doesn't have classes
            functions=self._extract_go_functions(content),
            variables=self._extract_go_variables(content),
            constants=self._extract_go_constants(content),
            docstrings=self._extract_go_docstrings(content),
            comments=self._extract_go_comments(content),
            relationships=self._analyze_go_relationships(content),
            complexity_metrics=self._calculate_go_complexity(content)
        )
        
        return structure
    
    def _extract_go_imports(self, content: str) -> List[str]:
        """Extract import statements from Go code"""
        imports = []
        
        # Match import statements
        import_pattern = r'import\s*(?:\(\s*(.*?)\s*\)|"([^"]+)")'
        for match in re.finditer(import_pattern, content, re.DOTALL):
            if match.group(1):  # Multiple imports in parentheses
                import_lines = match.group(1).strip().split('\n')
                for line in import_lines:
                    line = line.strip()
                    if line and not line.startswith('"'):
                        line = f'"{line}"'
                    if line.startswith('"') and line.endswith('"'):
                        imports.append(line[1:-1])
            elif match.group(2):  # Single import
                imports.append(match.group(2))
        
        return imports
    
    def _extract_go_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function definitions from Go code"""
        functions = []
        
        # Match function declarations
        func_pattern = r'func\s+(?:\([^)]*\)\s*)?(\w+)\s*\([^)]*\)(?:\s*[^{]+)?\s*\{'
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1)
            functions.append({
                'name': func_name,
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        return functions
    
    def _extract_go_variables(self, content: str) -> List[Dict[str, Any]]:
        """Extract variable declarations from Go code"""
        variables = []
        
        # Match variable declarations
        var_pattern = r'var\s+(\w+)\s+(?:\w+(?:\[\d+\])?(?:\.\w+)*(?:\{[^}]*\})?)'
        for match in re.finditer(var_pattern, content):
            var_name = match.group(1)
            variables.append({
                'name': var_name,
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        # Match short variable declarations
        short_var_pattern = r'(\w+)\s*:=\s*'
        for match in re.finditer(short_var_pattern, content):
            var_name = match.group(1)
            variables.append({
                'name': var_name,
                'line_number': content[:match.start()].count('\n') + 1,
                'type': 'short_declaration'
            })
        
        return variables
    
    def _extract_go_constants(self, content: str) -> List[Dict[str, Any]]:
        """Extract constant declarations from Go code"""
        constants = []
        
        # Match constant declarations
        const_pattern = r'const\s+(\w+)\s+(?:\w+(?:\[\d+\])?(?:\.\w+)*(?:\{[^}]*\})?)'
        for match in re.finditer(const_pattern, content):
            const_name = match.group(1)
            constants.append({
                'name': const_name,
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        return constants
    
    def _extract_go_docstrings(self, content: str) -> List[Dict[str, Any]]:
        """Extract docstrings from Go code"""
        docstrings = []
        
        # Match godoc comments
        godoc_pattern = r'//\s*(.+?)(?=\n//|\n\n|\nfunc|\nvar|\nconst|\ntype|\npackage)'
        for match in re.finditer(godoc_pattern, content, re.DOTALL):
            doc_content = match.group(1).strip()
            if doc_content:
                docstrings.append({
                    'content': doc_content,
                    'line_number': content[:match.start()].count('\n') + 1,
                    'type': 'godoc'
                })
        
        return docstrings
    
    def _extract_go_comments(self, content: str) -> List[Dict[str, Any]]:
        """Extract comments from Go code"""
        comments = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                comments.append({
                    'content': stripped[2:].strip(),
                    'line_number': i,
                    'type': 'line_comment'
                })
        
        return comments
    
    def _analyze_go_relationships(self, content: str) -> Dict[str, List[str]]:
        """Analyze relationships between Go code elements"""
        relationships = {
            'imports': self._extract_go_imports(content),
            'inheritance': [],  # Go doesn't have inheritance
            'dependencies': []
        }
        
        return relationships
    
    def _calculate_go_complexity(self, content: str) -> Dict[str, Any]:
        """Calculate complexity metrics for Go code"""
        lines = content.split('\n')
        
        metrics = {
            'lines_of_code': len([line for line in lines if line.strip() and not line.strip().startswith('//')]),
            'functions': len(self._extract_go_functions(content)),
            'classes': 0,  # Go doesn't have classes
            'complexity_score': 0
        }
        
        # Simple complexity calculation based on control structures
        control_patterns = [
            r'\bif\b',
            r'\bfor\b',
            r'\bswitch\b',
            r'\bselect\b',
            r'\bgo\b',
            r'\bdefer\b'
        ]
        
        complexity = 0
        for pattern in control_patterns:
            complexity += len(re.findall(pattern, content))
        
        metrics['complexity_score'] = complexity
        
        return metrics
    
    def _analyze_rust(self, file_path: str, content: str) -> CodeStructure:
        """Analyze Rust code structure"""
        structure = CodeStructure(
            file_path=file_path,
            language='rust',
            imports=self._extract_rust_imports(content),
            classes=self._extract_rust_structs(content),
            functions=self._extract_rust_functions(content),
            variables=self._extract_rust_variables(content),
            constants=self._extract_rust_constants(content),
            docstrings=self._extract_rust_docstrings(content),
            comments=self._extract_rust_comments(content),
            relationships=self._analyze_rust_relationships(content),
            complexity_metrics=self._calculate_rust_complexity(content)
        )
        
        return structure
    
    def _extract_rust_imports(self, content: str) -> List[str]:
        """Extract import statements from Rust code"""
        imports = []
        
        # Match use statements
        use_pattern = r'use\s+([^;]+);'
        for match in re.finditer(use_pattern, content):
            imports.append(match.group(1).strip())
        
        return imports
    
    def _extract_rust_structs(self, content: str) -> List[Dict[str, Any]]:
        """Extract struct definitions from Rust code"""
        structs = []
        
        # Match struct declarations
        struct_pattern = r'(?:pub\s+)?struct\s+(\w+)(?:\s*<[^>]*>)?(?:\s*\([^)]*\))?\s*\{'
        for match in re.finditer(struct_pattern, content):
            struct_name = match.group(1)
            structs.append({
                'name': struct_name,
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        return structs
    
    def _extract_rust_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function definitions from Rust code"""
        functions = []
        
        # Match function declarations
        func_pattern = r'(?:pub\s+)?(?:async\s+)?(?:extern\s+[^{]*\s+)?fn\s+(\w+)\s*\([^)]*\)(?:\s*->\s*[^{]+)?\s*\{'
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1)
            functions.append({
                'name': func_name,
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        return functions
    
    def _extract_rust_variables(self, content: str) -> List[Dict[str, Any]]:
        """Extract variable declarations from Rust code"""
        variables = []
        
        # Match let statements
        let_pattern = r'let\s+(?:mut\s+)?(\w+)\s*='
        for match in re.finditer(let_pattern, content):
            var_name = match.group(1)
            variables.append({
                'name': var_name,
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        return variables
    
    def _extract_rust_constants(self, content: str) -> List[Dict[str, Any]]:
        """Extract constant declarations from Rust code"""
        constants = []
        
        # Match const statements
        const_pattern = r'const\s+(\w+)\s*:\s*[^=]+\s*='
        for match in re.finditer(const_pattern, content):
            const_name = match.group(1)
            constants.append({
                'name': const_name,
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        return constants
    
    def _extract_rust_docstrings(self, content: str) -> List[Dict[str, Any]]:
        """Extract docstrings from Rust code"""
        docstrings = []
        
        # Match rustdoc comments
        rustdoc_pattern = r'///\s*(.+?)(?=\n///|\n\n|\nfn|\nstruct|\nenum|\ntrait|\nimpl|\nmod|\nuse|\nconst)'
        for match in re.finditer(rustdoc_pattern, content, re.DOTALL):
            doc_content = match.group(1).strip()
            if doc_content:
                docstrings.append({
                    'content': doc_content,
                    'line_number': content[:match.start()].count('\n') + 1,
                    'type': 'rustdoc'
                })
        
        return docstrings
    
    def _extract_rust_comments(self, content: str) -> List[Dict[str, Any]]:
        """Extract comments from Rust code"""
        comments = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                comments.append({
                    'content': stripped[2:].strip(),
                    'line_number': i,
                    'type': 'line_comment'
                })
        
        return comments
    
    def _analyze_rust_relationships(self, content: str) -> Dict[str, List[str]]:
        """Analyze relationships between Rust code elements"""
        relationships = {
            'imports': self._extract_rust_imports(content),
            'inheritance': [],  # Rust doesn't have inheritance
            'dependencies': []
        }
        
        return relationships
    
    def _calculate_rust_complexity(self, content: str) -> Dict[str, Any]:
        """Calculate complexity metrics for Rust code"""
        lines = content.split('\n')
        
        metrics = {
            'lines_of_code': len([line for line in lines if line.strip() and not line.strip().startswith('//')]),
            'functions': len(self._extract_rust_functions(content)),
            'classes': len(self._extract_rust_structs(content)),
            'complexity_score': 0
        }
        
        # Simple complexity calculation based on control structures
        control_patterns = [
            r'\bif\b',
            r'\bmatch\b',
            r'\bloop\b',
            r'\bwhile\b',
            r'\bfor\b',
            r'\basync\b'
        ]
        
        complexity = 0
        for pattern in control_patterns:
            complexity += len(re.findall(pattern, content))
        
        metrics['complexity_score'] = complexity
        
        return metrics
    
    def _analyze_cpp(self, file_path: str, content: str) -> CodeStructure:
        """Analyze C++ code structure"""
        structure = CodeStructure(
            file_path=file_path,
            language='cpp',
            imports=self._extract_cpp_includes(content),
            classes=self._extract_cpp_classes(content),
            functions=self._extract_cpp_functions(content),
            variables=self._extract_cpp_variables(content),
            constants=self._extract_cpp_constants(content),
            docstrings=self._extract_cpp_docstrings(content),
            comments=self._extract_cpp_comments(content),
            relationships=self._analyze_cpp_relationships(content),
            complexity_metrics=self._calculate_cpp_complexity(content)
        )
        
        return structure
    
    def _extract_cpp_includes(self, content: str) -> List[str]:
        """Extract include statements from C++ code"""
        includes = []
        
        # Match include statements
        include_pattern = r'#include\s*[<"]([^>"]+)[>"]'
        for match in re.finditer(include_pattern, content):
            includes.append(match.group(1))
        
        return includes
    
    def _extract_cpp_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract class definitions from C++ code"""
        classes = []
        
        # Match class declarations
        class_pattern = r'(?:public\s+|private\s+|protected\s+)?class\s+(\w+)(?:\s*:\s*[^{]+)?\s*\{'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            classes.append({
                'name': class_name,
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        return classes
    
    def _extract_cpp_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function definitions from C++ code"""
        functions = []
        
        # Match function declarations
        func_pattern = r'(?:\w+\s+)*(\w+)\s*\([^)]*\)(?:\s*const)?\s*\{'
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1)
            
            # Skip common keywords
            if func_name in ['class', 'struct', 'if', 'for', 'while', 'switch', 'try', 'catch']:
                continue
            
            functions.append({
                'name': func_name,
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        return functions
    
    def _extract_cpp_variables(self, content: str) -> List[Dict[str, Any]]:
        """Extract variable declarations from C++ code"""
        variables = []
        
        # Match variable declarations
        var_pattern = r'(?:const\s+)?(?:\w+(?:<[^>]+>)?\s+(?:\*\s*)?)(\w+)\s*(?:=|;)'
        for match in re.finditer(var_pattern, content):
            var_name = match.group(1)
            
            # Skip common keywords
            if var_name in ['class', 'struct', 'if', 'for', 'while', 'switch', 'try', 'catch']:
                continue
            
            variables.append({
                'name': var_name,
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        return variables
    
    def _extract_cpp_constants(self, content: str) -> List[Dict[str, Any]]:
        """Extract constant declarations from C++ code"""
        constants = []
        
        # Match const declarations
        const_pattern = r'const\s+(?:\w+(?:<[^>]+>)?\s+(?:\*\s*)?)(\w+)\s*(?:=|;)'
        for match in re.finditer(const_pattern, content):
            const_name = match.group(1)
            constants.append({
                'name': const_name,
                'line_number': content[:match.start()].count('\n') + 1
            })
        
        # Match #define statements
        define_pattern = r'#define\s+(\w+)\s+([^\\\n]+)'
        for match in re.finditer(define_pattern, content):
            const_name = match.group(1)
            constants.append({
                'name': const_name,
                'line_number': content[:match.start()].count('\n') + 1,
                'type': 'macro'
            })
        
        return constants
    
    def _extract_cpp_docstrings(self, content: str) -> List[Dict[str, Any]]:
        """Extract docstrings from C++ code"""
        docstrings = []
        
        # Match Doxygen comments
        doxygen_pattern = r'/\*\*\s*\n(.*?)\s*\*/'
        for match in re.finditer(doxygen_pattern, content, re.DOTALL):
            doc_content = match.group(1)
            # Clean up the docstring
            doc_lines = [line.strip().lstrip('*') for line in doc_content.split('\n')]
            cleaned_doc = '\n'.join(doc_lines).strip()
            
            docstrings.append({
                'content': cleaned_doc,
                'line_number': content[:match.start()].count('\n') + 1,
                'type': 'doxygen'
            })
        
        return docstrings
    
    def _extract_cpp_comments(self, content: str) -> List[Dict[str, Any]]:
        """Extract comments from C++ code"""
        comments = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                comments.append({
                    'content': stripped[2:].strip(),
                    'line_number': i,
                    'type': 'line_comment'
                })
        
        return comments
    
    def _analyze_cpp_relationships(self, content: str) -> Dict[str, List[str]]:
        """Analyze relationships between C++ code elements"""
        relationships = {
            'imports': self._extract_cpp_includes(content),
            'inheritance': [],
            'dependencies': []
        }
        
        # Extract inheritance relationships
        inheritance_pattern = r'class\s+(\w+)\s*:\s*[^{]*public\s+(\w+)'
        for match in re.finditer(inheritance_pattern, content):
            child_class = match.group(1)
            parent_class = match.group(2)
            relationships['inheritance'].append(f"{child_class} -> {parent_class}")
        
        return relationships
    
    def _calculate_cpp_complexity(self, content: str) -> Dict[str, Any]:
        """Calculate complexity metrics for C++ code"""
        lines = content.split('\n')
        
        metrics = {
            'lines_of_code': len([line for line in lines if line.strip() and not line.strip().startswith('//')]),
            'functions': len(self._extract_cpp_functions(content)),
            'classes': len(self._extract_cpp_classes(content)),
            'complexity_score': 0
        }
        
        # Simple complexity calculation based on control structures
        control_patterns = [
            r'\bif\b',
            r'\bfor\b',
            r'\bwhile\b',
            r'\bswitch\b',
            r'\btry\b',
            r'\bcatch\b'
        ]
        
        complexity = 0
        for pattern in control_patterns:
            complexity += len(re.findall(pattern, content))
        
        metrics['complexity_score'] = complexity
        
        return metrics
    
    def _analyze_c(self, file_path: str, content: str) -> CodeStructure:
        """Analyze C code structure"""
        # For now, use C++ analysis with C-specific adjustments
        structure = self._analyze_cpp(file_path, content)
        structure.language = 'c'
        
        return structure
    
    def generate_documentation(self, request: DocumentationRequest) -> DocumentationResult:
        """
        Generate documentation based on the provided request.
        
        Args:
            request: DocumentationRequest with generation parameters
            
        Returns:
            DocumentationResult with generated content and metadata
        """
        import time
        start_time = time.time()
        
        self.logger.info(f"Generating {request.documentation_type} documentation for {len(request.file_paths)} files")
        
        # Initialize AI processor if not already done
        if not self.ai_processor:
            self._initialize_ai_processor()
        
        # Analyze code structure
        structures = self.analyze_code_structure(request.file_paths)
        
        # Prepare codebase content for AI
        codebase_content = self._prepare_codebase_content(structures)
        
        # Select appropriate template
        template = self._select_template(request)
        
        # Generate documentation using AI
        if self.ai_processor:
            documentation_content = self._generate_with_ai(
                codebase_content, 
                request, 
                template
            )
        else:
            # Fallback to template-based generation
            documentation_content = self._generate_with_template(
                structures, 
                request, 
                template
            )
        
        # Generate diagrams if requested
        diagrams = []
        if request.include_diagrams:
            diagrams = self._generate_diagrams(structures)
        
        # Generate examples if requested
        examples = []
        if request.include_examples:
            examples = self._generate_examples(structures)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create result
        result = DocumentationResult(
            content=documentation_content,
            metadata={
                'file_count': len(request.file_paths),
                'documentation_type': request.documentation_type,
                'output_format': request.output_format,
                'template': request.template,
                'languages': list(set(s.language for s in structures)),
                'total_functions': sum(len(s.functions) for s in structures),
                'total_classes': sum(len(s.classes) for s in structures),
            },
            diagrams=diagrams,
            examples=examples,
            processing_time=processing_time
        )
        
        self.logger.info(f"Documentation generation completed in {processing_time:.2f}s")
        
        return result
    
    def _prepare_codebase_content(self, structures: List[CodeStructure]) -> str:
        """Prepare codebase content for AI processing"""
        content_parts = []
        
        for structure in structures:
            content_parts.append(f"## File: {structure.file_path}")
            content_parts.append(f"**Language:** {structure.language}")
            
            if structure.classes:
                content_parts.append("\n### Classes:")
                for cls in structure.classes:
                    content_parts.append(f"- **{cls['name']}** (line {cls.get('line_number', 'N/A')})")
                    if cls.get('docstring'):
                        content_parts.append(f"  - {cls['docstring'][:100]}...")
            
            if structure.functions:
                content_parts.append("\n### Functions:")
                for func in structure.functions:
                    content_parts.append(f"- **{func['name']}** (line {func.get('line_number', 'N/A')})")
                    if func.get('docstring'):
                        content_parts.append(f"  - {func['docstring'][:100]}...")
            
            if structure.imports:
                content_parts.append("\n### Imports:")
                for imp in structure.imports[:10]:  # Limit to first 10 imports
                    content_parts.append(f"- {imp}")
                if len(structure.imports) > 10:
                    content_parts.append(f"- ... and {len(structure.imports) - 10} more imports")
            
            content_parts.append("\n" + "-" * 50 + "\n")
        
        return "\n".join(content_parts)
    
    def _select_template(self, request: DocumentationRequest) -> str:
        """Select appropriate template based on request parameters"""
        if request.template and request.template in self.templates:
            return request.template
        
        # Select template based on documentation type
        template_map = {
            'api': 'api_documentation',
            'readme': 'readme_template',
            'architecture': 'architecture_template',
            'examples': 'examples_template',
            'all': 'comprehensive_template'
        }
        
        return template_map.get(request.documentation_type, 'default_template')
    
    def _generate_with_ai(self, codebase_content: str, request: DocumentationRequest, template: str) -> str:
        """Generate documentation using AI processor"""
        try:
            # Load documentation agent prompt
            agent_prompt = self._load_agent_prompt()
            
            # Format prompt with template and request parameters
            formatted_prompt = self._format_agent_prompt(agent_prompt, codebase_content, request, template)
            
            # Process with AI
            from app.core.config import settings
            response = self.ai_processor.process_question(
                question=formatted_prompt,
                conversation_history=[],
                codebase_content="",
                model=settings.default_model,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating documentation with AI: {e}")
            # Fallback to template-based generation
            return self._generate_with_template([], request, template)
    
    def _load_agent_prompt(self) -> str:
        """Load documentation generator agent prompt"""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__), 
                "../../../prompts/coding/agent/documentation-generator.md"
            )
            
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                self.logger.warning(f"Documentation agent prompt not found at {prompt_path}")
                return self._get_default_agent_prompt()
                
        except Exception as e:
            self.logger.error(f"Error loading agent prompt: {e}")
            return self._get_default_agent_prompt()
    
    def _get_default_agent_prompt(self) -> str:
        """Get default agent prompt if file not found"""
        return """
        You are a technical documentation specialist. Generate comprehensive documentation 
        for the provided codebase, including API documentation, usage examples, and 
        architectural explanations. Use clear, professional language and proper formatting.
        """
    
    def _format_agent_prompt(self, agent_prompt: str, codebase_content: str, request: DocumentationRequest, template: str) -> str:
        """Format agent prompt with request parameters"""
        # Replace placeholders in agent prompt
        formatted_prompt = agent_prompt.replace("{codebase_content}", codebase_content)
        formatted_prompt = formatted_prompt.replace("{documentation_type}", request.documentation_type)
        formatted_prompt = formatted_prompt.replace("{output_format}", request.output_format)
        formatted_prompt = formatted_prompt.replace("{target_audience}", request.target_audience)
        
        # Add template-specific instructions
        if template in self.templates:
            template_instructions = self.templates[template].get('instructions', '')
            formatted_prompt = formatted_prompt.replace("{template_instructions}", template_instructions)
        
        return formatted_prompt
    
    def _generate_with_template(self, structures: List[CodeStructure], request: DocumentationRequest, template: str) -> str:
        """Generate documentation using templates (fallback method)"""
        if template not in self.templates:
            template = 'default_template'
        
        template_content = self.templates[template].get('content', '')
        
        # Replace template placeholders
        documentation = template_content.replace("{project_name}", "Generated Documentation")
        documentation = documentation.replace("{documentation_type}", request.documentation_type)
        documentation = documentation.replace("{generation_date}", datetime.now().strftime("%Y-%m-%d"))
        
        # Add basic structure information
        if structures:
            languages = list(set(s.language for s in structures))
            documentation = documentation.replace("{languages}", ", ".join(languages))
            
            total_functions = sum(len(s.functions) for s in structures)
            total_classes = sum(len(s.classes) for s in structures)
            documentation = documentation.replace("{total_functions}", str(total_functions))
            documentation = documentation.replace("{total_classes}", str(total_classes))
        else:
            documentation = documentation.replace("{languages}", "Unknown")
            documentation = documentation.replace("{total_functions}", "0")
            documentation = documentation.replace("{total_classes}", "0")
        
        return documentation
    
    def _generate_diagrams(self, structures: List[CodeStructure]) -> List[Dict[str, Any]]:
        """Generate architecture diagrams from code structure"""
        diagrams = []
        
        # Generate dependency diagram
        dependency_diagram = self._generate_dependency_diagram(structures)
        if dependency_diagram:
            diagrams.append(dependency_diagram)
        
        # Generate class diagram if there are classes
        if any(s.classes for s in structures):
            class_diagram = self._generate_class_diagram(structures)
            if class_diagram:
                diagrams.append(class_diagram)
        
        return diagrams
    
    def _generate_dependency_diagram(self, structures: List[CodeStructure]) -> Optional[Dict[str, Any]]:
        """Generate Mermaid dependency diagram"""
        try:
            mermaid_code = ["graph TD"]
            added_nodes = set()
            
            for structure in structures:
                file_node = structure.file_path.replace('/', '_').replace('.', '_')
                if file_node not in added_nodes:
                    mermaid_code.append(f"    {file_node}[{structure.file_path}]")
                    added_nodes.add(file_node)
                
                # Add import relationships
                for imp in structure.imports[:10]:  # Limit to first 10 imports
                    imp_node = imp.replace('/', '_').replace('.', '_').replace('-', '_')
                    if imp_node not in added_nodes:
                        mermaid_code.append(f"    {imp_node}[{imp}]")
                        added_nodes.add(imp_node)
                    
                    mermaid_code.append(f"    {file_node} --> {imp_node}")
            
            if len(mermaid_code) > 1:  # More than just the graph TD line
                return {
                    'type': 'dependency_diagram',
                    'format': 'mermaid',
                    'code': '\n'.join(mermaid_code),
                    'title': 'Dependency Diagram'
                }
            
        except Exception as e:
            self.logger.error(f"Error generating dependency diagram: {e}")
        
        return None
    
    def _generate_class_diagram(self, structures: List[CodeStructure]) -> Optional[Dict[str, Any]]:
        """Generate Mermaid class diagram"""
        try:
            mermaid_code = ["classDiagram"]
            
            for structure in structures:
                for cls in structure.classes:
                    class_name = cls['name']
                    
                    # Add class definition
                    mermaid_code.append(f"    class {class_name} {{")
                    
                    # Add methods
                    for method in cls.get('methods', []):
                        method_name = method['name']
                        if method.get('is_async'):
                            method_name = f"async {method_name}"
                        mermaid_code.append(f"        +{method_name}()")
                    
                    # Add attributes
                    for attr in cls.get('attributes', []):
                        attr_name = attr['name']
                        mermaid_code.append(f"        -{attr_name}")
                    
                    mermaid_code.append("    }")
                    
                    # Add inheritance relationships
                    for base in cls.get('base_classes', []):
                        mermaid_code.append(f"    {base} <|-- {class_name}")
            
            if len(mermaid_code) > 1:  # More than just the classDiagram line
                return {
                    'type': 'class_diagram',
                    'format': 'mermaid',
                    'code': '\n'.join(mermaid_code),
                    'title': 'Class Diagram'
                }
            
        except Exception as e:
            self.logger.error(f"Error generating class diagram: {e}")
        
        return None
    
    def _generate_examples(self, structures: List[CodeStructure]) -> List[Dict[str, Any]]:
        """Generate usage examples from code structure"""
        examples = []
        
        for structure in structures:
            if structure.language == 'python':
                python_examples = self._generate_python_examples(structure)
                examples.extend(python_examples)
            elif structure.language in ['javascript', 'typescript']:
                js_examples = self._generate_js_examples(structure)
                examples.extend(js_examples)
        
        return examples
    
    def _generate_python_examples(self, structure: CodeStructure) -> List[Dict[str, Any]]:
        """Generate Python usage examples"""
        examples = []
        
        for cls in structure.classes:
            if cls['methods']:
                # Create class instantiation example
                example_code = f"# Example: Using {cls['name']}\n"
                example_code += f"{cls['name']} = {cls['name']}()\n"
                
                # Add method call examples
                for method in cls['methods'][:3]:  # Limit to first 3 methods
                    if not method['name'].startswith('_'):  # Skip private methods
                        example_code += f"result = {cls['name']}.{method['name']}()\n"
                
                examples.append({
                    'language': 'python',
                    'title': f"Using {cls['name']}",
                    'code': example_code,
                    'description': f"Basic usage example for the {cls['name']} class"
                })
        
        for func in structure.functions:
            if not func['name'].startswith('_'):  # Skip private functions
                # Create function call example
                example_code = f"# Example: Calling {func['name']}\n"
                
                # Add parameters if available
                args = func.get('args', [])
                if args:
                    example_code += f"result = {func['name']}({', '.join(args[:3])})\n"
                else:
                    example_code += f"result = {func['name']}()\n"
                
                examples.append({
                    'language': 'python',
                    'title': f"Calling {func['name']}",
                    'code': example_code,
                    'description': f"Example usage of the {func['name']} function"
                })
        
        return examples
    
    def _generate_js_examples(self, structure: CodeStructure) -> List[Dict[str, Any]]:
        """Generate JavaScript/TypeScript usage examples"""
        examples = []
        
        for cls in structure.classes:
            if cls['methods']:
                # Create class instantiation example
                example_code = f"// Example: Using {cls['name']}\n"
                example_code += f"const instance = new {cls['name']}();\n"
                
                # Add method call examples
                for method in cls['methods'][:3]:  # Limit to first 3 methods
                    if not method['name'].startswith('_'):  # Skip private methods
                        example_code += f"const result = instance.{method['name']}();\n"
                
                examples.append({
                    'language': structure.language,
                    'title': f"Using {cls['name']}",
                    'code': example_code,
                    'description': f"Basic usage example for the {cls['name']} class"
                })
        
        for func in structure.functions:
            if not func['name'].startswith('_'):  # Skip private functions
                # Create function call example
                example_code = f"// Example: Calling {func['name']}\n"
                
                # Add parameters if available
                args = func.get('args', [])
                if args:
                    example_code += f"const result = {func['name']}({', '.join(args[:3])});\n"
                else:
                    example_code += f"const result = {func['name']}();\n"
                
                examples.append({
                    'language': structure.language,
                    'title': f"Calling {func['name']}",
                    'code': example_code,
                    'description': f"Example usage of the {func['name']} function"
                })
        
        return examples
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load documentation templates"""
        templates = {}
        
        # Default template directory
        template_dir = os.path.join(
            os.path.dirname(__file__), 
            "../../templates/documentation"
        )
        
        # If template directory doesn't exist, use embedded templates
        if not os.path.exists(template_dir):
            return self._get_embedded_templates()
        
        try:
            for template_file in os.listdir(template_dir):
                if template_file.endswith('.md'):
                    template_name = template_file[:-3]  # Remove .md extension
                    template_path = os.path.join(template_dir, template_file)
                    
                    with open(template_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract metadata from template
                    metadata = {}
                    if content.startswith('---'):
                        end_metadata = content.find('---', 3)
                        if end_metadata != -1:
                            metadata_content = content[3:end_metadata]
                            try:
                                import yaml
                                metadata = yaml.safe_load(metadata_content) or {}
                            except yaml.YAMLError:
                                pass
                            
                            content = content[end_metadata + 3:]
                    
                    templates[template_name] = {
                        'content': content,
                        'metadata': metadata,
                        'instructions': metadata.get('instructions', '')
                    }
            
        except Exception as e:
            self.logger.error(f"Error loading templates: {e}")
            return self._get_embedded_templates()
        
        return templates
    
    def _get_embedded_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get embedded templates as fallback"""
        return {
            'default_template': {
                'content': """
# {project_name} Documentation

Generated on {generation_date}

## Overview

This document provides documentation for the codebase.

## Code Structure

- **Languages**: {languages}
- **Total Functions**: {total_functions}
- **Total Classes**: {total_classes}

## API Documentation

Detailed API documentation will be generated here.

## Usage Examples

Usage examples will be provided here.
                """,
                'metadata': {},
                'instructions': 'Generate basic documentation with structure overview.'
            },
            'api_documentation': {
                'content': """
# API Documentation

## Overview

This document provides comprehensive API documentation for the project.

## Endpoints

API endpoints will be documented here.

## Data Models

Data models and their properties will be documented here.

## Error Handling

Error codes and handling will be documented here.
                """,
                'metadata': {},
                'instructions': 'Generate comprehensive API documentation with endpoints and data models.'
            },
            'readme_template': {
                'content': """
# {project_name}

## Description

Project description goes here.

## Installation

Installation instructions go here.

## Usage

Usage instructions go here.

## Contributing

Contributing guidelines go here.

## License

License information goes here.
                """,
                'metadata': {},
                'instructions': 'Generate a comprehensive README file with installation and usage instructions.'
            },
            'architecture_template': {
                'content': """
# Architecture Documentation

## Overview

This document describes the system architecture.

## Components

System components will be documented here.

## Data Flow

Data flow diagrams will be included here.

## Dependencies

System dependencies will be documented here.
                """,
                'metadata': {},
                'instructions': 'Generate architecture documentation with component diagrams and data flow.'
            },
            'examples_template': {
                'content': """
# Usage Examples

## Basic Usage

Basic usage examples will be provided here.

## Advanced Usage

Advanced usage examples will be provided here.

## Common Patterns

Common usage patterns will be documented here.
                """,
                'metadata': {},
                'instructions': 'Generate practical usage examples for the codebase.'
            },
            'comprehensive_template': {
                'content': """
# Comprehensive Documentation

## Overview

This document provides comprehensive documentation for the project.

## API Documentation

API documentation will be included here.

## Architecture

Architecture documentation will be included here.

## Usage Examples

Usage examples will be provided here.

## Contributing

Contributing guidelines will be included here.
                """,
                'metadata': {},
                'instructions': 'Generate comprehensive documentation covering all aspects of the project.'
            }
        }


    def generate_documentation_with_guid(self, request: DocumentationRequest) -> DocumentationResult:
        """
        Generate documentation with GUID-based file naming.
        
        Args:
            request: DocumentationRequest with generation parameters
            
        Returns:
            DocumentationResult with GUID-prefixed content and metadata
        """
        # Generate GUID for this documentation session
        session_guid = str(uuid.uuid4())[:8]  # Use first 8 characters for brevity
        
        # Generate documentation
        result = self.generate_documentation(request)
        
        # Add GUID to metadata
        result.metadata['session_guid'] = session_guid
        result.metadata['guid_prefixed_files'] = {}
        
        self.cache[session_guid] = ([result], request.file_paths)
        
        return result
    
    def create_file_listing(self, file_paths: List[str], session_guid: str) -> Dict[str, Any]:
        """
        Create a comprehensive file listing with date and size metadata.
        
        Args:
            file_paths: List of file paths to analyze
            session_guid: GUID for the current session
            
        Returns:
            Dictionary containing file listing metadata
        """
        file_listing = {
            'session_guid': session_guid,
            'generated_at': datetime.utcnow().isoformat(),
            'total_files': len(file_paths),
            'files': []
        }
        
        total_size = 0
        for file_path in file_paths:
            try:
                file_stat = os.stat(file_path)
                file_info = {
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'size': file_stat.st_size,
                    'modified_date': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    'created_date': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                    'extension': os.path.splitext(file_path)[1]
                }
                file_listing['files'].append(file_info)
                total_size += file_stat.st_size
            except Exception as e:
                self.logger.error(f"Error getting file info for {file_path}: {e}")
                file_listing['files'].append({
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'size': 0,
                    'error': str(e),
                    'extension': os.path.splitext(file_path)[1]
                })
        
        file_listing['total_size'] = total_size
        return file_listing
    
    def create_documentation_zip(self,
                               documentation_results: List[DocumentationResult],
                               file_paths: List[str],
                               session_guid: str,
                               include_source_files: bool = True) -> bytes:
        """
        Create a zip file containing all documentation output and optionally source files.
        
        Args:
            documentation_results: List of documentation results to include
            file_paths: List of source file paths
            session_guid: GUID for the current session
            include_source_files: Whether to include original source files
            
        Returns:
            Zip file as bytes
        """
        self.logger.info(f"Creating documentation zip for session {session_guid}")
        
        # Create temporary file for zip
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            zip_path = temp_file.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add documentation files with GUID prefix
                for result in documentation_results:
                    doc_type = result.metadata.get('documentation_type', 'documentation')
                    guid_filename = f"{session_guid}-{doc_type}.md"
                    zipf.writestr(guid_filename, result.content)
                    
                    # Add metadata as JSON
                    metadata_filename = f"{session_guid}-{doc_type}.metadata.json"
                    metadata_content = json.dumps({
                        'metadata': result.metadata,
                        'generated_at': result.generated_at.isoformat(),
                        'processing_time': result.processing_time,
                        'token_usage': result.token_usage
                    }, indent=2)
                    zipf.writestr(metadata_filename, metadata_content)
                
                # Add file listing
                file_listing = self.create_file_listing(file_paths, session_guid)
                listing_filename = f"{session_guid}-file-listing.json"
                zipf.writestr(listing_filename, json.dumps(file_listing, indent=2))
                
                # Add source files if requested
                if include_source_files:
                    for file_path in file_paths:
                        try:
                            if os.path.exists(file_path) and os.path.isfile(file_path):
                                # Create GUID-prefixed filename
                                original_name = os.path.basename(file_path)
                                guid_filename = f"{session_guid}-source-{original_name}"
                                zipf.write(file_path, guid_filename)
                        except Exception as e:
                            self.logger.error(f"Error adding file {file_path} to zip: {e}")
                
                # Add README with session information
                readme_content = f"""# Documentation Package

Generated: {datetime.utcnow().isoformat()}
Session GUID: {session_guid}
Total Files: {len(file_paths)}

## Contents

### Documentation Files
"""
                for result in documentation_results:
                    doc_type = result.metadata.get('documentation_type', 'documentation')
                    readme_content += f"- {session_guid}-{doc_type}.md\n"
                    readme_content += f"- {session_guid}-{doc_type}.metadata.json\n"
                
                readme_content += f"""
### File Information
- {session_guid}-file-listing.json

"""
                if include_source_files:
                    readme_content += "### Source Files\n"
                    for file_path in file_paths:
                        original_name = os.path.basename(file_path)
                        readme_content += f"- {session_guid}-source-{original_name}\n"
                
                zipf.writestr(f"{session_guid}-README.md", readme_content)
            
            # Read zip file as bytes
            with open(zip_path, 'rb') as f:
                zip_bytes = f.read()
            
            self.logger.info(f"Successfully created documentation zip ({len(zip_bytes)} bytes)")
            return zip_bytes
            
        except Exception as e:
            self.logger.error(f"Error creating documentation zip: {e}")
            raise
        finally:
            # Clean up temporary file
            try:
                os.unlink(zip_path)
            except:
                pass


# Singleton instance
documentation_service = DocumentationService()