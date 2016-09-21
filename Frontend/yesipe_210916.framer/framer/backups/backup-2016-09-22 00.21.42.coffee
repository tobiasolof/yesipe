# 'Firebase REST API Class' module demo project 'firebaseSlider' v1.0
# by Marc Krenn, May 29th, 2016 | marc.krenn@gmail.com | @marc_krenn

# **Please deactivate Auto Refresh and reload manually using CMD+R!**
{Firebase} = require 'firebase'
{TextLayer} = require 'TextLayer'
makeGradientModule = require("makeGradient")
arcMovement = require "arcMovement"

# The required information is located at https://firebase.google.com → Console → YourProject → ...
yesipe_test1 = new Firebase

	projectID: "yesipe-test1" # ... Database → first part of URL
	secret: "gJI3JRUAqNkovqbSvg8063drzryPhzdmwnBr3KXZ" # ... Project Settings → Database → Database Secrets
	server: "s-usc1c-nss-104.firebaseio.com" # Get this info by setting `server: undefined´ first

# Definitions -----
fwidth = Screen.width
fheight = Screen.height

yesipe_test1.put("/deviceSize", [fwidth,fheight])

standardSize = fwidth/10
bubbleSize = standardSize*3.5
canvasSize = 5500

yesipe_test1.put("/canvasSize", canvasSize)

green = "#61A6A1"
purple = "#E76186"
beige = "#CCC1AA"

suggestionsArray = []
yesipe_test1.onChange "/suggestions", (suggs) ->
	tempArray = _.toArray (suggs)
	suggestionsArray = tempArray

positionsArray = []
yesipe_test1.onChange "/positions", (pos) ->
	tempArray = _.toArray (pos)
	positionsArray = tempArray

yesipe_test1.put("/done", false)
yesipe_test1.put("/clear", true)
Utils.delay .2, ->
	 yesipe_test1.put("/clear", false)

# Layers ------------------------------

bkg = new BackgroundLayer
	backgroundColor: "rgba(255,255,255,1)"

scroll = new ScrollComponent
# 	backgroundColor: "rgba(255,255,255,0)"
	width: fwidth
	height: fheight

spacerForScroll = new Layer
	superLayer: scroll.content
	backgroundColor: "rgba(255,255,255,1)"
	width: canvasSize
	height: canvasSize

scroll.scrollPoint = 
	x: spacerForScroll.width/2
	y: spacerForScroll.height/2

screenReferenceLayer = new Layer
	width: fwidth
	height: fheight
	backgroundColor: "rgba(255,255,255,0)"
	opacity: 1

bubbles = []
bubblesChosen = []
foodstrings = []
animationPosition = []
alternateBubbles = []
# animationText = []

chosenCollector = new Layer
	superLayer: screenReferenceLayer
	width: 20
	height: 20
	backgroundColor: beige
	borderRadius: bubbleSize*5
	x: -200
	y: fheight+200
	index: 5
	
chosenCollector.states.add
	show:
		scale: 1
		width: bubbleSize*2
		height: bubbleSize*2
		midX: bubbleSize-100
		midY: fheight-bubbleSize+100
# 	hide:
# 		scale: 0.2
# 		x: -600
# 		y: fheight+200
# 	flyaway:
# 		scale:10
# 		opacity: 0
# 	recipe:
# 		scale: 10
# 		x:Align.center
# 		y:Align.center
chosenCollector.states.animationOptions = 
	time: .5

YESipe_logo = new Layer
	width: standardSize*4.5
	height: standardSize*4.5
	image: "images/YESipe-logo.png"
YESipe_logo.center()

createBubbles = () ->
	for b in [0...suggestionsArray.length]
		do (b)->
			bubbles[b] = new Layer
				name: "bubble #" + b
				parent: scroll.content
				width: positionsArray[b][2]*2
				height: positionsArray[b][2]*2
				x: Align.center
				y: -1000
				borderRadius: 1000
				backgroundColor: green
				
			yesipe_test1.get "/positions", (array) ->
				tempArray = _.toArray (array)
				for a in [0...tempArray.length]
					animationPosition[a] = new Animation
						layer: bubbles[a]
						properties: 
							x: positionsArray[a][0]
							y: positionsArray[a][1]
# 							width: positionsArray[a][2]
# 							height: positionsArray[a][2]
						time: 1.5
					animationPosition[a].start()
	
			bubbles[b].onDoubleTap ->
# 				yesipe_test1.post("/chosen", suggestionsArray[b]["name"])
				yesipe_test1.put("/choice", b)
				x = bubblesChosen.length
				bubblesChosen.push bubbles[b]
				tempX = bubbles[b].x
				tempY = bubbles[b].y
				scaleFactor = (1/bubbles[b].width)
				tempWidth = bubbles[b].width
				tempHeight = bubbles[b].height
				bubblesChosen[x].parent = screenReferenceLayer
				bubblesChosen[x].x = tempX - scroll.scrollX
				bubblesChosen[x].y = tempY - scroll.scrollY
				
				bubblesChosen[x].states.add
					selected: 
# 						scale: 0.5
# 						width: 200
# 						height: 200
# 						scale: (1/tempWidth)*100
						scale: 140*scaleFactor
						midX: 200+100*(x-1)
						midY: fheight-110
						backgroundColor: purple
					done:
# 						scale: 0.8
						scale: 250*scaleFactor
						midX: 150 + (200*x)
						midY: 250
					recipe:
# 						scale: 0.3
						scale: 50*scaleFactor
						y: -fheight
						x: Align.center
					reset:
						x: -fwidth
						y: 2*fheight
					
				bubblesChosen[x].states.animationOptions = 
					time: 1
				
				bubblesChosen[x].states.switch("selected")
				chosenCollector.states.switch("show")
				reset.states.switch("show")	
				
				bubbles[b] = new Layer
				bubbles[b].visible = false
				foodstrings[b] = new TextLayer
				foodstrings[b].visible = false
				
				Utils.delay 0.5, ->
					if x is 0
						launchDone()
					
# 					flyoutBubbles()
								
# 					Utils.delay 0.5, ->
					yesipe_test1.onChange "/suggestions", ->
						flyoutBubbles()
						Utils.delay 0.5, ->
							resetBubbles()

				bubblesChosen[x].ignoreEvents = true
				
			bubbles[b].onLongPress ->
				yesipe_test1.put("/request", b)
				createAlternatives(bubbles[b], bubbles[b].midX, bubbles[b].midY)
				scroll.scrollToPoint(
					x: bubbles[b].midX - fwidth/2
					y: bubbles[b].midY - fheight/2)
				
				for bub in bubbles
					do (bub) ->
						bub.animate
							properties:
								opacity: 0.5
# 						bub.opacity = 0.5
						bubbles[b].animateStop()
						bubbles[b].opacity = 1
						
						Utils.delay 2, ->
							bubbles[b].onClick ->
								for bub in bubbles
									bub.animate
										properties:
											opacity:1
							yesipe_test1

alternateArray = []
# yesipe_test1.onChange "/altIngredients/alternatives", (alt) ->
# 	tempArray = _.toArray (alt)
# 	alternateArray = tempArray

createAlternatives = (orgLayer, orgX, orgY) ->
	yesipe_test1.onChange "/altIngredients/alternatives", (alt) ->
		tempArray = _.toArray (alt)
		alternateArray = tempArray
		
		print alternateArray
		
		for a in [0...alternateArray.length]
			do (a) ->
				alternateBubbles[a] = new Layer
					superLayer: scroll.content
					width: bubbleSize
					height: bubbleSize
					borderRadius: bubbleSize
	# 				x: orgX - 300 + (bubbleSize*1.1)*a
	# 				y: orgY + bubbleSize*1.5
					midX: orgX
					midY: orgY
					scale:0.1
					backgroundColor: purple
					circleCoord = arcMovement.circlePoint orgX, orgY, 360/alternateArray.length*a, orgLayer.width*1.2, orgLayer.width*1.2
					
				orgLayer.placeBefore(alternateBubbles[a])
				orgLayer.opacity = 1
				
				alternateBubbles[a].animate
					properties:
						midX: circleCoord.x
						midY: circleCoord.y
						scale: 1
						opacity: 1
					time: 0.3
					delay: 1
				
				alternateText = new TextLayer
					superLayer: alternateBubbles[a]
					autoSizeHeight: true
					textTransform: "capitalize"
					width: 110
					padding: 30
					lineHeight: 1.1
					fontSize: bubbleSize/6
					fontFamily: "CircularStd-Bold"
					text: alternateArray[a]["name"]
					color: "white"
					textAlign: "center"
					setup: true
				alternateText.center()
				

createText = () ->
	for t in [0...suggestionsArray.length]
			do (t)->
				foodstrings[t] = new TextLayer
					superLayer: bubbles[t]
					name: "ingredientString:" + t
					autoSizeHeight: true
					textTransform: "capitalize"
					width: 100
					padding: 30
					lineHeight: 1.1
					fontSize: positionsArray[t][2]/3
					fontFamily: "CircularStd-Bold"
					text: suggestionsArray[t]["name"]
					color: "white"
					textAlign: "center"
# 					setup: true
				foodstrings[t].center()
	
resetBubbles = () ->
	for b in bubbles
		b.destroy()
	for t in foodstrings
		t.destroy()
	bubbles = []
	foodstrings = []
	createBubbles()
	createText()
	
flyoutBubbles = () ->
	for b in bubbles
		b.animate
			properties:
				y: -200

# Övriga knappar ---------------
reset = new Layer
	backgroundColor: "rgba(255,102,102,1)"
	width: bubbleSize/2
	height: bubbleSize/2
	x: fwidth+100
	y: fheight-100
	borderRadius: bubbleSize
	scale: 0.1

plus_white = new Layer
	width: bubbleSize/5
	height: bubbleSize/5
	superLayer: reset
	image: "images/plus - white.png"
plus_white.center()

reset.states.add
	show:
		x: Align.right(-100)
		maxY: fheight-100
		rotation: 45
		scale: 1

done=null
launchDone = () ->
	done = new Layer
		superLayer: chosenCollector
# 		index: 1
		z: 10
		width: standardSize*2
		height: standardSize*2
		backgroundColor: green
		borderRadius: 500
		scale: 0.1
	done.center()

	checkIcon = new Layer
		superLayer: done
		width: done.width/2.5
		height: done.width/2.5
		image: "images/check3 - white.png"
	checkIcon.center()
		
# 	done.animate
# 		properties: 
# 			scale: 1
# 		curve: "spring(880, 47, 0)"

	done.states.add
		show:
			scale: 1
			width: standardSize*2
			height: standardSize*2
			backgroundColor: green
			borderRadius: 500
			x: Align.center
			y: Align.center
		done:
			midX: screenReferenceLayer.midX
			maxY: fheight - 100
			scale: 1.3
# 			borderWidth: 50
# 			borderColor: "white"
		recipe:
			midX: screenReferenceLayer.midX
			y: fheight+500
	
	done.states.animationOptions = 
		curve: "spring(880, 47, 0)"
	done.states.switch("show")
	done.states.animationOptions = 
		time:1
	
	done.onClick ->
		yesipe_test1.put("/done", true)
		
		if done.states.current is "show"
			done.superLayer = screenReferenceLayer
			done.midX = chosenCollector.midX
			done.midY = chosenCollector.midY
			done.states.switch("done")
			launchRecipe()
			for b in bubblesChosen
				b.states.switch("done")
			
		else
			i = recipePage.horizontalPageIndex(recipePage.currentPage)
			
			done.states.switch("recipe")
			recipePage.states.switch("recipe")
			recipePic[i].states.switch("recipe")
			recipeInfo[i].states.switch("final")
			for r in recipeTitle
				r.states.switch("recipe")
			for b in bubblesChosen
				b.states.switch("recipe")
			for i in extraIngredient
				i.states.switch("recipe")
			done.placeBefore()
			
		reset.states.switch("default")
		chosenCollector.states.switch("default")
# 		chosenCollector.states.switch("recipe")
		searchBar.states.switch("default")
			
		flyoutBubbles()
	
	done.onLongPress ->
		yesipe_test1.put("/done", false)
		if done.states.current is "done"
# 			done.states.switch("default")
# 			done.scale = 1
# 			done.center()
# 			recipePage.states.switch("default")
			recipePage.animate
				properties:
					y:2000
			Utils.delay 0.5, ->
				chosenCollector.states.switch("show")
				searchBar.states.switch("onscreen")
				for b in bubblesChosen
					b.states.switch("selected")
				resetBubbles()
				reset.states.switch("show")
	# 			done.superLayer = chosenCollector
	# 			done.states.switch("show")
				done.animate
					properties:
						midX: bubbleSize-100
						midY: fheight-bubbleSize+100
						scale: 1
					time: 1
				Utils.delay 2, ->
	# 				done.midX = chosenCollector.midX
	# 				done.midY = chosenCollector.midY
					done.superLayer = chosenCollector
					done.states.switchInstant("show")
# 					nullobject.destroy()
					recipePage.destroy()

recipePage=null
recipe = []
# recipeArray = []
recipesArray = []
recipeInfo = []
recipeInfoText = []
recipePic = []
recipeTitle = []
extraIngredient = []
extraIngredientText = []
instructionScroll = []
recipeInstructions = []

launchRecipe = () ->
# 	yesipe_test1.onChange "/recipe", (recipe) ->
# 		tempArray = _.toArray (recipe)
# 		recipeArray = tempArray

		yesipe_test1.onChange "/recipes", (rec) ->
			tempArray = _.toArray (rec)
			recipesArray = tempArray
		
# 	Utils.delay 2.5, -> 	
# 		Utils.delay 1.5, -> 
			picSize =  fwidth * 0.85
		
			recipePage = new PageComponent
				parent: screenReferenceLayer
				backgroundColor: null
				y: fheight
				height: fheight+500+standardSize*2
				width: fwidth
				clip: false
				scrollVertical: false
			recipePage.states.add
				onscreen:
					y: fheight-(picSize+standardSize*2)
				recipe:
					y: -(500+standardSize*2)
			
# 			nullobject = new Layer
# 				parent:recipePage.content
# 				visible: false
				
			fadeInstructions = new Layer
				superLayer: recipePage
				backgroundColor: "rgba(255,255,255,0)"
				width: Screen.width
				height: 120
				maxY: recipePage.height
				z: 1
			makeGradientModule.linear(fadeInstructions, ["rgba(255,255,255,0)","white"])
			
			for r in [0...recipesArray.length]
				do (r)->
					recipe[r] = new Layer
						superLayer: recipePage.content
						x: fwidth*r
						width: fwidth
						backgroundColor: null
						
					recipeInfo[r]=new Layer
						name:"recipeInfo"+r
						superLayer: recipe[r]
						width: fwidth*0.55
						height: fwidth*0.25
						backgroundColor: null
						borderWidth:10
						borderColor:"grey"
						y:50
						x: Align.center
						opacity:1
					recipeInfo[r].states.add
						final:
							opacity:0
					
					recipeInfoText[r] = new TextLayer
						superLayer: recipeInfo[r]
						width: recipeInfo[r].width
						autoSizeHeight:true
						name:"recipeInfoText"+r
						fontSize: standardSize/2
						text: "tid: "+ recipesArray[r]["cooking_time"]+  "\n" + recipesArray[r]["score"] + " / " + recipesArray[r]["ingredients"].length + " ingredienser"
						fontFamily: "CircularStd-Bold"
						color: "grey"
						textAlign: "center"
	# 					setup:true
					recipeInfoText[r].center()
						
					recipePic[r] = new Layer
						name:"recipePic"+r
						superLayer: recipe[r]
						x: Align.center
						y: 150+standardSize*2
						backgroundColor: beige
						width: picSize
						height: picSize
						borderRadius: picSize
						image: recipesArray[r]["image"]
			# 			borderWidth: 5
			# 			borderColor: green
					recipePic[r].states.add
						recipe:
							y: -picSize/3+500+standardSize*2
							scale: 1.3
					
					recipePic[r].onDoubleTap ->
						if done.states.current is "recipe"
							for i in instructionScroll
								i.scrollToTop()
							done.states.switch("done")
							recipePage.states.switch("onscreen")
							for r in recipeInfo
								r.states.switch("default")
							for r in recipePic
								r.states.switch("default")
							for r in recipeTitle
								r.states.switch("done")
							for b in bubblesChosen
								b.states.switch("done")
							for i in extraIngredient
								i.states.switch("onscreen")
	# 						recipePic[r].ignoreEvents = true
	# 				recipePic[r].ignoreEvents = true
						
					recipeTitle[r] = new TextLayer
						name:"recipeTitle"+r
						backgroundColor: "rgba(255,255,255,0.7)"
						padding: 20
						superLayer: recipe[r]
						y: 150+(standardSize*2)+10
						x: Align.center(-50)
						width: recipe[r].width-170
						text: recipesArray[r]["title"]
						fontSize: fwidth/10
						autoSizeHeight: true
						lineHeight: 0.9
						fontFamily: "CircularStd-Bold"
						color: green
						textAlign: "left"
						setup: false
					recipeTitle[r].states.add
						recipe:
							y: 500+70+standardSize*2
						done:
							y: 150+standardSize*2+20
					
					instructionScroll[r] = new ScrollComponent
						name: "instructionScroll"+r
						superLayer: recipe[r]
						width: fwidth*0.8
						height: fheight-picSize
						y: picSize + 500+standardSize*2
						x: Align.center
						scrollHorizontal: false
					instructionScroll[r].onScroll ->
						recipePage.scroll=false
					instructionScroll[r].onScrollEnd ->
						if recipePage.states.current is "onscreen"
							recipePage.scrollHorizontal = true
						
					recipeInstructions[r] = new TextLayer
						name: "recipeInstructions"+r
						superLayer: instructionScroll[r].content
						width: instructionScroll[r].width
						height: fheight*1.3
			# 			autoSizeHeight: true
						text: recipesArray[r]["instructions"]
						color: "black"
						fontSize: fwidth/25
						lineHeight: 1.5
			# 			setup:true

			recipePage.states.switch("onscreen")
				
			recipePage.on Events.AnimationEnd, ->
				if recipePage.states.current is "recipe"
					recipePage.scroll = false
				if recipePage.states.current is "onscreen"
					recipePage.scrollHorizontal = true
					
searchBar = new Layer
	x: Align.center
	y: -250
	width: fwidth * 0.9
	height: standardSize*1.5
	borderRadius: 300
	backgroundColor: "rgba(125,125,125,1)"
# 	opacity: 0.5
	
searchBar.states.add
	onscreen: 
		x: Align.center
		y: standardSize/2
# 		backgroundColor: "rgba(120,120,120,1)"
# 		opacity: 0.5
	focus:
		y: standardSize*2
# 		backgroundColor: "rgba(125,125,125,1)"
# 		opacity: 1

searchInput = new TextLayer
	parent: searchBar
	x: Align.left(standardSize/3)
	text: "Något särskilt du söker?"
	fontSize: searchBar.height/2.5
	fontFamily: "CircularStd-Medium"
	color: "White"
	setup: false
	autoSize: true
	padding: 20
	contentEditable: true
searchInput.centerY()
	
searchIcon = new Layer
	superLayer: searchBar
	x: Align.right(-standardSize*1.5)
	width: searchBar.height/2
	height: searchBar.height/2
	image: "images/search - white.png"
searchIcon.centerY()

# Events + Firebase --------------------
	
reset.onClick ->
	yesipe_test1.put("/done", false)
	yesipe_test1.put("/clear", true)
	Utils.delay 1, ->
		 yesipe_test1.put("/clear", false)
	
	chosenCollector.states.switch("default")
	reset.states.switch("default")
	searchBar.states.switch("onscreen")
	searchInput.text = "Något särskilt du söker?"
	
	flyoutBubbles()
	
	Utils.delay 0.5, ->
		 resetBubbles()
	
	for b in bubblesChosen
		b.states.switch("reset")
	
	Utils.delay 2, ->
		for b in bubblesChosen
			b.destroy()
			
	Utils.delay 3, ->
		done.destroy()
		bubblesChosen = []
	
searchBar.onDoubleTap ->
	scroll.scrollPoint = 
		x: spacerForScroll.width/2
		y: spacerForScroll.height/2
	flyoutBubbles()
	reset.states.switch("show")
	searchBar.states.switch("focus")
	screenReferenceLayer.ignoreEvents = false
		
screenReferenceLayer.onDoubleTap ->
	if searchBar.states.current is "focus"
		searchBar.states.switch("onscreen")
		screenReferenceLayer.ignoreEvents = true
		resetBubbles()
		reset.states.switch("default")
	
screenReferenceLayer.ignoreEvents = true
	
searchIcon.onClick ->
	yesipe_test1.put("/search", searchInput.text)

YESipe_logo.onTap ->	
	YESipe_logo.animate
		properties: 
			y: 4000
	
	searchBar.states.switch("onscreen")
# 	yesipe_test1.onChange "/suggestions", ->
	createBubbles()
	createText()