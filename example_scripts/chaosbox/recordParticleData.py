# This file is located at:
# "~/Python/iaq/Publish_to_InfluxDB.py"

import json
import requests
import sseclient
import time as time
import decoder as de
from termcolor import colored
from influxdb import InfluxDBClient


# Credentials are store in a GIT IGNORE'ed file
import credentials as cd

# particles to watch in the SSEStream
good_particles = [
    '580053000b51353335323535', # PH013
    '450035000a51353335323536',
    '290041000f47353136383631',
    '30001d001447353136383631',
    '2a003f000347353137323334',
    '340032001447353136383631',
    '27001c001347353136383631',
    '340032001447353136383631',
    '390026000a47353137323334',
    '1d002a000b47353137323334', # PH062
    '38003c001447353136383631', # PH027
    '420058000a51353335323536', # PH008
    '19002b000b47353137323334', # PH040
    '3e003e000d47353136383631', # PH035
    '340040001447353136383631', # PH037
    '3b001f001447353136383631', # parklet_1
    '340024001447353136383631', # parklet_2
    '280028000a51353335323535', # PH012
    '1f004b000a51353335323536', # PH011
    '48001d000b51353335323535', # PH007
    '540048000b51353335323536', # PH015
    '2a0060000a51353335323535', # PH017
    '2a0032000547343233323032', # PH023
    '410021000d47353136383631', # PH026
    '270030000d47353136383631', # PH031
    '340047000b47353137323334', # PH032
    '390043001447353136383631', # PH039
    '2b0049000347353137323334', # PH036
    '2f0044000647343232363230', # PH063
    '180031001951353338363036', # EL002
    '530035000c51343334363138', # EL001
    '520035000c51343334363138', # EL003
    '2a002a000b51343334363138', # EL004
    '200039000347343339373536', # PH022
    '3b003d000c51343334363138', # EL005
    '26002d001651353530333533', # PH038
    '34003e001447353136383631', # PH028
]


# make sure this is current
access_token = cd.access_token

# influx credentials
usr = cd.usr
password = cd.passwd
db = cd.db
host = cd.host
port = cd.port
measurement = cd.measurement
client = InfluxDBClient(host, port, usr, password, db)

# will hold all registered particles
particles = {}

# this is a list of messages that need to be understood and programmed for
unknown_messages = [
    'spark/device/app-hash',
    'spark/device/last_reset'
]


class Particle:
    def __init__(self, _id, name, last_app, last_ip_address, last_heard, product_id, connected, platform_id,
                 cellular, status):

        # Particle defined attributes
        self.id = _id
        self.name = name
        self.last_app = last_app
        self.last_ip_address = last_ip_address
        self.last_heard = last_heard
        self.product_id = product_id
        self.connected = connected
        self.platform_id = platform_id
        self.cellular = cellular
        self.status = status
        self.log = False

        # Particles APIs
        self.api = "https://api.particle.io/v1/devices/" + self.id + "/?access_token=" + access_token
        self.var_api = 'https://api.particle.io/v1/devices/' + self.id + '/?access_token=' + access_token
        self.result_api = ''

        # Chaos defined attributes
        self.has_location = False
        self.location = "unknown"
        self.experiment = "unknown"
        self.var_req = None
        self.var_json = None
        self.variables = []
        self.current_var = None
        self.measurements = {}

        # Gather more data if device is connected
        if self.connected:
            try:
                self.get_variables()
            except:
                self.connected = False
                print(self.name + ' is now offline.')

    def print_attributes(self):
        print('\n' + colored(self.name, 'red'))
        print('Location: ')
        try:
            print colored(self.location, 'green')
        except:
            print colored('Unknown', 'green')
        print 'Connected: ' + colored(self.connected, 'blue')
        print 'Variables are:'
        for i in self.variables:
            print i

    def generate_result_url(self):
        self.result_api = 'https://api.particle.io/v1/devices/' + self.id + '/' + self.current_var + '/?access_token=' + access_token
        return self.result_api

    def get_variables(self):
        # reset our variable list
        self.variables = []

        try:
	    self.var_req = requests.get(self.var_api)
	    self.var_json = self.var_req.json()['variables']
	    try:
		self.variables = [v for v in self.var_json]
	    except TypeError:
		self.connected = False
		print self.name + ' status was updated: Connected = ',
		print colored(self.connected, 'blue')

		# # add measurements for each variable
		# for v in self.variables:
		#     self.measurements[v] = m.return_measurement(v)
            if 'logging' in self.variables:
                try:
		    self.current_var = 'logging'
		    self.generate_result_url()
		    self.var_req = requests.get(self.result_api)
		    self.var_json = self.var_req.json()
		    self.log = self.var_json['result']
		    print 'Device\'s log status is: ',
		    print colored(self.log, 'green')
		except:
		    print colored('Error retrieving log status', 'cyan')

	    if 'location' in self.variables:
		self.has_location = True
		self.location = 'known'
		self.variables = [v for v in self.variables if v != 'location']
		print '\n' + colored(self.name, 'red')
		print 'finding location...'
		try:
		    self.current_var = 'location'
		    self.generate_result_url()
		    self.var_req = requests.get(self.result_api)
		    self.var_json = self.var_req.json()
		    self.location = self.var_json['result']
		    print 'Device\'s location is: ',
		    print colored(self.location, 'green')
		except:
		    print colored('Error retrieving location', 'cyan')

	    print 'It\'s ' + colored('variables', 'green') + ' are: '
	    for v in self.variables:
		print v
		    # print self.measurements[v]
        except KeyError:
	    print 'This particles has no variables'


# deviceAPI
class DeviceAPI:
    def __init__(self):
        self.url = 'https://api.particle.io/v1/devices/?access_token=' + access_token

        self.devices_req = None
        self.devices_json = None
        self.claimed = 0
        self.connected = 0
        self.selected_particle = None

        self.start_time = 0
        self.end_time = 0
        self.duration = 0

        # create particle objects, and time it
        print colored('\nWELCOME', 'cyan')
        print 'Creating Particle objects...'
        self.start_time = time.time()
        self.create_particles()  # this is where the magic happens
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        print '\nIt took ' + colored(self.duration, 'red') + ' seconds.'

    def get_particles(self):
        self.devices_req = requests.get(self.url)
        self.devices_json = self.devices_req.json()
        return self.devices_json

    # generates a dictionary of particles from the Particles DeviceAPI
    def create_particles(self):
        for l in self.get_particles():
                particles[l['id']] = Particle(
                    l['id'],
                    l['name'],
                    l['last_app'],
                    l['last_ip_address'],
                    l['last_heard'],
                    l['product_id'],
                    l['connected'],
                    l['platform_id'],
                    l['cellular'],
                    l['status'],
                )


    # updates all the claimed particles with the results of Particles DeviceAPI call
    def update_particles(self):
        for l in self.get_particles():
                particles[l['id']].id = l['id']
                particles[l['id']].name = l['name']
                particles[l['id']].id = l['id']
                particles[l['id']].name = l['name']
                particles[l['id']].last_app = l['last_app']
                particles[l['id']].last_ip_address = l['last_ip_address']
                particles[l['id']].last_heard = l['last_heard']
                particles[l['id']].product_id = l['product_id']
                particles[l['id']].connected = l['connected']
                particles[l['id']].platform_id = l['platform_id']
                particles[l['id']].cellular = l['cellular']  # that really doesn't need to be there
                particles[l['id']].status = l['status']

    def connected_particles(self):
        if particles:
            self.update_particles()  # update the device statuses
            self.enumerate_connected()
        else:
            self.create_particles()
            self.connected_particles()

    def enumerate_connected(self):
        self.connected = 0
        for p in particles:
            if particles[p].connected:
                self.connected += 1
        print '\nThere are ' + str(self.connected) + colored(' connected', 'green') + ' Particles:'
        for p in particles:
            if particles[p].connected:
                self.selected_particle = particles[p]
                print self.selected_particle.name,
                # print 'Location:',
                # print particles[p].location,
                print particles[p].id,
                print particles[p].name


class SSEClient:
    def __init__(self):
        self.url = 'https://api.particle.io/v1/devices/events?access_token=' + access_token
        self.client = None
        self.event = None
        self.data = None
        self.json_body = None
        self.measurement = None
        self.particle_to_update = ''
        self.json2write = None

    def start_sse(self):
        self.client = sseclient.SSEClient(self.url)
        for event in self.client:
            if type(event.data) is not str:
                # set object attributes to current event
                self.event = event.event
                self.data = event.data
                self.data = json.loads(self.data)

                if particles[self.data['coreid']].log == True or self.data['coreid'] == '53ff6a066678505539552367':  # 
                    # if the event is a status change, update
                    if self.event == 'spark/status':
                        self.particle_to_update = self.data['coreid']
                        if self.data['data'] == 'online':
                            particles[self.particle_to_update].connected = True
                            particles[self.particle_to_update].get_variables()
                        elif self.data['data'] == 'offline':
                            particles[self.particle_to_update].connected = False
                        else:
                            print colored('Unknown spark status', 'yellow')

                        print particles[self.particle_to_update].name + ' status was updated: Connected = ',
                        print colored(particles[self.particle_to_update].connected, 'blue')

                        # add a call to update particle if connected = True
                        self.particle_to_update = None

                    elif self.event == 'spark/device/app-hash':
                        print colored('HOLY SHIT', 'red'),
                        print 'we got a ',
                        print colored('spark/device/app-hash', 'green'),
                        print 'event. Better figure out what to do with those!'
                    # otherwise

                    else:
                        # generate the influx object, by passing the appropriate particle
                        self.influx_write(
                            self.data['coreid'],
                            self.event,
                            self.data['published_at'],
                            self.data['data']
                        )

        def json_write(self, measurement, name, location, _time, _type, value, specific=None):
            self.json2write = [
                {
                "measurement": measurement,
                "tags": {
                    'name': name,
                    'location': location,
                    'label': specific,
                },
                "time": _time,
                "fields": {
                    _type: value,
                }
            }
        ]
        return self.json2write

    def influx_write(self, _id, key, _time, value):
        if particles:
            # When new code is flashed
            # print event
            # print value

            # Start working
            if key == 'spark/flash/status':
                if value == 'started':
                    print colored(particles[_id].name, 'red') + 'is being ' + colored('flashed', 'red')
                elif value == 'success':
                    print colored(particles[_id].name, 'red') + 'flash ' + colored('successful!', 'green')
                self.json_body = [
                    {
                        "measurement": 'firmware',
                        "tags": {
                            "name": particles[_id].name,
                            'location': particles[_id].location
                        },
                        "time": _time,
                        "fields": {
                            "value": value,
                        }
                    }
                ]
                client.write_points(self.json_body)
                return
            elif key == 'spark/device/last_reset':
	        pass
	    else:
		print colored(particles[_id].name, 'red'),
		print key,
		print value
		for r in de.decode_event(key, value):	
			# print r[0], r[1], r[2], r[3]
		    self.json_body = [
			{
			    "measurement": measurement,
			    "tags": {
			        "experiment": 'unknown',
			        'location': particles[_id].location,
			        "label": r[0],
			        "event": r[2],
			        "unit": r[3],
			        "name": particles[_id].name,
			    },
			    "time": _time,
			    "fields": {
			        "value": float(r[1]),
			    }
			}
		    ]
		    # print self.json_body
		    client.write_points(self.json_body)
        else:
            print 'Particles have not been created!'


d = DeviceAPI()
d.connected_particles()

s = SSEClient()
print '\nStarting SSE Client...'
while True:
    try:
        s.start_sse()
    except:
        print colored("FATAL ERROR, restarting", 'red')

