#!/usr/bin/env python3
# Example call:
#   ./activity-events-count-events.py --jwt-file prod.jwt --org-id 302 --start-date '2022-01-01T00:00:00' \
#       --end-date '2022-02-01T00:00:00'
#
#   getActivityEvents:exampleTest-302-1652216195135 starting
#   Processing 2022-01-01 00:00:00 (inclusive) to 2022-02-01 00:00:00 (exclusive) ...
#   Call 0 ... returned 30374 records, date range 2021-12-31T16:22:29.633000 - 2022-01-31T15:31:32.805000, more: True
#   Call 1 ... returned 30691 records, date range 2022-01-20T16:00:18.168381 - 2022-01-27T15:59:56.445000, more: True
#   Call 2 ... returned 31006 records, date range 2022-01-27T16:00:06.628000 - 2022-01-31T15:59:54.770000, more: False
#   92071 results.
#   getActivityEvents:exampleTest-302-1652216195135 done: 13:57:01

import os
import json
import time
import requests
import functools
from typing import Dict, Any, Optional, Union
from datetime import datetime, MAXYEAR
from datetime import datetime, timezone

import os
import time
import argparse
from datetime import datetime, timedelta

ONE_SEC_IN_MS = 1000


def time_input_to_secs(time_input: datetime) -> int:
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=timezone.utc)
    specified = time_input.replace(tzinfo=timezone.utc)
    rtn = int((specified - epoch).total_seconds())
    return rtn


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="""
        This tool calls the helium activity events API.
        """)
    parser.add_argument('--jwt-file',
                        type=str,
                        required=True,
                        help='File containing the JWT auth token to use when calling helium.')
    parser.add_argument('--start-date',
                        type=str,
                        required=True,
                        help='Start date (inclusive). E.g. "2022-01-05T00:00:00"')
    parser.add_argument('--end-date',
                        type=str,
                        required=True,
                        help='End date (exclusive). E.g. "2022-01-10T00:00:00')
    parser.add_argument('--org-id',
                        type=str,
                        required=True,
                        help='org to query.')
    parser.add_argument('--debug',
                        action='store_true',
                        default=False,
                        help='Include additional logging for better API understanding.')
    parser.add_argument('--log-all',
                        action='store_true',
                        default=False,
                        help='Set the x-op-debug: log-all header for additional server side logging.')
    parser.add_argument('--with-hook-events',
                        action='store_true',
                        default=False,
                        help='By default, this sample program does not include the hookEvent associated with an '
                             'activity event. Including this option will cause the API results to also include the'
                             'associated hookEvent object.')

    args = parser.parse_args()

    with open(args.jwt_file, 'r') as fp:
        args.jwt = fp.read().strip()

    return args


def get_activity_events(
        args: argparse.Namespace,
        search_id: str,
        start_dt: datetime, end_dt: datetime,
        cursor: Optional[str]) -> Dict[str, Any]:
    params = {
        'filter': f'uiData.time:({int(time_input_to_secs(start_dt))}-<'
                  f'{int(time_input_to_secs(end_dt))})',
        'options': f'searchId:{search_id}',
    }
    if not args.with_hook_events:
        params['options'] += ',uiDataOnly'

    if cursor:
        params['cursor'] = cursor
    headers = {
        'Authorization': args.jwt,
        'x-op-debug': 'log-all' if args.log_all else '',
    }
    url = f'https://api.openpath.com/orgs/{args.org_id}/reports/activity/events'
    if args.debug:
        print(f'{url}: headers:')
        print('Authorization: {JWT}')
        print(f'x-op-debug: {headers["x-op-debug"]}')
        print(f'Query parameters: {params}')
    response = requests.get(url=url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def minDateFn(a, b):
    return min(a, datetime.fromtimestamp(b['uiData']['time']))


def maxDateFn(a, b):
    return max(a, datetime.fromtimestamp(b['uiData']['time']))


def main():
    args = parse_args()

    start_dt = datetime.fromisoformat(args.start_date)
    end_dt = datetime.fromisoformat(args.end_date)
    overall_num = 0
    loop_num = 0
    call_stats = []
    cursor = None
    more = True
    search_id_base = f'exampleTest-{args.org_id}-{int(time.time()*1000)}'
    print(f'getActivityEvents:{search_id_base} starting')
    print(f'Processing {start_dt} (inclusive) to {end_dt} (exclusive) ... ')
    while more:
        search_id = f'{search_id_base}-{loop_num}'
        loop_num += 1
        print(f'Call {len(call_stats)} ... ', end='')
        response = get_activity_events(args=args, search_id=search_id, start_dt=start_dt, end_dt=end_dt, cursor=cursor)

        if args.debug:
            file_name = f'/tmp/reports-response-{search_id_base}-loop{loop_num}.json'
            with open(file_name, 'w') as fp:
                json.dump(response, fp)
            print(f'Full response written to: {file_name}')

        num = len(response['data'])
        min_date = functools.reduce(minDateFn, response['data'], datetime(MAXYEAR, start_dt.month, start_dt.day))
        max_date = functools.reduce(maxDateFn, response['data'], datetime.fromtimestamp(0))
        overall_num += num
        call_stats.append({
            'minDate': min_date,
            'maxDate': max_date,
            'num': num,
        })
        more = response['cursors']['hasNextPage']
        print(f'returned {len(response["data"])} records, date range {min_date.isoformat()} '
              f'- {max_date.isoformat()}, more: {more}')

        if more:
            cursor = response['cursors']['nextCursor']

        # If debugging, include blank line between loop iterations to make each loop start more obvious.
        if args.debug:
            print()

    print(f'{overall_num} results.')

    print(f'getActivityEvents:{search_id_base} done: {time.strftime("%H:%M:%S", time.localtime(time.time()))}')


if __name__ == '__main__':
    main()
