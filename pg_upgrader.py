import argparse
import json
from threading import Thread
import time

import boto3


class RDSPostgresUpgrader():
    client = boto3.client('rds')

    def __init__(self, pg_engine_versions, ids=None, tags=None):
        self.pg_engine_versions = pg_engine_versions
        self.db_instance_ids = ids
        if tags is not None:
            self.db_instance_tags = tags
            self._set_db_instance_ids_from_tags()

    def _uses_postgres(self, db_instance_id):
        db_engine = self.client.describe_db_instances(
            DBInstanceIdentifier=db_instance_id
        )["DBInstances"][0]["Engine"]
        uses_postgres = db_engine == "postgres"
        if not uses_postgres:
            print(
                "Excluding DB instance: {} as it does not use postgres."
                " DB Engine: '{}' was reported"
                .format(db_instance_id, db_engine)
            )
        return uses_postgres

    def _modify_db(self, db_instance_id):
            for pg_engine_version in self.pg_engine_versions:
                print("Waiting for {} to become available"
                      .format(db_instance_id))
                self.client.get_waiter("db_instance_available").wait(
                    DBInstanceIdentifier=db_instance_id
                )
                self.client.modify_db_instance(
                    DBInstanceIdentifier=db_instance_id,
                    EngineVersion=pg_engine_version,
                    AllowMajorVersionUpgrade=True,
                    ApplyImmediately=True
                )
                print("Upgrading {} to: {}"
                      .format(db_instance_id, pg_engine_version))
                time.sleep(30)

    def _set_db_instance_ids_from_tags(self):
        matching_db_instance_ids = set([])
        for db_instance in self.client.describe_db_instances()["DBInstances"]:
            tags = self.client.list_tags_for_resource(
                ResourceName=db_instance["DBInstanceArn"]
            )
            tag_list = tags.get("TagList")
            if tag_list is not None:
                if all(
                    self.db_instance_tags.get(tag["Key"]) == tag["Value"]
                    for tag in tag_list
                ):
                    matching_db_instance_ids.add(
                        db_instance["DBInstanceIdentifier"]
                    )
        if not matching_db_instance_ids:
            print("No instances found matching tags: {}"
                  .format(self.db_instance_tags))
        self.db_instance_ids = list(matching_db_instance_ids)

    def upgrade(self):
        threads = []
        for db_instance_id in self.db_instance_ids:
            if self._uses_postgres(db_instance_id):
                thread = Thread(target=self._modify_db, args=(db_instance_id,))
                threads.append(thread)
                thread.start()
        for thread in threads:
            thread.join()


def create_parser():
    parser = argparse.ArgumentParser(
        description='Gather RDSPostgresUpgrader configurables.'
    )
    db_instance_id_group = parser.add_mutually_exclusive_group(required=True)
    db_instance_id_group.add_argument(
        '-ids', '--rds_db_instance_ids', type=str, nargs='+',
        help='RDS DBInstanceIdentifier(s) to target for an upgrade'
    )
    db_instance_id_group.add_argument(
        '-tags', '--rds_db_instance_tags', type=json.loads,
        help='Tags of RDS DBInstances to target for an upgrade'
    )
    parser.add_argument(
        '-versions', '--pg_target_versions', type=str, nargs='+',
        help='One or more postgres engine version(s) to target for an upgrade',
        default=["9.4.18", "9.5.13", "9.6.9", "10.4"]
    )
    return parser


def main():
    args = create_parser().parse_args()
    RDSPostgresUpgrader(args.pg_target_versions,
                        ids=args.rds_db_instance_ids,
                        tags=args.rds_db_instance_tags).upgrade()

if __name__ == '__main__':
    main()
