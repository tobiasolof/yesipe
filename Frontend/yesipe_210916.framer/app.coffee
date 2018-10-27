{TextLayer} = require 'TextLayer'
{request} = require "npm"

# Definitions -----

standardSize = Screen.width / 10
maxScrollDist = Screen.height / 10

green = "#61A6A1"
purple = "#E76186"
beige = "#CCC1AA"
white = "#FFFFFF"

# Variables -----

bubbles = []
chosen = []
recipes = []

# Layers -----

backgroundLayer = new Layer
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
  bubbleLayer.visible = true
  get_suggestions('')

bubbleLayer = new Layer
  parent: backgroundLayer
  size: Screen
  backgroundColor: null
  visible: false
bubbleLayer.states.add
  out:
    maxY: 0
  in:
    minY: 0

pullDown = new TextLayer
  parent: bubbleLayer
  width: Screen.width
  autoSizeHeight: true
  y: Align.top
  text: "pull down to refresh suggestions"
  textAlign: "center"
  fontFamily: "Helvetica"
  fontWeight: 100
  fontSize: Screen.height / 75
  color: "black"
pullDown.states.add
  def:
    y: pullDown.y

arrowDown = new Layer
  parent: pullDown
  backgroundColor: null
  height: pullDown.height * 1.5
  width: pullDown.width / 4
  x: Align.center
  minY: pullDown.height
  html: "<img src = 'images/down-arrow.png' height = '10%' width = '10%'>"
arrowDown.states.add
  def:
    minY: arrowDown.minY
    scale: 1

pullUp = new TextLayer
  parent: bubbleLayer
  width: pullDown.width
  autoSizeHeight: true
  text: "pull up to generate recipes"
  textAlign: "center"
  fontFamily: pullDown.fontFamily
  fontWeight: pullDown.fontWeight
  fontSize: pullDown.fontSize
  color: pullDown.color
pullUp.y = Align.bottom
pullUp.states.add
  def:
    y: pullUp.y

arrowUp = new Layer
  parent: pullUp
  backgroundColor: arrowDown.backgroundColor
  height: arrowDown.height
  width: arrowDown.width
  x: arrowDown.x
  maxY: 0
  html: "<img src = 'images/up-arrow.png' height = '10%' width = '10%'>"
arrowUp.states.add
  def:
    maxY: arrowUp.maxY
    scale: 1

bubbleScroll = new ScrollComponent
  parent: bubbleLayer
  width: Screen.width
  height: Screen.height
  opacity: 0
  scrollHorizontal: false
bubbleScroll.onScroll ->
  if bubbleScroll.scrollY < 0
    if arrowDown.y < maxScrollDist
      pullDown.y -= 1
      arrowDown.y += 2
      arrowDown.scale = 1 - (1/maxScrollDist)*arrowDown.y
      pullUp.y += 1
      arrowUp.y += 1
  if bubbleScroll.scrollY > 0
    if arrowUp.y > -maxScrollDist
      pullUp.y += 1
      arrowUp.y -= 2
      arrowUp.scale = 1 - (1/maxScrollDist)*(-arrowUp.y)
      pullDown.y -= 1
      arrowDown.y -= 1
bubbleScroll.onScrollEnd ->
  if bubbleScroll.scrollY < -maxScrollDist
    for b in bubbles
      do (b) ->
        if b not in chosen
          b.states.switch('out')
          b.onAnimationEnd ->
            b.destroy()
    get_suggestions()
    arrowDown.states.switch('def')
    pullDown.states.switch('def')
    arrowUp.states.switch('def')
    pullUp.states.switch('def')
  if bubbleScroll.scrollY > maxScrollDist
    for b in bubbles
      do (b) ->
        b.states.switch('out')
    bubbles[-1..][0].onAnimationEnd ->
      if bubbles[-1..][0].states.current is 'out'
        bubbleLayer.states.switchInstant('out')
        bubbleLayer.visible = false
        get_recipes()

recipeLayer = new PageComponent
  parent: backgroundLayer
  backgroundColor: null
  height: Screen.height
  width: Screen.width
  y: Screen.height*10
#  scrollVertical: false
recipeLayer.states.add
    out:
      y: recipeLayer.y
    in:
      y: Align.top

pullDownRecipe = new TextLayer
  parent: recipeLayer
  width: pullDown.width
  autoSizeHeight: true
  y: pullDown.y
  text: "pull down to get back to ingredient space"
  textAlign: "center"
  fontFamily: pullDown.fontFamily
  fontWeight: pullDown.fontWeight
  fontSize: pullDown.fontSize
  color: pullDown.color
pullDownRecipe.states.add
  def:
    y: pullDownRecipe.y

arrowDownRecipe = new Layer
  parent: pullDownRecipe
  backgroundColor: arrowDown.backgroundColor
  height: arrowDown.height
  width: arrowDown.width
  x: arrowDown.x
  minY: arrowDown.minY
  html: arrowDown.html
arrowDownRecipe.states.add
  def:
    minY: arrowDownRecipe.height
    scale: 1

launchRecipe = (recipes) ->
  recipeLayer.states.switch('in')
  for recipe in recipeLayer.content.subLayers
    recipe.destroy()
  for r, i in recipes
    do (r, i)->

      recipe = new Layer
        parent: recipeLayer.content
        height: Screen.height - (pullDownRecipe.height + arrowDownRecipe.height)
        width: Screen.width
        x: Screen.width*i
        minY: pullDownRecipe.height + arrowDownRecipe.height
        backgroundColor: null
      
      recipeScroll = new ScrollComponent
        parent: recipe
        size: Screen
        opacity: 0
        scrollHorizontal: false
      recipeScroll.onScroll ->
        if recipeScroll.scrollY < 0
          if arrowDownRecipe.y < maxScrollDist
            pullDownRecipe.y -= 1
            arrowDownRecipe.y += 2
            arrowDownRecipe.scale = 1 - (1/maxScrollDist)*arrowDownRecipe.y
      recipeScroll.onScrollEnd ->
        arrowDownRecipe.states.switch('def')
        if recipeScroll.scrollY < -maxScrollDist
          recipeLayer.states.switch('out')
          bubbleLayer.visible = true
          bubbleLayer.states.switchInstant('in')
          for b in bubbles
            do (b) ->
              if b in chosen
                b.states.switch('selected')
              else
                b.states.switch('in')
          pullDown.states.switch('def')
          arrowDown.states.switch('def')
          pullUp.states.switch('def')
          arrowUp.states.switch('def')
        pullDownRecipe.states.switch('def')

      recipeInfo = new Layer
        parent: recipe
        width: Screen.width*0.55
        height: Screen.width*0.25
        x: Align.center
        backgroundColor: null
        borderWidth:10
        borderColor:'grey'

      recipeInfoText = new TextLayer
        parent: recipeInfo
        backgroundColor: backgroundLayer.backgroundColor
        width: recipeInfo.width
        autoSizeHeight: true
        fontSize: standardSize/2
        text: "tid: "+ r["cooking_time"]+  "\n" + r["score"] + " / " + r["ingredients"].length + " ingredienser"
        fontFamily: "CircularStd-Bold"
        color: "grey"
        textAlign: "center"
      recipeInfoText.center()

      recipePic = new Layer
        parent: recipe
        width: Screen.width * 0.8
        height: Screen.width * 0.8
        x: Align.center
        y: recipeInfo.height*1.1
        borderRadius: Screen.width * 0.8 / 2
        image: r["image"]

      recipeTitle = new TextLayer
        parent: recipe
        width: recipe.width
        y: recipePic.y * 1.2
        x: Align.left
        backgroundColor: "rgba(255,255,255,0.8)"
        text: r["title"]
        fontSize: standardSize/2
        autoSizeHeight: true
        lineHeight: 1.5
        fontFamily: "CircularStd-Bold"
        textAlign: "center"
        color: green

      instructionScroll = new ScrollComponent
        parent: recipe
        width: Screen.width*0.8
        height: Screen.height
        y: (recipePic.y + recipePic.height)*1.05
        x: Align.center
        scrollHorizontal: false
      instructionScroll.onScroll ->
        recipeLayer.scroll=false
      instructionScroll.onScrollEnd ->
        recipeLayer.scrollHorizontal = true

      recipeInstructions = new TextLayer
        parent: instructionScroll.content
        width: instructionScroll.width
        height: Screen.height*2
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
  b = new TextLayer
    parent: bubbleLayer
    name: s['name']
    width: s['r']
    height: s['r']
    borderRadius: s['r']/2
    midX: p['x']
    midY: p['y']
    backgroundColor: green

    text: s['name']
    textAlign: "center"
    textTransform: "lowercase"
    fontFamily: "Helvetica"
    fontWeight: 100
    fontSize: s['r']/5
    color: "black"
  b.paddingTop = (b.height - b.fontSize)/2
  b.paddingBottom = (b.height - b.fontSize)/2
  b.states.add
    in:
      midX: s['x']
      midY: pullDown.height + s['y']
      backgroundColor: green
    selected:
      midX: s['x']
      midY: pullDown.height + s['y']
      backgroundColor: purple
    out:
      midX: p['x']
      midY: p['y']
  b.states.switch('in')
  b.onTap ->
    # TODO: ADD TO TRAINING DATA
    if b.states.current is 'in'
      b.states.switch('selected')
      chosen.push b
    else if b.states.current is 'selected'
      b.states.switch('in')
      chosen = chosen.filter (c) -> c isnt b
  return b

get_suggestions = (b) ->
  body =
    n: 10
    dev_x: Screen.width
    dev_y: Screen.height - pullDown.height - pullUp.height
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
