#!/usr/bin/env python3
"""
Project Statistics Analyzer
Analyzes your Monster Hunter Game project and provides detailed statistics
Run this from your project root directory
"""

import os
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

class ProjectAnalyzer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root).resolve()
        self.stats = {
            'total_files': 0,
            'total_lines': 0,
            'by_extension': defaultdict(lambda: {'files': 0, 'lines': 0}),
            'by_directory': defaultdict(lambda: {'files': 0, 'lines': 0}),
            'file_sizes': [],
            'largest_files': [],
            'code_files': 0,
            'config_files': 0,
            'documentation_files': 0
        }
        
        # File extensions to analyze
        self.code_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript', 
            '.jsx': 'React JSX',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript JSX',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.html': 'HTML',
            '.json': 'JSON',
            '.sql': 'SQL',
            '.yml': 'YAML',
            '.yaml': 'YAML'
        }
        
        self.config_extensions = {
            '.json', '.yml', '.yaml', '.toml', '.ini', '.cfg', '.env'
        }
        
        self.doc_extensions = {
            '.md', '.txt', '.rst', '.doc', '.docx', '.pdf'
        }
        
        # Directories to skip
        self.skip_dirs = {
            '__pycache__', '.git', 'node_modules', '.vscode', '.idea', 
            'venv', 'env', '.env', 'build', 'dist', '.next', '.pytest_cache',
            'outputs'  # Skip AI generated outputs
        }
        
        # Files to skip
        self.skip_files = {
            '.DS_Store', 'Thumbs.db', '.gitignore', '.gitkeep'
        }

    def is_text_file(self, file_path):
        """Check if file is likely a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)  # Try to read first 1KB
            return True
        except (UnicodeDecodeError, PermissionError):
            return False

    def count_lines(self, file_path):
        """Count lines in a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for line in f)
        except:
            return 0

    def analyze_file(self, file_path):
        """Analyze a single file"""
        rel_path = file_path.relative_to(self.project_root)
        extension = file_path.suffix.lower()
        file_size = file_path.stat().st_size
        
        # Skip if in skip list
        if file_path.name in self.skip_files:
            return
            
        # Count lines for text files
        lines = 0
        if self.is_text_file(file_path):
            lines = self.count_lines(file_path)
        
        # Update statistics
        self.stats['total_files'] += 1
        self.stats['total_lines'] += lines
        self.stats['file_sizes'].append(file_size)
        
        # By extension
        ext_name = self.code_extensions.get(extension, extension or 'no extension')
        self.stats['by_extension'][ext_name]['files'] += 1
        self.stats['by_extension'][ext_name]['lines'] += lines
        
        # By directory (top level)
        top_dir = str(rel_path.parts[0]) if rel_path.parts else 'root'
        self.stats['by_directory'][top_dir]['files'] += 1
        self.stats['by_directory'][top_dir]['lines'] += lines
        
        # File categories
        if extension in self.code_extensions:
            self.stats['code_files'] += 1
        elif extension in self.config_extensions:
            self.stats['config_files'] += 1
        elif extension in self.doc_extensions:
            self.stats['documentation_files'] += 1
        
        # Track largest files
        self.stats['largest_files'].append({
            'path': str(rel_path),
            'lines': lines,
            'size_kb': round(file_size / 1024, 1)
        })

    def analyze_directory(self, dir_path):
        """Recursively analyze a directory"""
        try:
            for item in dir_path.iterdir():
                if item.is_file():
                    self.analyze_file(item)
                elif item.is_dir() and item.name not in self.skip_dirs:
                    self.analyze_directory(item)
        except PermissionError:
            pass  # Skip directories we can't read

    def run_analysis(self):
        """Run the complete analysis"""
        print("🔍 Analyzing Monster Hunter Game Project...")
        print(f"📁 Project Root: {self.project_root}")
        print("⏳ This may take a moment...\n")
        
        self.analyze_directory(self.project_root)
        
        # Sort largest files
        self.stats['largest_files'].sort(key=lambda x: x['lines'], reverse=True)
        self.stats['largest_files'] = self.stats['largest_files'][:10]  # Top 10
        
        return self.stats

    def print_results(self):
        """Print formatted results"""
        stats = self.stats
        
        print("=" * 60)
        print("📊 MONSTER HUNTER GAME PROJECT ANALYSIS")
        print("=" * 60)
        print()
        
        # Overview
        print("🏗️ PROJECT OVERVIEW:")
        print(f"  Total Files: {stats['total_files']:,}")
        print(f"  Total Lines of Code: {stats['total_lines']:,}")
        print(f"  Code Files: {stats['code_files']:,}")
        print(f"  Config Files: {stats['config_files']:,}")
        print(f"  Documentation Files: {stats['documentation_files']:,}")
        
        if stats['file_sizes']:
            avg_size = sum(stats['file_sizes']) / len(stats['file_sizes'])
            total_size_mb = sum(stats['file_sizes']) / (1024 * 1024)
            print(f"  Average File Size: {avg_size/1024:.1f} KB")
            print(f"  Total Project Size: {total_size_mb:.1f} MB")
        print()
        
        # By file type
        print("📝 BY FILE TYPE:")
        ext_sorted = sorted(stats['by_extension'].items(), 
                           key=lambda x: x[1]['lines'], reverse=True)
        for ext_name, data in ext_sorted:
            if data['files'] > 0:
                print(f"  {ext_name:12} {data['files']:3} files  {data['lines']:6,} lines")
        print()
        
        # By directory
        print("📁 BY DIRECTORY:")
        dir_sorted = sorted(stats['by_directory'].items(), 
                           key=lambda x: x[1]['lines'], reverse=True)
        for dir_name, data in dir_sorted:
            if data['files'] > 0:
                print(f"  {dir_name:12} {data['files']:3} files  {data['lines']:6,} lines")
        print()
        
        # Largest files
        print("📋 LARGEST FILES (by lines):")
        for i, file_info in enumerate(stats['largest_files'], 1):
            if file_info['lines'] > 0:
                print(f"  {i:2}. {file_info['path']:40} {file_info['lines']:4,} lines ({file_info['size_kb']} KB)")
        print()
        
        # Project complexity assessment
        print("💡 PROJECT COMPLEXITY ASSESSMENT:")
        total_lines = stats['total_lines']
        
        if total_lines < 1000:
            complexity = "🟢 Small project"
        elif total_lines < 5000:
            complexity = "🟡 Medium project"
        elif total_lines < 15000:
            complexity = "🟠 Large project"
        else:
            complexity = "🔴 Very large project"
            
        print(f"  {complexity}")
        print(f"  Estimated Development Time: {self.estimate_dev_time(total_lines)}")
        print(f"  Maintenance Complexity: {self.estimate_maintenance(stats)}")
        print()
        
        # Technology stack
        print("🔧 DETECTED TECHNOLOGY STACK:")
        tech_stack = self.detect_tech_stack(stats)
        for tech in tech_stack:
            print(f"  • {tech}")
        print()
        
        # Token estimation for Claude
        estimated_tokens = total_lines * 10  # Rough estimate: ~10 tokens per line
        context_percentage = (estimated_tokens / 200000) * 100  # Assuming 200k context
        
        print("🧠 CLAUDE CONTEXT ESTIMATION:")
        print(f"  Estimated Tokens: ~{estimated_tokens:,}")
        print(f"  Context Usage: ~{context_percentage:.1f}%")
        print()

    def estimate_dev_time(self, lines):
        """Estimate development time based on lines of code"""
        # Very rough estimate: 10-50 lines per day depending on complexity
        if lines < 1000:
            return "1-4 weeks"
        elif lines < 5000:
            return "2-4 months"
        elif lines < 15000:
            return "6-12 months"
        else:
            return "1+ years"

    def estimate_maintenance(self, stats):
        """Estimate maintenance complexity"""
        dirs = len(stats['by_directory'])
        types = len([x for x in stats['by_extension'] if stats['by_extension'][x]['files'] > 0])
        
        if dirs <= 3 and types <= 3:
            return "🟢 Low (simple structure)"
        elif dirs <= 8 and types <= 6:
            return "🟡 Medium (moderate complexity)"
        else:
            return "🔴 High (complex architecture)"

    def detect_tech_stack(self, stats):
        """Detect technology stack from file extensions"""
        stack = []
        extensions = stats['by_extension']
        
        if extensions.get('Python', {}).get('files', 0) > 0:
            stack.append("🐍 Python (Backend)")
        if extensions.get('JavaScript', {}).get('files', 0) > 0:
            stack.append("⚛️ JavaScript/React (Frontend)")
        if extensions.get('CSS', {}).get('files', 0) > 0:
            stack.append("🎨 CSS (Styling)")
        if extensions.get('JSON', {}).get('files', 0) > 0:
            stack.append("📋 JSON (Configuration)")
        if 'requirements.txt' in [f.name for f in self.project_root.glob('requirements.txt')]:
            stack.append("📦 pip (Python Dependencies)")
        if 'package.json' in [f.name for f in self.project_root.glob('package.json')]:
            stack.append("📦 npm (Node Dependencies)")
        
        return stack

    def save_detailed_report(self, filename="project_analysis.json"):
        """Save detailed analysis to JSON file"""
        report = {
            'analysis_date': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'summary': {
                'total_files': self.stats['total_files'],
                'total_lines': self.stats['total_lines'],
                'code_files': self.stats['code_files'],
                'config_files': self.stats['config_files']
            },
            'by_extension': dict(self.stats['by_extension']),
            'by_directory': dict(self.stats['by_directory']),
            'largest_files': self.stats['largest_files']
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Detailed report saved to: {filename}")

def main():
    """Main function"""
    analyzer = ProjectAnalyzer()
    analyzer.run_analysis()
    analyzer.print_results()
    
    # Ask if user wants detailed JSON report
    try:
        save_report = input("\n💾 Save detailed JSON report? (y/n): ").lower().strip()
        if save_report in ['y', 'yes']:
            analyzer.save_detailed_report()
    except KeyboardInterrupt:
        print("\n\n👋 Analysis complete!")

if __name__ == "__main__":
    main()