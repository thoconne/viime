from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy.orm.session import make_transient

from .models import CSVFile, CSVFileSchema, db, GroupLevel, TableColumn, \
    TableRow, ValidatedMetaboliteTable, ValidatedMetaboliteTableSchema


def is_sample_file(csv: CSVFile) -> bool:
    return csv.sample_group is not None


def import_files(files: List[CSVFile]):
    new_ids = {str(c.id): uuid4() for c in files}

    todo = files.copy()

    while todo:
        csv = todo.pop(0)

        new_id = new_ids.get(str(csv.id))
        ori_id = csv.id
        table = csv.table

        # remove from session
        for sub in csv.columns + csv.rows + csv.group_levels:
            db.session.expunge(sub)
            make_transient(sub)
            sub.csv_file_id = new_id

        db.session.expunge(csv)
        make_transient(csv)

        # update releated things
        csv.id = new_id
        csv.created = datetime.utcnow()
        csv.meta = csv.meta.copy()
        csv.sample_group = None
        # extra option to mimic the _read_csv logic
        csv.save_table(table, index=False, header=False)

        if 'merged' in csv.meta:
            # ensure we also merge the others
            merged_ids: List[str] = csv.meta['merged']
            new_merged_ids: List[str] = []
            for file_id in merged_ids:
                if file_id not in new_ids:
                    extra: CSVFile = CSVFile.query.get(file_id)
                    if extra:
                        extra_new_id = uuid4()
                        new_ids[extra.id] = extra_new_id
                        todo.append(extra)
                        new_merged_ids.append(str(extra_new_id))
                else:
                    new_merged_ids.append(str(new_ids[file_id]))
            csv.meta['merged'] = new_merged_ids

        db.session.add(csv)
        for sub in csv.columns + csv.rows + csv.group_levels:
            db.session.add(sub)

        v: ValidatedMetaboliteTable = ValidatedMetaboliteTable.query \
            .filter_by(csv_file_id=ori_id).first()
        if not v:
            continue

        db.session.expunge(v)
        make_transient(v)

        v.id = uuid4()
        v.csv_file_id = csv.id
        v.created = csv.created
        v.meta = csv.meta.copy()
        db.session.add(v)

    return files


def dump_info(csv: CSVFile):
    return dict(name=csv.name, description=csv.description, id=csv.id)


def list_samples():
    groups: Dict[str, List[CSVFile]] = {}
    for csv in CSVFile.query.filter(CSVFile.sample_group.isnot(None)).all():
        groups.setdefault(csv.sample_group, []).append(csv)
    return [dict(name=k, files=[dump_info(csv) for csv in v]) for k, v in groups.items()]


_validation_keys = ['normalization', 'normalization_argument', 'scaling',
                    'imputation_info',
                    'scaling', 'transformation']


def dump(csv: CSVFile):
    out = CSVFileSchema(exclude=[
        'id',
        'created',
        'table_validation',
        'measurement_table',
        'size',
        'missing_cells'
    ]).dump(csv)

    v = ValidatedMetaboliteTable.query.filter_by(csv_file_id=csv.id).first_or_404()

    v_out = ValidatedMetaboliteTableSchema(
        only=_validation_keys).dump(v)

    if csv.sample_group:
        out['sample_group'] = csv.sample_group
    out.update(v_out)

    return out


def upload(json: Dict[str, Any]):
    # extract validated table specific keys
    validated: Dict[str, Any] = {}
    for key in _validation_keys:
        if key in json:
            validated[key] = json.pop(key)

    # remove not auto imported things
    columns: List[Any] = json.pop('columns', [])
    rows: List[Any] = json.pop('rows', [])
    group_levels: List[Any] = json.pop('group_levels', [])
    sample_group = json.pop('sample_group', None)
    selected_columns = json.pop('selected_columns', [])
    if not json.get('description'):
        json['description'] = ''

    csv = CSVFileSchema().load(json)

    # update types afterwards since the default is auto generated

    def update(acts, templates, model):
        if not templates:
            return
        for act, template in zip(acts, templates):
            for col in model.__table__.columns.keys():
                if col in template:
                    setattr(act, col, template[col])
            db.session.add(act)

    update(csv.columns, columns, TableColumn)
    update(csv.rows, rows, TableRow)

    if group_levels:
        csv.group_levels = [GroupLevel(**g) for g in group_levels]
    csv.sample_group = sample_group
    csv.selected_columns = selected_columns

    db.session.add(csv)
    db.session.flush()

    validated_table = ValidatedMetaboliteTable.create_from_csv_file(csv, **validated)
    db.session.add(validated_table)

    return dump(csv)


def enable_sample(csv: CSVFile, group: Optional[str] = 'Default'):
    csv.sample_group = group or 'Default'
    return csv


def disable_sample(csv: CSVFile, group: Optional[str] = 'Default'):
    csv.sample_group = None
    return csv
