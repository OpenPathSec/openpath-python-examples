# Openpath Python sample code

This repository contains sample code for using Python 3.x to interact with Openpath APIs and systems.

> For general info about Openpath, see https://www.openpath.com/.
>
> For developer-centric info, including a walk-through on using the API as well as detailed interactive API documentation, see https://openpath.readme.io/.

Note that the sample code here is merely intended to demonstrate the minimum sequence of steps needed to get you up and running with a data flow, and is such is written in a straight line fashion, without the encapsulation, abstractions, error-handling, or separation of code/config that you would expect in production code.

## User/credential management sample

Several code samples in the `users_example` directory can serve as
skeletons for working with users and credentials.

To set up:

```sh
cd users_example
pip3 install --user -r requirements.txt    # or use a virtualenv or your other preferred approach to python packages
```

Then to list all the users in your org:

```sh
python3 users_example.py you@corp.com yourOpenpathPassword yourOpenpathOrgId
```

To list all the credentials (covering all users) in your org:

```sh
python3 credentials_example.py you@corp.com yourOpenpathPassword yourOpenpathOrgId
```

Or try the following for a more complex example that does multiple steps:

- fetch all users
- fetch all credentials
- find an existing user matching a given email address, or else create such a user if none exists yet
- for that user, find an existing card credential with a given number, or else create such a credential if none exists yet

```sh
python3 create_credential_example.py you@corp.com yourOpenpathPassword yourOpenpathOrgId emailAddressOfUserToFindOrCreate cardNumberInOpenpath64BitFormat
```

### MQTT/websockets samples

For general info on our MQTT system for pushing real-time events out to clients, see https://openpath.readme.io/docs/real-time-events-via-mqtt.

In python, there are two main approaches to using MQTT with Openpath. The simpler approach is to use the native python AWS IoT SDK. A more lightweight approach (from the perspective of required dependencies) is to use a vanilla MQTT client, namely paho.

#### MQTT with AWS SDK

This example relies on the [official AWS IoT SDK](https://github.com/aws/aws-iot-device-sdk-python).

See the example code in [awssdk_example.py](awssdk_example/awssdk_example.py).

Run it as follows:

```sh
cd awssdk_example
pip3 install --user -r requirements.txt    # or use a virtualenv or your other preferred approach to python packages
python3 awssdk_example3.py you@corp.com yourOpenpathPassword yourOpenpathOrgId yourOpenpathAcuId
```

#### MQTT with paho library

This examples relies on [paho, a python MQTT library](https://github.com/eclipse/paho.mqtt.python).

See the example code in [paho_example.py](paho_example/paho_example.py).

Run it as follows:

```sh
cd paho_example
pip3 install --user -r requirements.txt    # or use a virtualenv or your other preferred approach to python packages
python3 paho_example3.py you@corp.com yourOpenpathPassword yourOpenpathOrgId yourOpenpathAcuId
```

## Reports Sample

### `/orgs/{orgId}/reports/activity/events` API Sample

This specific API endpoint is different than many of the other APIs. This API uses cursor paging rather than offset & limit. This allows the API to return as much results as fast as possible without having to sort the overall result set. The implications of this is the the results are delivered out of order. If there are many results, you will have to call the API multiple times moving the cursor forward with each call. See the example for implementation details.

See the [API description at readme.io](https://openpath.readme.io/reference/getactivityevents-1) for a full API description.

See the example code in [activity-events-count-events.py](reports_activity_events_example/activity-events-count-events.py).

```sh
cd reports_activity_events_example
pip3 install --user -r requirements.txt    # or use a virtualenv or your other preferred approach to python packages
./activity-events-count-events.py --help
./activity-events-count-events.py --jwt-file my.jwt --org-id 302 --start-date '2022-01-01T00:00:00' --end-date '2022-02-01T00:00:00'
```

where my.jwt is a simple text file containing your Helium JWT authentication token returned from the login call.
