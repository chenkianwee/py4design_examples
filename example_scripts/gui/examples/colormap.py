import pyqtgraph as pq

pos = [0,1]
c = [(1,1,1), (0,0,0)]
cmap = pq.ColorMap(pos, c)
lut = cmap.getLookupTable(alpha=False)
print lut
img = pq.ImageItem()
img.setLookupTable(lut)
img.setLevels([0,1])        

plot = pq.plot(title = "test");
plot.addItem(img)

#self.timer = QtCore.QTimer()
#self.timer.timeout.connect(self.check_for_new_data_and_replot)
#self.timer.start(100)
#img.setImage(data.T)
#self.win.show() 