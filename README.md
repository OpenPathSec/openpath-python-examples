# Openpath Python sample code

This repository contains sample code for using Python3 to interact
with Openpath APIs and systems.

> For general info about Openpath, see https://www.openpath.com/.

> For developer-centric info, including walk-throughs on using the API
> as well as detailed interactive API documentation, see
> https://openpath.readme.io/.

Note that the sample code here is merely intended to demonstrate the
minimum sequence of steps needed to get you up and running with a data
flow, and is such is written in a straightline fashion, without the
encapsulation, abstractions, error-handling, or separation of
code/config that you would expect in production code.

### User/credential management sample

Several code samples in the `users_example` directory can serve as
skeletons for working with users and credentials.

To set up:

```
cd users_example
pip3 install --user -r requirements.txt    # or use a virtualenv or your other preferred approach to python packages
```

Then to list all the users in your org:

```
python3 users_example.py you@corp.com yourOpenpathPassword yourOpenpathOrgId
```

To list all the credentials (covering all users) in your org:

```
python3 credentials_example.py you@corp.com yourOpenpathPassword yourOpenpathOrgId
```

Or try the following for a more complex example that does multiple steps:
- fetch all users
- fetch all credentials
- find an existing user matching a given email address, or else create such a user if none exists yet
- for that user, find an existing card credential with a given number, or else create such a credential if none exists yet

```
python3 create_credential_example.py you@corp.com yourOpenpathPassword yourOpenpathOrgId emailAddressOfUserToFindOrCreate cardNumberInOpenpath64BitFormat
```

### MQTT/websockets samples

For general info on our MQTT system for pushing real-time events out
to clients, see
https://openpath.readme.io/docs/real-time-events-via-mqtt.

In python, there are two main approaches to using MQTT with
Openpath. The simpler approach is to use the native python AWS IoT
SDK. A more lightweight approach (from the perspective of required
dependencies) is to use a vanilla MQTT client, namely paho.

#### MQTT with AWS SDK

This example relies on the [official AWS IoT SDK](https://github.com/aws/aws-iot-device-sdk-python).

See the example code in [awssdk_example.py](awssdk_example/awssdk_example.py).

Run it as follows:

```
cd awssdk_example
pip3 install --user -r requirements.txt    # or use a virtualenv or your other preferred approach to python packages
python3 awssdk_example3.py you@corp.com yourOpenpathPassword yourOpenpathOrgId yourOpenpathAcuId
```

#### MQTT with paho library

This examples relies on [paho, a python MQTT library](https://github.com/eclipse/paho.mqtt.python).

See the example code in [paho_example.py](paho_example/paho_example.py).

Run it as follows:

```
cd paho_example
pip3 install --user -r requirements.txt    # or use a virtualenv or your other preferred approach to python packages
python3 paho_example3.py you@corp.com yourOpenpathPassword yourOpenpathOrgId yourOpenpathAcuId
```
