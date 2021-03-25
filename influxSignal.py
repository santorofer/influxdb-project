import MDSplus

try:
    from influxdb import InfluxDBClient
except:
    print(
        "You must install the `influxdb` python package to use the `influxhistorian` device class")
    exit(1)

def iquery(startTimeQuery=start_time, endTimeQuery=end_time):
    """Instantiate a connection to the InfluxDB."""
    host='localhost'
    port=8086

    user     = 'admin'
    password = 'password'
    dbname   = 'NOAA_water_database'

    client = InfluxDBClient(host, port, user, password, dbname)
    # example influxDB query:
    # 'SELECT "water_level" FROM "h2o_feet" WHERE time >= 1568745000000000000 AND time <= 1568750760000000000;'
    query = 'SELECT "water_level" FROM "h2o_feet" WHERE time >= %s AND time <= %s;' % (startTimeQuery, endTimeQuery)

    result = client.query(query, params={'epoch': 'ms'})

    data = list(result.get_points())

    valueData = [None] * len(data)
    timeData  = [None] * len(data)

    i = 0
    for row in data:
        valueData[i] = float(row['value'])
        timeData[i] = row['time']
        i += 1

    values = MDSplus.Float32Array(valueData)
    times  = MDSplus.Uint64Array(timeData)

    return values, times

def getTree(tree_name, shot_number):
    return MDSplus.Tree(tree_name, shot_number, 'NORMAL')


def influxSignal(tree, shot_number):
    tree = getTree(tree, shot_number)
    treetimectx = tree.getTimeContext()

    values, times = iquery(treetimectx[0], treetimectx[1])
    return MDSplus.Signal(values, None, times)