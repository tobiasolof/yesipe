{TextLayer} = require 'TextLayer'
makeGradientModule = require("makeGradient")
arcMovement = require "arcMovement"
{request} = require "npm"

# Definitions -----

standardSize = Screen.width / 10
bubbleSize = standardSize * 3.5
canvasSize = Screen.height * 3

green = "#61A6A1"
purple = "#E76186"
beige = "#CCC1AA"
white = "#FFFFFF"

# Variables -----

bubbles = []
foodStrings = []

# Layers -----

bkg = new BackgroundLayer
	backgroundColor: white

bubbleScroll = new ScrollComponent
	width: Screen.width
	height: Screen.height

# chosenLayer = new Layer
#   width: Screen.width
#   height: Screen.height

spacerForScroll = new Layer
	superLayer: bubbleScroll.content
	backgroundColor: white
	width: canvasSize
	height: canvasSize

centerOfCanvas = {
	x: spacerForScroll.width / 2 - Screen.width / 2,
	y: spacerForScroll.height / 2 - Screen.height / 2
}

bubbleScroll.scrollToPoint(centerOfCanvas)

screenReferenceLayer = new Layer
	width: Screen.width
	height: Screen.height
	opacity: 0

chosenCollector = new Layer
	superLayer: screenReferenceLayer
	width: 20
	height: 20
	backgroundColor: beige
	borderRadius: bubbleSize * 5
	x: -200
	y: Screen.height + 200
	index: 5

chosenCollector.states.add
	show:
		scale: 1
		width: bubbleSize * 2
		height: bubbleSize * 2
		midX: bubbleSize - 100
		midY: Screen.height - bubbleSize + 100

chosenCollector.states.animationOptions =
	time: .5

YESipe_logo = new Layer
	width: standardSize * 4
	height: standardSize * 4
	midX: Screen.width / 2
	midY: Screen.height / 2
	image: "images/YESipe-logo.png"
YESipe_logo.center()

# Functions -----

to_hash = (pairs) ->
  hash = {}
  hash[key] = value for [key, value] in pairs
  hash

flyOut = (b) ->
  b.animate
    properties:
      x: (b.x - Screen.width / 2) * 10
      y: (b.y - Screen.height/ 2) * 10

chosen = []
placeBubbles = (suggestions) ->
  bubbles = []
  for s, i in suggestions
    do (s, i) ->
      bubbles[i] = new Layer
        name: s['name']
        borderRadius: 1000
        parent: bubbleScroll.content
        width: s['r']
        height: s['r']
        x: s['x']
        y: s['y']
        backgroundColor: green
      createText(i, s['name'], s['r'])

      bubbles[i].states.add
        def:
          parent: bubbleScroll.content
          width: s['r']
          height: s['r']
          x: s['x']
          y: s['y']
          backgroundColor: green
        selected:
          # parent: screenReferenceLayer.content
          scale: 140 / bubbles[i].width
          midX: 1200 + 100 * (chosen.length - 1)
          midY: Screen.height - 110
          backgroundColor: purple
        done:
          scale: 250 / bubbles[i].width
          midX: 150 + (200 * chosen.length)
          midY: 250
        recipe:
          scale: 50 / bubbles[i].width
          y: -Screen.height
          x: Align.center
        reset:
          x: -Screen.width
          y: 2 * Screen.height


      bubbles[i].onTap ->
        do (i) ->
          return if bubbleScroll.isDragging
          # Move bubble from bubbles to chosen
          bubbles[i].states.switch("selected")
          chosenCollector.states.switch("show")
          chosen.push bubbles[i]

          bubbles.splice(i, 1)
          # Make bubbles fly out
          for b in bubbles
            flyOut(b)
            # b.destroy()
          get_suggestions()

doneLayer = new Layer
  superLayer: chosenCollector
  z: 10
  width: standardSize * 2
  height: standardSize * 2
  backgroundColor: green
  borderRadius: 500
  scale: 0.1
doneLayer.center()

checkIcon = new Layer
  superLayer: doneLayer
  width: doneLayer.width / 2.5
  height: doneLayer.width / 2.5
  image: "images/check3 - white.png"
checkIcon.center()

done=null
launchDone = () ->

  doneLayer.states.add
    show:
      scale: 1
      width: standardSize * 2
      height: standardSize * 2
      backgroundColor: green
      borderRadius: 500
      x: Align.center
      y: Align.center
    done:
      midX: screenReferenceLayer.midX
      maxY: Screen.height - 100
      scale: 1.3
    recipe:
      midX: screenReferenceLayer.midX
      y: Screen.height + 500

  doneLayer.states.animationOptions =
    curve: "spring(880, 47, 0)"
  doneLayer.states.switch("show")
  doneLayer.states.animationOptions =
    time: 1

  doneLayer.onClick ->
    if doneLayer.states.current is "show"
      doneLayer.superLayer = screenReferenceLayer
      doneLayer.midX = chosenCollector.midX
      doneLayer.midY = chosenCollector.midY
      doneLayer.states.switch("done")
      # launchRecipe()
      # for b in bubblesChosen
      # 	b.states.switch("done")

    # else
    # 	i = recipePage.horizontalPageIndex(recipePage.currentPage)
#
    # 	done.states.switch("recipe")
    # 	recipePage.states.switch("recipe")
    # 	recipePic[i].states.switch("recipe")
    # 	recipeInfo[i].states.switch("final")
    # 	for r in recipeTitle
    # 		r.states.switch("recipe")
    # 	for b in bubblesChosen
    # 		b.states.switch("recipe")
    # 	for i in extraIngredient
    # 		i.states.switch("recipe")
    # 	done.placeBefore()
#
    # reset.states.switch("default")
    # chosenCollector.states.switch("default")
# 	# 	chosenCollector.states.switch("recipe")
    # searchBar.states.switch("default")

    flyoutBubbles()

get_suggestions = () ->
  body =
    n: 30
    canvas_size: canvasSize
    dev_x: Screen.width
    dev_y: Screen.height
    chosen: to_hash ([c["name"], [c["name"]]] for c in chosen)
  request(
    url: 'http://localhost:8005/generate_suggestions'
    method: 'POST'
    headers: 'content-type': 'application/json'
    body: JSON.stringify(body)
    (error, response, body) ->
      placeBubbles(JSON.parse(response.body))
  )

createText = (i, name, r) ->
  do () ->
    foodStrings[i] = new TextLayer
      superLayer: bubbles[i]
      name: name
      autoSizeHeight: true
      textTransform: "capitalize"
      width: 100
      padding: 30
      # lineHeight: 1.1
      fontSize: r / 5
      fontFamily: "CircularStd-Bold"
      text: name
      color: "white"
      textAlign: "center"
      visible: true
    foodStrings[i].center()

# MAIN -----

body = JSON.stringify({
  "chosen": {
    "ananas": ["ananas"],
    "lax": ["lax", "laxfilé"]
  },
  "n": 30,
  "canvas_size": canvasSize,
  "dev_x": Screen.width,
  "dev_y": Screen.height
})

YESipe_logo.onTap ->
  YESipe_logo.visible = false
#	YESipe_logo.animate
#		properties: {
#			midX: Screen.width / 2
#			midY: Screen.height / 2
#		}
  get_suggestions()
