bkg = new BackgroundLayer
	backgroundColor: "white"
	
scroll = new ScrollComponent
	width: Screen.width
	height: Screen.height

scrollSpacer = new Layer
	backgroundColor:"null"
	width: Screen.width*3
	height: Screen.height*3
	superLayer: scroll.content
	
screenRef = new Layer
	width: Screen.width
	height: Screen.height
	backgroundColor:"null"

numberOfSel=0

class circleLayer extends Layer
	constructor: (options) ->
		super _.defaults options,
			superLayer:scroll.content
			width:300
			height:300
			borderRadius:200
			backgroundColor:"green"
		@state = "standard"
		
# 		@onTap ->
# 			if @state is "2"
# 				@destroy()
# 				numberOfSel = numberOfSel-1
# 				
# 			if @state is "selected"
# 				@remove()
# 				@state = "2"
# 			
# 			if @state is "standard"
# 				@selected()
# 				numberOfSel = numberOfSel+1
# 				@state = "selected"

		@onTap ->
			if @state is "2"
				@destroy()
				numberOfSel = numberOfSel-1
				
			if @state is "selected"
				@remove()
				@state = "2"
			
			if @state is "standard"
				selectBubble(@)	
	selected: ->
		@backgroundColor = "red"
		@scale = 0.8
		@superLayer = screenRef
		@x = Align.left(100*numberOfSel)
		@y = Align.bottom
# 		@ignoreEvents = true
	remove: ->
# 		@backgroundColor = "green"
		@html = "X"
		@opacity = 0.5
# 		@x = Align.left
# 		@y = Align.top

positions=[[330,200,"whatis"],[302,840,"where"],[500,500,"well"],[200,1400,"hello"],[1500,400,"whatnot"]]

selectBubble = (layer) ->
	tempX=layer.x
	tempY=layer.y
	layer.superLayer = screenRef
	scaleFactor = (1/layer.width)
	tempWidth = layer.width
	tempHeight = layer.height
	layer.x = tempX - scroll.scrollX
	layer.y = tempY - scroll.scrollY


	layer.animate
		properties:
			backgroundColor: "red"
			scale: 0.8
			x: 200*numberOfSel
			y: Align.bottom

for a in [0...positions.length]
	bubble = new circleLayer
		name: "bubble#{a}"
		midX:positions[a][0]
		midY:positions[a][1]
		html:positions[a][2]
		style:
			color: "white"
			textAlign: "center"
			lineHeight: "290px"
			fontWeight: "900"
			fontSize: "50px"
