#region imports
from GraphicsView_GUI import Ui_Form
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw
import math
import sys
import numpy as np
import scipy as sp
from scipy import optimize
#endregion

#region class definitions
class RigidLink(qtw.QGraphicsItem):
    def __init__(self, stX, stY, enX, enY, radius=10, parent=None, pen=None, brush=None, name='RigidLink', width=1.0, thickness=0.5, material='Steel'):
        super().__init__(parent)
        self.pen = pen
        self.brush = brush
        self.name = name
        self.startX = stX
        self.startY = stY
        self.endX = enX
        self.endY = enY
        self.radius = radius
        self.width = width
        self.thickness = thickness
        self.material = material
        self.weight = 0.0
        self.angle = self.linkAngle()
        self.rect = qtc.QRectF(-self.radius, -self.radius, self.length + self.radius, self.radius)
        self.transform = qtg.QTransform()
        self.transform.reset()

    def boundingRect(self):
        boundingRect = self.transform.mapRect(self.rect)
        return boundingRect

    def deltaY(self):
        self.DY = self.endY - self.startY
        return self.DY

    def deltaX(self):
        self.DX = self.endX - self.startX
        return self.DX

    def linkLength(self):
        self.length = math.sqrt(math.pow(self.deltaX(), 2) + math.pow(self.deltaY(), 2))
        return self.length

    def linkAngle(self):
        self.linkLength()
        if self.length == 0.0:
            self.angle = 0
        else:
            self.angle = math.acos(self.DX / self.length)
            self.angle *= -1 if (self.DY > 0) else 1
        return self.angle

    def paint(self, painter, option, widget=None):
        path = qtg.QPainterPath()
        len = self.linkLength()
        angLink = self.linkAngle() * 180 / math.pi
        rectSt = qtc.QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)
        rectEn = qtc.QRectF(self.length - self.radius, -self.radius, 2 * self.radius, 2 * self.radius)
        centerLinePen = qtg.QPen()
        centerLinePen.setStyle(qtc.Qt.DashDotLine)
        r, g, b, a = self.pen.color().getRgb()
        centerLinePen.setColor(qtg.QColor(r, g, b, 128))
        centerLinePen.setWidth(1)
        p1 = qtc.QPointF(0, 0)
        p2 = qtc.QPointF(len, 0)
        painter.setPen(centerLinePen)
        painter.drawLine(p1, p2)
        path.arcMoveTo(rectSt, 90)
        path.arcTo(rectSt, 90, 180)
        path.lineTo(self.length, self.radius)
        path.arcMoveTo(rectEn, 270)
        path.arcTo(rectEn, 270, 180)
        path.lineTo(0, -self.radius)
        if self.pen is not None:
            painter.setPen(self.pen)
        if self.brush is not None:
            painter.setBrush(self.brush)
        painter.drawPath(path)
        pivotStart = qtc.QRectF(-self.radius / 6, -self.radius / 6, self.radius / 3, self.radius / 3)
        pivotEnd = qtc.QRectF(self.length - self.radius / 6, -self.radius / 6, self.radius / 3, self.radius / 3)
        painter.drawEllipse(pivotStart)
        painter.drawEllipse(pivotEnd)
        self.rect = qtc.QRectF(-self.radius, -self.radius, self.length + 2 * self.radius, 2 * self.radius)
        self.transform.reset()
        self.transform.translate(self.startX, self.startY)
        self.transform.rotate(-angLink)
        self.setTransform(self.transform)
        self.transform.reset()
        stTT = (f"link: {self.name}\n"
                f"start: ({self.startX:.3f}, {self.startY:.3f})\n"
                f"end: ({self.endX:.3f}, {self.endY:.3f})\n"
                f"length: {self.length:.3f}\n"
                f"angle: {self.angle * 180 / math.pi:.3f}\n"
                f"width: {self.width:.3f}\n"
                f"thickness: {self.thickness:.3f}\n"
                f"material: {self.material}\n"
                f"weight: {self.weight:.2f} lb")
        self.setToolTip(stTT)

class RigidPivotPoint(qtw.QGraphicsItem):
    def __init__(self, ptX, ptY, pivotHeight, pivotWidth, parent=None, pen=None, brush=None, rotation=0, name='RigidPivotPoint', support_type='pin'):
        super().__init__(parent)
        self.x = ptX
        self.y = ptY
        self.pen = pen
        self.brush = brush
        self.height = pivotHeight
        self.width = pivotWidth
        self.radius = min(self.height, self.width) / 4
        self.rect = qtc.QRectF(self.x - self.width / 2, self.y - self.radius, self.width, self.height + self.radius)
        self.rotationAngle = rotation
        self.name = name
        self.support_type = support_type
        self.load = 0.0
        self.transformation = qtg.QTransform()
        self.updateTooltip()

    def updateTooltip(self):
        self.setToolTip(f"Node: {self.name}\nx={self.x:.3f}, y={self.y:.3f}\nSupport: {self.support_type}\nLoad: {self.load:.2f} lb")

    def boundingRect(self):
        bounding_rect = self.transformation.mapRect(self.rect)
        return bounding_rect

    def rotate(self, angle):
        self.rotationAngle = angle

    def paint(self, painter, option, widget=None):
        path = qtg.QPainterPath()
        radius = min(self.height, self.width) / 2
        H = math.sqrt((self.width / 2) ** 2 + self.height ** 2)
        phi = math.asin(radius / H)
        theta = math.asin(self.height / H)
        ang = math.pi - phi - theta
        l = H * math.cos(phi)

        x1 = self.width / 2
        y1 = self.height
        path.moveTo(x1, y1)
        x2 = l * math.cos(ang)
        y2 = l * math.sin(ang)
        path.lineTo(x1 + x2, y1 - y2)
        pivotRect = qtc.QRectF(-radius, -radius, 2 * radius, 2 * radius)
        stAng = math.pi / 2 - phi - theta
        spanAng = math.pi - 2 * stAng
        path.arcTo(pivotRect, stAng * 180 / math.pi, spanAng * 180 / math.pi)
        x4 = -self.width / 2
        y4 = self.height
        path.lineTo(x4, y4)

        if self.pen is not None:
            painter.setPen(self.pen)
        if self.brush is not None:
            painter.setBrush(self.brush)
        painter.drawPath(path)

        pivotPtRect = qtc.QRectF(-radius / 4, -radius / 4, radius / 2, radius / 2)
        painter.drawEllipse(pivotPtRect)
        x5 = -self.width
        x6 = self.width
        painter.drawLine(x5, y4, x6, y4)
        penOutline = qtg.QPen(qtc.Qt.NoPen)
        hatchbrush = qtg.QBrush(qtc.Qt.BDiagPattern)
        painter.setPen(penOutline)
        painter.setBrush(hatchbrush)
        support = qtc.QRectF(x5, y4, self.width * 2, self.height)
        painter.drawRect(support)

        self.rect = qtc.QRectF(-self.width, -self.radius, self.width * 2, self.height * 2 + self.radius)
        self.transformation.reset()
        self.transformation.translate(self.x, self.y)
        self.transformation.rotate(self.rotationAngle)
        self.setTransform(self.transformation)
        self.updateTooltip()

class MainWindow(Ui_Form, qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setupGraphics()
        self.gv_Main.setMouseTracking(True)
        self.pushButton.setMouseTracking(True)
        self.setMouseTracking(True)
        self.buildScene()
        self.prevAlpha = 0
        self.prevBeta = 0
        self.angle1 = math.pi
        self.angle2 = math.pi
        self.spnd_Zoom.valueChanged.connect(self.setZoom)
        self.pushButton.clicked.connect(self.pickAColor)
        self.scene.installEventFilter(self)
        self.mouseDown = False
        self.show()

    def setupGraphics(self):
        self.scene = qtw.QGraphicsScene()
        self.scene.setObjectName("MyScene")
        self.scene.setSceneRect(-200, -200, 400, 400)
        self.gv_Main.setScene(self.scene)
        self.setupPensAndBrushes()

    def setupPensAndBrushes(self):
        self.penThick = qtg.QPen(qtc.Qt.darkGreen)
        self.penThick.setWidth(5)
        self.penMed = qtg.QPen(qtc.Qt.darkBlue)
        self.penMed.setStyle(qtc.Qt.SolidLine)
        self.penMed.setWidth(2)
        self.penLink = qtg.QPen(qtg.QColor("orange"))
        self.penLink.setWidth(1)
        self.penGridLines = qtg.QPen()
        self.penGridLines.setWidth(1)
        self.penGridLines.setColor(qtg.QColor.fromHsv(197, 144, 228, 128))
        self.brushFill = qtg.QBrush(qtc.Qt.darkRed)
        self.brushHatch = qtg.QBrush()
        self.brushHatch.setStyle(qtc.Qt.DiagCrossPattern)
        self.brushGrid = qtg.QBrush(qtg.QColor.fromHsv(87, 98, 245, 128))
        self.brushLink = qtg.QBrush(qtg.QColor.fromHsv(35, 255, 255, 64))
        self.brushPivot = qtg.QBrush(qtg.QColor.fromHsv(0, 0, 128, 255))

    def mouseMoveEvent(self, a0: qtg.QMouseEvent):
        w = app.widgetAt(a0.globalPos())
        if w is None:
            name = 'none'
        else:
            name = w.objectName()
        self.setWindowTitle(str(a0.x()) + ',' + str(a0.y()) + name)

    def eventFilter(self, obj, event):
        if obj == self.scene:
            et = event.type()
            if event.type() == qtc.QEvent.GraphicsSceneMouseMove:
                w = app.topLevelAt(event.screenPos())
                screenPos = event.screenPos()
                scenePos = event.scenePos()
                strScreen = "screen x = {}, screen y = {}".format(screenPos.x(), screenPos.y())
                strScene = ":  scene x = {}, scene y = {}".format(scenePos.x(), scenePos.y())
                self.setWindowTitle(strScreen + strScene)
                if self.mouseDown:
                    l1 = self.link1.linkLength()
                    l2 = self.link2.linkLength()
                    l3 = self.link3.linkLength()
                    scenePos = event.scenePos()
                    x = scenePos.x()
                    y = scenePos.y()
                    if x == self.link1.startX:
                        self.angle1 = math.pi / 2 if y <= self.link1.startY else math.pi * 3.0 / 2.0
                    else:
                        self.angle1 = math.atan(-(y - self.link1.startY) / (x - self.link1.startX))
                        self.angle1 += math.pi if x < self.link1.startX else 0
                    if self.link3.endX == self.link3.startX:
                        self.angle2 = math.pi / 2 if self.link3.endY <= self.link3.startY else math.pi * 3.0 / 2.0
                    else:
                        self.angle2 = math.atan(-(self.link3.endY - self.link2.startY) / (self.link3.endX - self.link3.startX))
                        self.angle2 += math.pi if self.link3.endX < self.link3.startX else 0
                    self.link1.endX = self.link1.startX + math.cos(self.angle1) * l1
                    self.link1.endY = self.link1.startY - math.sin(self.angle1) * l1
                    x1 = self.link1.endX
                    y1 = self.link1.endY
                    self.lTest = l2
                    def fn1(angle2):
                        # Extract scalar value from angle2
                        angle2_scalar = angle2.item() if isinstance(angle2, np.ndarray) and angle2.size == 1 else float(angle2[0]) if isinstance(angle2, (np.ndarray, list)) else angle2
                        x2 = self.link3.startX + l3 * math.cos(angle2_scalar)
                        y2 = self.link3.startY - l3 * math.sin(angle2_scalar)
                        self.lTest = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                        return l2 - self.lTest
                    # Pass a scalar initial guess to fsolve
                    result = optimize.fsolve(fn1, self.angle2)
                    # Extract the scalar value from the result
                    result_scalar = float(result[0]) if isinstance(result, np.ndarray) else result
                    if abs(self.lTest - l2) > 0.001:
                        self.angle2 = self.prevBeta
                        self.angle1 = self.prevAlpha
                        self.link1.endX = self.link1.startX + math.cos(self.angle1) * l1
                        self.link1.endY = self.link1.startY - math.sin(self.angle1) * l1
                    else:
                        self.angle2 = result_scalar
                        self.prevAlpha = self.angle1
                        self.prevBeta = self.angle2
                    self.link3.endX = self.link3.startX + l3 * math.cos(self.angle2)
                    self.link3.endY = self.link3.startY - l3 * math.sin(self.angle2)
                    self.link2.startX = self.link1.endX
                    self.link2.startY = self.link1.endY
                    self.link2.endX = self.link3.endX
                    self.link2.endY = self.link3.endY
                    len2 = self.link2.linkLength()
                    self.scene.update()
            if event.type() == qtc.QEvent.GraphicsSceneWheel:
                if event.delta() > 0:
                    self.spnd_Zoom.stepUp()
                else:
                    self.spnd_Zoom.stepDown()
            if event.type() == qtc.QEvent.GraphicsSceneMousePress:
                if event.button() == qtc.Qt.LeftButton:
                    self.mouseDown = True
            if event.type() == qtc.QEvent.GraphicsSceneMouseRelease:
                self.mouseDown = False
        return super(MainWindow, self).eventFilter(obj, event)

    def buildScene(self):
        self.scene.clear()
        self.drawAGrid(DeltaX=10, DeltaY=10, Height=400, Width=400, Pen=self.penGridLines, Brush=self.brushGrid)
        brush = qtg.QBrush()
        brush.setStyle(qtc.Qt.BDiagPattern)
        self.pivot0 = self.drawPivot(-100, 0, 10, 20)
        self.pivot0.setTransformOriginPoint(qtc.QPointF(self.pivot0.x, self.pivot0.y))
        self.pivot0.rotate(90)
        self.pivot1 = self.drawPivot(60, -30, 10, 20)
        self.pivot1.setTransformOriginPoint(qtc.QPointF(self.pivot1.x, self.pivot1.y))
        self.pivot1.rotate(-90)
        self.link0 = self.drawLinkage(self.pivot0.x, self.pivot0.y, self.pivot1.x, self.pivot1.y, radius=5, pen=self.penGridLines, brush=self.brushGrid)
        self.link1 = self.drawLinkage(-100, 0, -100, -60, 5)
        self.link2 = self.drawLinkage(-100, -60, 100, -150, 5)
        self.link3 = self.drawLinkage(60, -30, 100, -150, 5)

    def drawAGrid(self, DeltaX=10, DeltaY=10, Height=200, Width=200, CenterX=0, CenterY=0, Pen=None, Brush=None, SubGrid=None):
        height = self.scene.sceneRect().height() if Height is None else Height
        width = self.scene.sceneRect().width() if Width is None else Width
        left = self.scene.sceneRect().left() if CenterX is None else (CenterX - width / 2.0)
        right = self.scene.sceneRect().right() if CenterX is None else (CenterX + width / 2.0)
        top = self.scene.sceneRect().top() if CenterY is None else (CenterY - height / 2.0)
        bottom = self.scene.sceneRect().bottom() if CenterY is None else (CenterY + height / 2.0)
        Dx = DeltaX
        Dy = DeltaY
        pen = qtg.QPen() if Pen is None else Pen
        if Brush is not None:
            rect = self.drawARectangle(left, top, width, height)
            rect.setBrush(Brush)
            rect.setPen(pen)
        x = left
        while x <= right:
            lVert = self.drawALine(x, top, x, bottom)
            lVert.setPen(pen)
            x += Dx
        y = top
        while y <= bottom:
            lHor = self.drawALine(left, y, right, y)
            lHor.setPen(pen)
            y += Dy

    def drawARectangle(self, leftX, topY, widthX, heightY, pen=None, brush=None):
        rect = qtw.QGraphicsRectItem(leftX, topY, widthX, heightY)
        if brush is not None:
            rect.setBrush(brush)
        if pen is not None:
            rect.setPen(pen)
        self.scene.addItem(rect)
        return rect

    def drawALine(self, stX, stY, enX, enY, pen=None):
        if pen is None:
            pen = self.penMed
        line = qtw.QGraphicsLineItem(stX, stY, enX, enY)
        line.setPen(pen)
        self.scene.addItem(line)
        return line

    def polarToRect(self, centerX, centerY, radius, angleDeg=0):
        angleRad = angleDeg * 2.0 * math.pi / 360.0
        return centerX + radius * math.cos(angleRad), centerY + radius * math.sin(angleRad)

    def drawACircle(self, centerX, centerY, Radius, angle=0, brush=None, pen=None):
        ellipse = qtw.QGraphicsEllipseItem(centerX - Radius, centerY - Radius, 2 * Radius, 2 * Radius)
        if pen is not None:
            ellipse.setPen(pen)
        if brush is not None:
            ellipse.setBrush(brush)
        self.scene.addItem(ellipse)
        return ellipse

    def drawASquare(self, centerX, centerY, Size, brush=None, pen=None):
        sqr = qtw.QGraphicsRectItem(centerX - Size / 2.0, centerY - Size / 2.0, Size, Size)
        if pen is not None:
            sqr.setPen(pen)
        if brush is not None:
            sqr.setBrush(brush)
        self.scene.addItem(sqr)
        return sqr

    def drawATriangle(self, centerX, centerY, Radius, angleDeg=0, brush=None, pen=None):
        pts = []
        x, y = self.polarToRect(centerX, centerY, Radius, 0 + angleDeg)
        pts.append(qtc.QPointF(x, y))
        x, y = self.polarToRect(centerX, centerY, Radius, 120 + angleDeg)
        pts.append(qtc.QPointF(x, y))
        x, y = self.polarToRect(centerX, centerY, Radius, 240 + angleDeg)
        pts.append(qtc.QPointF(x, y))
        x, y = self.polarToRect(centerX, centerY, Radius, 0 + angleDeg)
        pts.append(qtc.QPointF(x, y))
        pg = qtg.QPolygonF(pts)
        PG = qtw.QGraphicsPolygonItem(pg)
        if pen is not None:
            PG.setPen(pen)
        if brush is not None:
            PG.setBrush(brush)
        self.scene.addItem(PG)
        return PG

    def drawAnArrow(self, startX, startY, endX, endY, pen=None, brush=None):
        line = qtw.QGraphicsLineItem(startX, startY, endX, endY)
        p = qtg.QPen() if pen is None else pen
        line.setPen(pen)
        angleDeg = 180.0 / math.pi * math.atan((endY - startY) / (endX - startX))
        self.scene.addItem(line)
        self.drawATriangle(endX, endY, 5, angleDeg=angleDeg, pen=pen, brush=brush)

    def drawRigidSurface(self, centerX, centerY, Width=10, Height=3, pen=None, brush=None):
        top = centerY
        left = centerX - Width / 2
        right = centerX + Width / 2
        self.drawALine(centerX - Width / 2, centerY, centerX + Width / 2, centerY, pen=pen)
        penOutline = qtg.QPen(qtc.Qt.NoPen)
        self.drawARectangle(left, top, Width, Height, pen=penOutline, brush=brush)

    def drawLinkage(self, stX, stY, enX, enY, radius=10, pen=None, brush=None):
        if pen is None:
            pen = self.penLink
        if brush is None:
            brush = self.brushLink
        lin1 = RigidLink(stX, stY, enX, enY, radius, pen=pen, brush=brush)
        self.scene.addItem(lin1)
        return lin1

    def drawPivot(self, x, y, ht, wd):
        pivot = RigidPivotPoint(x, y, ht, wd, brush=self.brushPivot)
        self.scene.addItem(pivot)
        return pivot

    def pickAColor(self):
        cdb = qtw.QColorDialog(self)
        c = cdb.getColor()
        hsv = c.getHsv()
        self.pushButton.setText(str(hsv))
        self.penGridLines.setColor(qtg.QColor.fromHsv(hsv[0], hsv[1], hsv[2], hsv[3]))
        self.buildScene()

    def setZoom(self):
        self.gv_Main.resetTransform()
        self.gv_Main.scale(self.spnd_Zoom.value(), self.spnd_Zoom.value())
#endregion

#region function calls
if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    mw.setWindowTitle('GraphicsView')
    sys.exit(app.exec())
#endregion