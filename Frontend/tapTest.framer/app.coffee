layerA = new Layer
	x: 61
	y: 92
	{count:0}

layerB = new Layer
	x: 375
	y: 350
	layerC = {count:0}
	
boxes = [layerA, layerB]
print layerC.count
	
for hola in boxes
	do (hola)->
	
		hola.onTap ->
			hola.count++
			print hola.count
		
		# 	print "X"+layerA.x
		# 	layerA.ignoreEvents = true
			if tapCount.count is 1
				firstTap(hola)
			else
				secondTap(hola)

firstTap = (layer) ->
	print layer
	print "first"
	layer.x=layer.x+20

secondTap = (layer) ->
	print layer
	print "second"
	layer.y=layer.y+20