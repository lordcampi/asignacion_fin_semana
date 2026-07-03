from pathlib import Path

structure = {
    'src': {
        'main.py': '# Entry point\n',
        'config': {
            'settings.py': '# Configuration settings\n'
        },
        'domain': {
            'agent.py': '# Agent domain model\n',
            'assignment.py': '# Assignment domain model\n'
        },
        'services': {
            'input_manager.py': '# InputManager service\n',
            'rule_engine.py': '# RuleEngine service\n',
            'assignment_engine.py': '# AssignmentEngine service\n',
            'balance_engine.py': '# BalanceEngine service\n'
        },
        'output': {
            'formatter.py': '# OutputFormatter\n'
        },
        'tests': {
            'test_rules.py': '# Pytest tests for rules\n'
        }
    }
}

def create_structure(base_path: Path, tree: dict) -> None:
    for name, content in tree.items():
        path = base_path / name
        if isinstance(content, dict):
            path.mkdir(parents=True, exist_ok=True)
            (path / '__init__.py').touch(exist_ok=True)
            create_structure(path, content)
        else:
            path.write_text(content, encoding='utf-8')

if __name__ == '__main__':
    create_structure(Path.cwd(), structure)