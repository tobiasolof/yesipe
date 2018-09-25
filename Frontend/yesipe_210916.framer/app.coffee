{TextLayer} = require 'TextLayer'
{request} = require "npm"

# Definitions -----

standardSize = Screen.width / 10

green = "#61A6A1"
purple = "#E76186"
beige = "#CCC1AA"
white = "#FFFFFF"

# Variables -----

bubbles = []
chosen = []
recipes = []

# Layers -----

bkg = new BackgroundLayer
  width: Screen.width
  height: Screen.height
  backgroundColor: beige

YESipe_logo = new Layer
	width: standardSize * 4
	height: standardSize * 4
	midX: Screen.width / 2
	midY: Screen.height / 2
	image: "images/YESipe-logo.png"
YESipe_logo.onTap ->
  YESipe_logo.visible = false
  get_suggestions('')

checkIcon = new Layer
  width: standardSize
  height: standardSize
  maxX: Screen.width
  minY: 0
  borderRadius: standardSize
  image: "images/tick.png"
  visible: false
checkIcon.onTap ->
  refreshIcon.visible = false
  for b in bubbles
    do (b) ->
      b.states.switch('out')
  get_recipes()

refreshIcon = new Layer  # TODO: ADD TO TRAINING DATA EACH TIME
  width: standardSize
  height: standardSize
  maxX: Screen.width - checkIcon.width*1.1
  minY: 0
  borderRadius: standardSize
  image: "images/refresh.png"
  visible: false
refreshIcon.onTap ->
  for b in bubbles
    do (b) ->
      if b not in chosen
        b.states.switch('out')
  get_suggestions()

backIcon = new Layer
  width: standardSize
  height: standardSize
  maxX: Screen.width
  minY: 0
  borderRadius: standardSize
  image: "images/cancel.png"
  visible: false
backIcon.onTap ->
  for b in bubbles
    do (b) ->
      if b in chosen
        b.states.switch('selected')
      else
        b.states.switch('def')
  backIcon.visible = false
  checkIcon.visible = true
  refreshIcon.visible = true
  recipeLayer.visible = false

recipeLayer = new PageComponent
  backgroundColor: null
  y: backIcon.height*1.1
  height: Screen.height
  width: Screen.width
  scrollVertical: false
  visible: false

launchRecipe = (recipes) ->
  checkIcon.visible = false
  backIcon.visible = true
  recipeLayer.visible = true
  for recipe in recipeLayer.content.subLayers
    recipe.destroy()
  for r, i in recipes
    do (r, i)->
      recipe = new Layer
        name: 'recipe'+i
        superLayer: recipeLayer.content
        x: Screen.width*i
        width: Screen.width
        backgroundColor: null

      recipeInfo = new Layer
        name:'recipeInfo'+i
        superLayer: recipe
        width: Screen.width*0.55
        height: Screen.width*0.25
        backgroundColor: null
        borderWidth:10
        borderColor:'grey'
        x: Align.center
        opacity: 1

      recipeInfoText = new TextLayer
        name:"recipeInfoText"+i
        superLayer: recipeInfo
        backgroundColor: bkg.backgroundColor
        width: recipeInfo.width
        autoSizeHeight: true
        fontSize: standardSize/2
        text: "tid: "+ r["cooking_time"]+  "\n" + r["score"] + " / " + r["ingredients"].length + " ingredienser"
        fontFamily: "CircularStd-Bold"
        color: "grey"
        textAlign: "center"
        setup: true
      recipeInfoText.center()

      recipePic = new Layer
        name:"recipePic"+i
        superLayer: recipe
        x: Align.center
        y: recipeInfo.height*1.1
        backgroundColor: beige
        width: Screen.width * 0.8
        height: Screen.width * 0.8
        borderRadius: Screen.width * 0.8 / 2
        image: r["image"]

      recipeTitle = new TextLayer
        name:"recipeTitle"+i
        backgroundColor: "rgba(255,255,255,0.7)"
        padding: 20
        superLayer: recipe
        y: recipePic.y * 1.2
        minX: 0
        width: recipePic.width
        text: r["title"]
        fontSize: standardSize/2
        autoSizeHeight: true
        lineHeight: standardSize / 20
        fontFamily: "CircularStd-Bold"
        color: green
        textAlign: "center"
        setup: false

      instructionScroll = new ScrollComponent
        name: "instructionScroll"+i
        superLayer: recipe
        width: Screen.width*0.8
        height: Screen.height
        y: recipePic.y + recipePic.height
        x: Align.center
        scrollHorizontal: false
      instructionScroll.onScroll ->
        recipeLayer.scroll=false
      instructionScroll.onScrollEnd ->
        recipeLayer.scrollHorizontal = true

      recipeInstructions = new TextLayer
        name: "recipeInstructions"+i
        superLayer: instructionScroll.content
        width: instructionScroll.width
        height: Screen.height*1.3
        text: r["instructions"]
        color: "black"
        fontFamily: "CircularStd-Bold"
        fontSize: standardSize/4
        lineHeight: 1.5

# Functions -----

dict_compr = (pairs) ->
  hash = {}
  hash[key] = value for [key, value] in pairs
  hash

extremePosition = (x, y) ->
  {
    x: (x - Screen.width / 2) * 100
    y: (y - Screen.height / 2) * 100
  }

makeBubble = (s) ->
  p = extremePosition(s['x'], s['y'])
  b = new Layer
    parent: bkg
    name: s['name']
    width: s['r']
    height: s['r']
    borderRadius: s['r']/2
    midX: p['x']
    midY: p['y']
    backgroundColor: green
  b.states.add
    def:
      midX: s['x']
      midY: s['y']
      backgroundColor: green
    selected:
      midX: s['x']
      midY: s['y']
      backgroundColor: purple
    out:
      midX: p['x']
      midY: p['y']
  b.states.switch('def')
  createText(b, s)
  b.onTap ->
    if b.states.current is 'def'
      b.states.switch('selected')
      chosen.push b
      checkIcon.visible = true
      refreshIcon.visible = true
    else if b.states.current is 'selected'
      b.states.switch('def')
      chosen = chosen.filter (c) -> c isnt b
  return b

createText = (b, s) ->
  f = new TextLayer
    parent: b
    name: s['name']
    x: Align.center
    y: Align.top
#    midX: b.midX
#    midY: b.midY
    text: s['name']
#    autosize: true
    textAlign: "center"
    textTransform: "capitalize"
    fontFamily: "CircularStd-Bold"
    color: "black"
    visible: true
  return f

get_suggestions = (b) ->
  body =
    n: 10
    dev_x: Screen.width
    dev_y: Screen.height
    chosen: dict_compr ([c["name"], [c["name"], c["midX"], c["midY"], c["width"]]] for c in chosen)
    choice: if b then b['name'] else ''
  request(
    url: 'http://localhost:8005/generate_suggestions'
    method: 'POST'
    headers: 'content-type': 'application/json'
    body: JSON.stringify(body)
    (error, response, body) ->
      suggestions = JSON.parse(response.body)
      for s in suggestions
        do (s) ->
          bubbles.push makeBubble(s)
  )

get_recipes = () ->
  recipes = []
  body =
    chosen: dict_compr ([c["name"], [c["name"]]] for c in chosen)
  request(
    url: 'http://localhost:8005/generate_recipes'
    method: 'POST'
    headers: 'content-type': 'application/json'
    body: JSON.stringify(body)
    (error, response, body) ->
      launchRecipe(JSON.parse(response.body))
  )
