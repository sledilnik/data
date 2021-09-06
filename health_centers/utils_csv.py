#!/usr/bin/env python

import collections
import csv
import datetime
import logging
import typing

import health_centers.dataclass
import health_centers.utils


logger = logging.getLogger(__file__.split('/')[-1])


@health_centers.utils.timeit
def write_csv(health_centers_csv: str, entities: typing.List[health_centers.dataclass.Entity]):
    logger.info('Writing CSV...')

    aggregates = collections.defaultdict(lambda: health_centers.dataclass.Numbers(0, 0, 0, 0, 0, 0, 0))
    for entity in entities:
        for key in health_centers.dataclass.Numbers.__annotations__.keys():
            aggregates[entity.date].__dict__[key] += entity.numbers.__dict__[key] or 0  # handle Null

    entity_mapping = collections.defaultdict(lambda: [])
    for entity in entities:
        entity_mapping[(entity.name_key, entity.date)].append(entity)

    def get_entity(name_key: str, date: datetime):
        found_entities = entity_mapping[(name_key, date)]

        if len(found_entities) == 0:
            logger.debug(f'No data found for {name_key} {date}')
            return None

        if len(found_entities) > 1:

            # it might happen that numbers come from diffent files, but if they are the same that's okay
            if len(set([e.numbers for e in found_entities])) == 1:
                return found_entities[0]

            # if numbers are not the same, then we take the maximum over all properties (not sum)
            # this is not ideal scenario though, and should maybe be removed in the future
            props = set([  # this definition is here so that we are sure maximums make sense for all the fields
                'examinations___medical_emergency', 'examinations___suspected_covid',
                'phone_triage___suspected_covid', 'tests___performed', 'tests___positive', 'sent_to___hospital',
                'sent_to___self_isolation'
            ])
            maxs = {p: 0 for p in props}
            for e in found_entities:
                assert e.numbers.__annotations__.keys() == props
                for a in props:
                    if (e.numbers.get(a) or -1) > maxs[a]:  # property can be None, therefore; or 0
                        maxs[a] = e.numbers.get(a)
            for e in found_entities:
                for prop in props:
                    if e.numbers.get(prop) == maxs[prop]:
                        return e

            # code unreachable (for now)
            for found_entity in found_entities:
                logger.error(found_entity)
            raise Exception(f'Too many entities found: {len(found_entities)}, {name_key}, {date}')
        return found_entities[0]

    with open(health_centers_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, dialect='excel', lineterminator='\n')

        def get_formatted_numbers_fields():
            return[field.replace('___', '.') for field in health_centers.dataclass.Numbers.__annotations__.keys()]

        columns = ['date']
        # scope: aggregates
        for field in get_formatted_numbers_fields():
            columns.append(f'hc.{field}')
        # scope: health centers
        for name in health_centers.mappings.unique_short_names:
            region = health_centers.mappings.region[name]
            for field in get_formatted_numbers_fields():
                columns.append(f'hc.{region}.{name}.{field}')
        writer.writerow(columns)

        # write data
        dates = sorted(list(set([entity.date for entity in entities])))
        for date in dates:

            columns = [date]
            # scope: aggregates
            for key in aggregates[date].__annotations__.keys():
                columns.append(aggregates[date].__dict__[key])
            # scope: health centers
            for name in health_centers.mappings.unique_short_names:
                entity = get_entity(name_key=name, date=date)
                for field in health_centers.dataclass.Numbers.__annotations__.keys():
                    if entity is None:
                        columns.append(None)
                    else:
                        columns.append(getattr(entity.numbers, field))
            writer.writerow(columns)
