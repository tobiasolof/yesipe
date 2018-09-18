{TextLayer} = require 'TextLayer'
makeGradientModule = require("makeGradient")
arcMovement = require "arcMovement"
{request} = require "npm"

# Definitions -----

standardSize = Screen.width / 10
bubbleSize = standardSize * 3.5
canvasSize = Screen.height

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
  backgroundColor: white

bubbleScroll = new ScrollComponent
  width: Screen.width * 2
  height: Screen.height * 2

chosenLayer = new Layer
  width: Screen.width
  height: Screen.height
  backgroundColor: null
  opacity = 0

YESipe_logo = new Layer
	width: standardSize * 4
	height: standardSize * 4
	midX: Screen.width / 2
	midY: Screen.height / 2
	image: "images/YESipe-logo.png"
YESipe_logo.onTap ->
  YESipe_logo.visible = false
  get_suggestions('')

checkBackground = new Layer
  width: standardSize * 2
  height: standardSize * 2
  maxX: Screen.width
  maxY: Screen.height / 2
  borderRadius: standardSize
  backgroundColor: beige
  visible: false
checkBackground.states.add
  def:
    maxX: Screen.width
    maxY: Screen.height / 2
  recipe:
    minY: 0

checkIcon = new Layer
  superLayer: checkBackground
  width: checkBackground.width / 2
  height: checkBackground.height / 2
  image: "images/check3 - white.png"
  visible: false
checkIcon.center()
checkIcon.onTap ->
  clearBubbles()
  clearChosen()
  get_recipes()

backIcon = new Layer
  superLayer: checkBackground
  width: checkBackground.width / 2
  height: checkBackground.height / 2
  image: "images/plus - white.png"
  visible: false
backIcon.center()
backIcon.onTap ->
  bringChosenBack()
  backIcon.visible = false
  checkBackground.states.switch('def')
  checkIcon.visible = true
  recipeLayer.visible = false
  get_suggestions()

recipeLayer = new PageComponent
  backgroundColor: null
  y: checkBackground.height*1.1
  height: Screen.height
  width: Screen.width
  scrollVertical: false
  visible: false

launchRecipe = (recipes) ->
  checkIcon.visible = false
  checkBackground.states.switch('recipe')
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
        backgroundColor: white
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

clearBubbles = () ->
  for b in bubbles
    do (b) ->
      b.states.switch('out')
  bubbles = []

clearChosen = () ->
  for c in chosen
    do (c) ->
      c.states.switch('recipe')

bringChosenBack = () ->
  for c in chosen
    do (c) ->
      c.states.switch('selected')

extremePosition = (x, y) ->
  {
    x: (x - Screen.width / 2) * 100
    y: (y - Screen.height / 2) * 100
  }

makeBubble = (s) ->
  p = extremePosition(s['x'], s['y'])
  b = new Layer
    parent: bubbleScroll.content
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
    selected:
#      minX: Screen.width * 0.01 + Screen.width * 0.1 * chosen.length
#      maxY: Screen.height * 0.99 / 2
      backgroundColor: purple
    out:
      midX: p['x']
      midY: p['y']
    recipe:
      midY: standardSize
      height: checkBackground.height
      width: checkBackground.width
  b.states.switch("def")
  createText(b, s)
  b.onTap ->
    if b.states.current is 'def'
      b.parent = chosenLayer
      b.midX = b.midX - bubbleScroll.scrollX
      b.midY = b.midY - bubbleScroll.scrollY
      b.states.switch('selected')
      b.animate
        minX: Screen.width * 0.01 + Screen.width * 0.1 * chosen.length
        maxY: Screen.height * 0.99 / 2
        backgroundColor: purple
      chosen.push b
      bubbles = bubbles.filter (bb) -> bb isnt b
      checkBackground.visible = true
      checkIcon.visible = true
      clearBubbles()
      get_suggestions(b)
    else if b.states.current is 'selected'
      b.states.switch('out')
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

placeBubbles = (suggestions) ->
  for s, i in suggestions
    do (s, i) ->
      bubbles[i] = makeBubble(s)

get_suggestions = (b) ->
  body =
    n: 10
    canvas_size: canvasSize
    dev_x: Screen.width
    dev_y: Screen.height
    chosen: c["name"] for c in chosen # dict_compr ([c["name"], [c["name"]]] for c in chosen)
    choice: if b then b['name'] else ''
  request(
    url: 'http://localhost:8005/generate_suggestions'
    method: 'POST'
    headers: 'content-type': 'application/json'
    body: JSON.stringify(body)
    (error, response, body) ->
      placeBubbles(JSON.parse(response.body))
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
