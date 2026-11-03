"""Fetch one CLI task-tree snapshot and adapt only the initialization boundary."""
import argparse
import copy
import json
from pathlib import Path
import subprocess


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(path)


def adapt(raw):
    if not isinstance(raw, dict) or raw.get('success') is False:
        raise ValueError('task tree failed')
    if not raw.get('pbi') or not raw.get('project_id') or not isinstance(raw.get('tasks'), list):
        raise ValueError('task tree requires pbi, project_id, tasks[]')
    data = copy.deepcopy(raw['tasks'])
    def rename(item, names):
        for old, new in names.items():
            if old in item:
                item[new] = item.pop(old)
    for task in data:
        if not isinstance(task, dict) or not task.get('design_task_id'):
            raise ValueError('invalid design task')
        for ir in task.get('ir_list', []):
            rename(ir, {'requirement_alm_id': 'requirementAlmId', 'asso_act_type': 'assoActType'})
            for sr in ir.get('sr_list', []):
                rename(sr, {'requirement_parent_id': 'requirementParentId', 'asso_act_type': 'assoActType'})
        for key in ('feature_list', 'function_list'):
            for item in task.get(key, []):
                rename(item, {'asso_act_type': 'assoActType'})
        # TR ir_list uses requirement_alm_id in the existing context contract.
    return {'success': True, 'pbi': int(raw['pbi']), 'project_id': raw['project_id'], 'data': data}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cli', required=True)
    p.add_argument('--product-name', required=True)
    p.add_argument('--owner-id', required=True)
    p.add_argument('--output-root', required=True)
    a = p.parse_args()
    try:
        cli = Path(a.cli)
        if not cli.is_absolute() or not cli.is_file():
            raise ValueError('--cli must be an existing absolute executable path')
        root = Path(a.output_root)
        command = [str(cli), 'coretest', 'testdesign', 'task', 'tree', '--product-name',
                   a.product_name, '--owner-id', a.owner_id, '-o', 'json']
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=120)
        save(root / 'design_task_info.cli_response.json', {
            'command': command, 'exit_code': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr})
        if result.returncode:
            raise ValueError('task tree failed; see design_task_info.cli_response.json')
        normalized = adapt(json.loads(result.stdout))
        save(root / 'design_task_info.json', normalized)
        print(json.dumps({'success': True, 'file': str(root / 'design_task_info.json')}, ensure_ascii=False))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({'success': False, 'error': str(exc)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
