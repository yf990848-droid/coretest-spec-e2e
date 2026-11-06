"""CLI boundary for existing TS/TC plans; never edits design inputs or archive state."""
import argparse
import json
from pathlib import Path
import subprocess


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(path)


def positive(value):
    if isinstance(value, bool) or not str(value).isdigit() or int(value) <= 0:
        raise ValueError('expected a positive platform ID')
    return str(value)


def required(value, key):
    if value is None or str(value).strip() == '' or '<TODO:' in str(value):
        raise ValueError('missing ' + key)
    return str(value)


def csv(value):
    if value is None:
        return ''
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return ','.join(value)
    if isinstance(value, str):
        return value
    raise ValueError('relation selections must be names/IDs as a string or string list')


def ts_flags(source, design_task_id, tr_id, creator):
    flags = ['--design-task-id', positive(design_task_id), '--tr-id', positive(tr_id),
             '--name', required(source.get('tsName') or source.get('ts_name'), 'ts_name'),
             '--type', required(source.get('tsType') or source.get('ts_type'), 'ts_type'),
             '--creator', required(creator, 'creator')]
    for keys, flag in [
        (('description',), 'description'),
        (('resolveDescription', 'resolve_description'), 'resolve-description'),
        (('sceneSelecteds',), 'scene-names'), (('functionSelecteds',), 'function-names'),
        (('featureSelecteds',), 'feature-names'), (('requirement_ids',), 'requirement-ids')]:
        value = next((source[k] for k in keys if k in source), '')
        value = csv(value)
        if value:
            flags += ['--' + flag, value]
    return flags


def tc_flags(source, tp_id, pbi, creator):
    for key in ('action_factor_names', 'data_factor_names', 'actionFactorInfo',
                'dataFactorInfo', 'action_factor_info', 'data_factor_info'):
        if source.get(key):
            raise ValueError('TC factor association requires CLI support for exact case_id + factors; unsupported field: ' + key)
    flags = ['--tp-id', positive(tp_id), '--version-pbi', required(pbi, 'pbi'),
             '--name', required(source.get('name'), 'name'),
             '--case-id', required(source.get('case_id'), 'case_id'),
             '--creator', required(source.get('creator') or creator, 'creator'),
             '--owner', required(source.get('owner') or creator, 'owner'),
             '--status', 'notArchived', '--case-id-type', source.get('case_id_type') or 'input_begin']
    mapping = {'auto_type': 'auto-type', 'rank': 'rank', 'description': 'description',
               'preparation': 'precondition', 'test_step': 'test-step',
               'expect_output': 'expected-output', 'post_process': 'post-process',
               'case_remark': 'case-remark', 'test_case_type': 'test-type',
               'test_case_activity': 'test-activity', 'apply_version': 'apply-version',
               'test_environment_id': 'test-env-id', 'test_environment_type': 'test-env-type',
               'execution_platform': 'execution-platform', 'test_case_author': 'test-case-author',
               'test_case_feature': 'test-case-feature', 'vbs_flag': 'vbs-flag',
               'threshold_flag': 'threshold-flag'}
    for key, flag in mapping.items():
        if key in source and source[key] is not None and source[key] != '':
            flags += ['--' + flag, str(source[key])]
    # Card columns (AutoType, TestType, envtype, DesignNote) are deliberately not remapped.
    return flags


class Runner:
    def __init__(self, cli, response_file):
        self.cli = Path(cli)
        if not self.cli.is_absolute() or not self.cli.is_file():
            raise ValueError('--cli must be an existing absolute executable path')
        self.path = Path(response_file).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.evidence = read(self.path) if self.path.exists() else {'calls': []}

    def call(self, args):
        command = [str(self.cli), 'coretest', 'testdesign'] + args + ['-o', 'json']
        entry = {'command': command}
        self.evidence['calls'].append(entry)
        save(self.path, self.evidence)
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=120)
            entry.update(exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
            save(self.path, self.evidence)
            if result.returncode:
                raise ValueError('CLI nonzero exit; inspect response evidence')
            data = json.loads(result.stdout)
            if not isinstance(data, dict) or data.get('success') is False:
                raise ValueError('CLI returned invalid/failed result')
            return data
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            entry['error'] = str(exc)
            save(self.path, self.evidence)
            raise

    def create(self, entity, flags):
        args = [entity, 'create-by-name' if entity == 'ts' else 'create'] + flags
        marker = self.path.with_suffix('.request.json')
        request = {'cli': str(self.cli), 'args': args}
        previous = marker.exists()
        if previous and read(marker) != request:
            raise ValueError('request changed; reconcile prior attempt before creating')
        if previous and self.evidence.get('success'):
            return self.evidence['id']
        if entity == 'tc':
            tp = flags[flags.index('--tp-id') + 1]
            case_id = flags[flags.index('--case-id') + 1]
            found = self.find_tc(tp, case_id, flags)
            if found:
                if not previous:
                    raise ValueError('case_id already exists; reconcile archive state before reuse')
                return found
        if previous:
            raise ValueError('previous creation outcome unresolved; do not automatically recreate; reconcile platform/state and retain evidence')
        # Exclusive durable marker precedes the write. Timeout/crash never triggers a blind retry.
        with marker.open('x', encoding='utf-8') as f:
            json.dump(request, f, ensure_ascii=False, indent=2)
        result = self.call(args)
        if entity == 'ts':
            return positive(result.get('ts_id'))
        found = self.find_tc(tp, case_id, flags)
        if not found:
            raise ValueError('created TC not confirmed by list; do not recreate; reconcile platform/state')
        return found

    def find_tc(self, tp, case_id, flags):
        result = self.call(['tc', 'list', '--tp-id', tp])
        if not isinstance(result.get('items'), list):
            raise ValueError('tc list requires items[]')
        pagination = result.get('pagination', {})
        if int(pagination.get('total', len(result['items']))) > len(result['items']):
            raise ValueError('incomplete tc list; cannot verify absence safely')
        matches = [x for x in result['items'] if x.get('case_id') == case_id]
        if len(matches) > 1:
            raise ValueError('ambiguous duplicate case_id')
        if not matches:
            return None
        item = matches[0]
        for key, flag in [('name', '--name'), ('pbi', '--version-pbi'), ('owner', '--owner'),
                          ('rank', '--rank'), ('auto_type', '--auto-type'), ('status', '--status')]:
            if flag in flags and str(item.get(key)) != flags[flags.index(flag) + 1]:
                raise ValueError('TC readback mismatch: ' + key)
        return positive(item.get('id'))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('entity', choices=['ts', 'tc'])
    for key in ('cli', 'input-file', 'creator', 'response-file'):
        p.add_argument('--' + key, required=True)
    p.add_argument('--ts-index', type=int)
    p.add_argument('--design-task-id')
    p.add_argument('--tr-id')
    p.add_argument('--tc-id-temp')
    p.add_argument('--tp-id')
    p.add_argument('--pbi')
    a = p.parse_args()
    runner = None
    try:
        source = read(a.input_file)
        if a.entity == 'ts':
            if a.ts_index is None or a.ts_index < 0:
                raise ValueError('nonnegative --ts-index required (catalog.tr_ts_index)')
            source = source['test_specs'][a.ts_index]
            flags = ts_flags(source, a.design_task_id, a.tr_id, a.creator)
        else:
            matches = [x for x in source['tcs'] if x.get('tc_id_temp') == a.tc_id_temp]
            if not a.tc_id_temp or len(matches) != 1:
                raise ValueError('tc_id_temp must identify exactly one TC')
            flags = tc_flags(matches[0], a.tp_id, a.pbi, a.creator)
        runner = Runner(a.cli, a.response_file)
        platform_id = runner.create(a.entity, flags)
        runner.evidence.update(success=True, id=platform_id)
        save(runner.path, runner.evidence)
        print(json.dumps({'success': True, 'id': platform_id, 'response_file': str(runner.path)}, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, IndexError, TypeError, subprocess.SubprocessError) as exc:
        result = {'success': False, 'error': str(exc), 'response_file': str(Path(a.response_file).resolve())}
        if runner is not None:
            runner.evidence.update(success=False, error=str(exc))
            save(runner.path, runner.evidence)
        print(json.dumps(result, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
