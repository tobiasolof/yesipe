# a = Utils.domLoadJSONSync('http://localhost:8005/test')


a = "[
  {
    \"freq\": 833,
    \"id\": 231,
    \"main_freq\": 133,
    \"name\": \"champinjoner\",
    \"r\": 159.48985189248492,
    \"score\": 0.9810824990272522,
    \"x\": 2165.0084614521793,
    \"y\": 1993.6238557377349
  },
  {
    \"freq\": 1823,
    \"id\": 1581,
    \"main_freq\": 437,
    \"name\": \"potatis\",
    \"r\": 250.0,
    \"score\": 0.5339010953903198,
    \"x\": 2315.8462320153703,
    \"y\": 2563.0011566412113
  }
]"






#console.log JSON.parse(a)[0]
#
#body =
#  n: 30
#  canvas_size: 2
#  dev_x: 2
#  dev_y: 2
#
#console.log JSON.parse(JSON.stringify(body))






body =
  n: 10
  canvas_size: 100
  dev_x: 100
  dev_y: 100
  chosen: []
request(
  url: 'http://localhost:8005/generate_suggestions'
  method: 'POST'
  headers: 'content-type': 'application/json'
  body: JSON.stringify(body)
  (error, response, body) ->
    console.log JSON.parse(response.body)
)