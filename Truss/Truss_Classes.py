#region imports
import math
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from GraphicsView_App import RigidLink, RigidPivotPoint
#endregion

#region class definitions
class Position:
    def __init__(self, pos=None, x=None, y=None, z=None):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        if pos is not None:
            self.x, self.y, self.z = pos
        self.x = x if x is not None else self.x
        self.y = y if y is not None else self.y
        self.z = z if z is not None else self.z

    def __eq__(self, other):
        if self.x != other.x: return False
        if self.y != other.y: return False
        if self.z != other.z: return False
        return True

    def __add__(self, other):
        return Position((self.x + other.x, self.y + other.y, self.z + other.z))

    def __iadd__(self, other):
        if isinstance(other, (float, int)):
            self.x += other
            self.y += other
            self.z += other
            return self
        if isinstance(other, Position):
            self.x += other.x
            self.y += other.y
            self.z += other.z
            return self

    def __sub__(self, other):
        return Position((self.x - other.x, self.y - other.y, self.z - other.z))

    def __isub__(self, other):
        if isinstance(other, (float, int)):
            self.x -= other
            self.y -= other
            self.z -= other
            return self
        if isinstance(other, Position):
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
            return self

    def __mul__(self, other):
        if isinstance(other, (float, int)):
            return Position((self.x * other, self.y * other, self.z * other))
        if isinstance(other, Position):
            return Position((self.x * other.x, self.y * other.y, self.z * other.z))

    def __rmul__(self, other):
        return self * other

    def __imul__(self, other):
        if isinstance(other, (float, int)):
            self.x *= other
            self.y *= other
            self.z *= other
            return self

    def __truediv__(self, other):
        if isinstance(other, (float, int)):
            return Position((self.x / other, self.y / other, self.z / other))

    def __idiv__(self, other):
        if isinstance(other, (float, int)):
            self.x /= other
            self.y /= other
            self.z /= other
            return self

    def set(self, strXYZ=None, tupXYZ=None):
        if strXYZ is not None:
            cells = strXYZ.replace('(', '').replace(')', '').strip().split(',')
            x, y, z = float(cells[0]), float(cells[1]), float(cells[2])
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)
        elif tupXYZ is not None:
            x, y, z = tupXYZ
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)

    def getTup(self):
        return (self.x, self.y, self.z)

    def getStr(self, nPlaces=3):
        return '{}, {}, {}'.format(round(self.x, nPlaces), round(self.y, nPlaces), round(self.z, nPlaces))

    def mag(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    def normalize(self):
        l = self.mag()
        if l <= 0.0: return
        self.__idiv__(l)

    def getAngleRad(self):
        l = self.mag()
        if l <= 0.0: return 0
        if self.y >= 0.0:
            return math.acos(self.x / l)
        return 2.0 * math.pi - math.acos(self.x / l)

    def getAngleDeg(self):
        return 180.0 / math.pi * self.getAngleRad()

class Rectangle:
    def __init__(self, top=None, left=None, bottom=None, right=None):
        self.top = 0 if top is None else top
        self.left = 0 if left is None else left
        self.bottom = 0 if bottom is None else bottom
        self.right = 0 if right is None else right

    def height(self):
        return self.top - self.bottom

    def width(self):
        return self.right - self.left

    def centerY(self):
        return self.bottom + self.height() / 2.0

    def centerX(self):
        return self.left + self.width() / 2.0

class Material:
    def __init__(self, uts=None, ys=None, modulus=None, staticFactor=None):
        self.uts = uts
        self.ys = ys
        self.E = modulus
        self.staticFactor = staticFactor

class Node:
    def __init__(self, name=None, position=None):
        self.name = name
        self.position = position if position is not None else Position()
        support_type = 'pin' if name.lower() in ['left', 'right'] else 'none'
        self.support_type = support_type
        self.load = 0.0
        self.graphic = RigidPivotPoint(position.x, position.y, 10, 30, support_type=support_type)

    def __eq__(self, other):
        if self.name != other.name: return False
        if self.position != other.position: return False
        return True

class Link:
    def __init__(self, name="", node1="1", node2="2", length=None, angleRad=None, width=1.0, thickness=0.5, material="Steel"):
        self.name = name
        self.node1_Name = node1
        self.node2_Name = node2
        self.length = length
        self.angleRad = angleRad
        self.width = width
        self.thickness = thickness
        self.material = material
        self.weight = 0.0
        self.graphic = RigidLink(0, 0, 1, 1)
        self.graphic.name = name

    def __eq__(self, other):
        if self.node1_Name != other.node1_Name: return False
        if self.node2_Name != other.node2_Name: return False
        if self.length != other.length: return False
        if self.angleRad != other.angleRad: return False
        return True

    def set(self, node1=None, node2=None, length=None, angleRad=None, width=None, thickness=None, material=None):
        self.node1_Name = node1
        self.node2_Name = node2
        self.length = length
        self.angleRad = angleRad
        self.width = width if width is not None else self.width
        self.thickness = thickness if thickness is not None else self.thickness
        self.material = material if material is not None else self.material

class TrussModel:
    def __init__(self):
        self.title = None
        self.links = []
        self.nodes = []
        self.material = Material()
        self.rct = Rectangle()

    def getNode(self, name):
        for n in self.nodes:
            if n.name == name:
                return n

    def getCenterPt(self):
        rct = Rectangle()
        rct.left = self.nodes[0].position.x
        rct.right = self.nodes[0].position.x
        rct.top = self.nodes[0].position.y
        rct.bottom = self.nodes[0].position.y
        for n in self.nodes:
            if rct.left > n.position.x:
                rct.left = n.position.x
            if rct.right < n.position.x:
                rct.right = n.position.x
            if rct.top < n.position.y:
                rct.top = n.position.y
            if rct.bottom > n.position.y:
                rct.bottom = n.position.y
        self.rct = rct

    def compute_link_weights(self):
        densities = {'Steel': 0.284, 'Aluminum': 0.098}
        for link in self.links:
            length = link.length
            width = link.width
            thickness = link.thickness
            material = link.material
            density = densities.get(material, 0.284)
            volume = length * width * thickness
            link.weight = volume * density
            link.graphic.weight = link.weight
            if hasattr(link.graphic, 'setToolTip'):
                link.graphic.setToolTip(
                    f"link: {link.name}\n"
                    f"start: ({link.graphic.startX:.3f}, {link.graphic.startY:.3f})\n"
                    f"end: ({link.graphic.endX:.3f}, {link.graphic.endY:.3f})\n"
                    f"length: {link.length:.3f}\n"
                    f"angle: {link.angleRad * 180 / math.pi:.3f}\n"
                    f"width: {link.width:.3f}\n"
                    f"thickness: {link.thickness:.3f}\n"
                    f"material: {link.material}\n"
                    f"weight: {link.weight:.2f} lb"
                )

    def compute_support_loads(self):
        total_weight = sum(link.weight for link in self.links)
        left_load = total_weight / 2
        right_load = total_weight / 2
        for node in self.nodes:
            if node.name.lower() == 'left':
                node.load = left_load
                node.graphic.load = left_load
                node.graphic.updateTooltip()
            elif node.name.lower() == 'right':
                node.load = right_load
                node.graphic.load = right_load
                node.graphic.updateTooltip()

class TrussView:
    def __init__(self):
        self.scene = qtw.QGraphicsScene()
        self.le_LongLinkName = qtw.QLineEdit()
        self.le_LongLinkNode1 = qtw.QLineEdit()
        self.le_LongLinkNode2 = qtw.QLineEdit()
        self.le_LongLinkLength = qtw.QLineEdit()
        self.te_Report = qtw.QTextEdit()
        self.gv = qtw.QGraphicsView()

        self.penLink = qtg.QPen(qtg.QColor("orange"))
        self.penLink.setWidth(1)
        self.penNode = qtg.QPen(qtc.Qt.darkBlue)
        self.penNode.setStyle(qtc.Qt.SolidLine)
        self.penNode.setWidth(1)
        self.penLabel = qtg.QPen(qtc.Qt.darkMagenta)
        self.penLabel.setStyle(qtc.Qt.SolidLine)
        self.penLabel.setWidth(1)
        self.penGridLines = qtg.QPen()
        self.penGridLines.setWidth(1)
        self.penGridLines.setColor(qtg.QColor.fromHsv(197, 144, 228, alpha=50))
        self.brushLink = qtg.QBrush(qtg.QColor.fromHsv(35, 255, 255, 64))
        self.brushPivot = qtg.QBrush(qtg.QColor.fromRgb(215, 215, 215, alpha=128))
        self.brushFill = qtg.QBrush(qtc.Qt.darkRed)
        self.brushNode = qtg.QBrush(qtg.QColor.fromCmyk(0, 0, 255, 0, alpha=100))
        self.brushGrid = qtg.QBrush(qtg.QColor.fromHsv(87, 98, 245, alpha=128))

    def setDisplayWidgets(self, args):
        self.te_Report = args[0]
        self.le_LongLinkName = args[1]
        self.le_LongLinkNode1 = args[2]
        self.le_LongLinkNode2 = args[3]
        self.le_LongLinkLength = args[4]
        self.gv = args[5]
        self.gv.setScene(self.scene)

    def displayReport(self, truss=None):
        st = '\tTruss Design Report\n'
        st += 'Title:  {}\n'.format(truss.title)
        st += 'Static Factor of Safety:  {:0.2f}\n'.format(truss.material.staticFactor)
        st += 'Ultimate Strength:  {:0.2f} ksi\n'.format(truss.material.uts)
        st += 'Yield Strength:  {:0.2f} ksi\n'.format(truss.material.ys)
        st += 'Modulus of Elasticity:  {:0.2f} Mpsi\n'.format(truss.material.E)
        st += '_____________Link Summary________________\n'
        st += 'Link\tNode1\tNode2\tLength\tAngle\tWidth\tThickness\tMaterial\tWeight\n'
        longest = None
        for l in truss.links:
            if longest is None or l.length > longest.length:
                longest = l
            st += '{}\t{}\t{}\t{:0.2f}\t{:0.2f}\t{:0.2f}\t{:0.2f}\t{}\t{:0.2f}\n'.format(
                l.name, l.node1_Name, l.node2_Name, l.length, l.angleRad * 180 / math.pi,
                l.width, l.thickness, l.material, l.weight)
        st += '_____________Node Summary________________\n'
        st += 'Node\tX\tY\tSupport\tLoad\n'
        for n in truss.nodes:
            st += '{}\t{:0.2f}\t{:0.2f}\t{}\t{:0.2f}\n'.format(
                n.name, n.position.x, n.position.y, n.support_type, n.load)
        self.te_Report.setText(st)
        self.le_LongLinkName.setText(longest.name)
        self.le_LongLinkLength.setText("{:0.2f}".format(longest.length))
        self.le_LongLinkNode1.setText(longest.node1_Name)
        self.le_LongLinkNode2.setText(longest.node2_Name)

    def buildScene(self, truss=None):
        truss.getCenterPt()
        rct = truss.rct
        rct.left -= 50
        rct.right += 50
        rct.top += 50
        rct.bottom -= 50

        self.scene.clear()
        self.drawAGrid(DeltaX=10, DeltaY=10, Height=abs(rct.height()), Width=abs(rct.width()), CenterX=0, CenterY=0)
        self.drawLinks(truss=truss)
        self.drawNodes(truss=truss)

    def drawAGrid(self, DeltaX=10, DeltaY=10, Height=320, Width=180, CenterX=120, CenterY=60):
        Pen = self.penGridLines
        Brush = self.brushGrid
        height = self.scene.sceneRect().height() if Height is None else Height
        width = self.scene.sceneRect().width() if Width is None else Width
        left = self.scene.sceneRect().left() if CenterX is None else (CenterX - width / 2.0)
        right = self.scene.sceneRect().right() if CenterX is None else (CenterX + width / 2.0)
        top = -1.0 * self.scene.sceneRect().top() if CenterY is None else (CenterY - height / 2.0)
        bottom = -1.0 * self.scene.sceneRect().bottom() if CenterY is None else (CenterY + height / 2.0)
        Dx = DeltaX
        Dy = DeltaY
        pen = qtg.QPen() if Pen is None else Pen

        if Brush is not None:
            rect = qtw.QGraphicsRectItem(left, top, width, height)
            rect.setBrush(Brush)
            rect.setPen(pen)
            self.scene.addItem(rect)
        x = left
        while x <= right:
            lVert = qtw.QGraphicsLineItem(x, top, x, bottom)
            lVert.setPen(pen)
            self.scene.addItem(lVert)
            x += Dx
        y = bottom
        while y >= top:
            lHor = qtw.QGraphicsLineItem(left, y, right, y)
            lHor.setPen(pen)
            self.scene.addItem(lHor)
            y -= Dy

    def drawLinks(self, truss=None):
        scene = self.scene
        truss.getCenterPt()
        rct = truss.rct
        offset = Position(x=rct.centerX(), y=rct.centerY())
        penLink = self.penLink
        for l in truss.links:
            n1 = truss.getNode(l.node1_Name)
            n2 = truss.getNode(l.node2_Name)
            l.graphic = RigidLink(
                n1.position.x - offset.x, -(n1.position.y - offset.y),
                n2.position.x - offset.x, -(n2.position.y - offset.y),
                radius=3, pen=self.penLink, brush=self.brushLink,
                name="link name = " + l.name,
                width=l.width, thickness=l.thickness, material=l.material
            )
            l.graphic.setToolTip(f"link: {l.name}\n")
            scene.addItem(l.graphic)

    def drawNodes(self, truss=None, scene=None):
        truss.getCenterPt()
        rct = truss.rct
        offset = Position(x=rct.centerX(), y=rct.centerY())
        for n in truss.nodes:
            x = n.position.x - offset.x
            y = (n.position.y - offset.y)
            toolTip = f"Node: {n.name}"
            if n.name.lower() in ['left', 'right']:
                n.graphic = RigidPivotPoint(x, -y, 10, 18, brush=self.brushPivot, name=n.name, support_type=n.support_type)
                self.scene.addItem(n.graphic)
            self.drawALabel(x=x - 5, y=y + 15, str=n.name, pen=self.penLabel)

    def drawALabel(self, x, y, str='', pen=None, brush=None, tip=None):
        scene = self.scene
        lbl = qtw.QGraphicsTextItem(str)
        w = lbl.boundingRect().width()
        h = lbl.boundingRect().height()
        lbl.setX(x - w / 2.0)
        lbl.setY(-y - h / 2.0)
        if tip is not None:
            lbl.setToolTip(tip)
        if pen is not None:
            lbl.setDefaultTextColor(pen.color())
        if brush is not None:
            bkg = qtw.QGraphicsRectItem(lbl.x(), lbl.y(), w, h)
            bkg.setBrush(brush)
            outlinePen = qtg.QPen(brush.color())
            bkg.setPen(outlinePen)
            scene.addItem(bkg)
        scene.addItem(lbl)

    def drawACircle(self, centerX, centerY, Radius, angle=0, brush=None, pen=None, name=None, tooltip=None):
        scene = self.scene
        ellipse = qtw.QGraphicsEllipseItem(centerX - Radius, -1.0 * (centerY + Radius), 2 * Radius, 2 * Radius)
        if pen is not None:
            ellipse.setPen(pen)
        if brush is not None:
            ellipse.setBrush(brush)
        if name is not None:
            ellipse.setData(0, name)
        if tooltip is not None:
            ellipse.setToolTip(tooltip)
        scene.addItem(ellipse)

class TrussController:
    def __init__(self):
        self.truss = TrussModel()
        self.view = TrussView()

    def ImportFromFile(self, data):
        self.truss = TrussModel()
        for L in data:
            L = L.strip()
            if L.find('#') == 0:
                pass
            else:
                Cells = L.split(',')
                if len(Cells) <= 1:
                    pass
                elif Cells[0].lower().find('title') >= 0:
                    self.truss.title = Cells[1].strip().strip("'")
                elif Cells[0].lower().find('material') >= 0:
                    sut = float(Cells[1].strip())
                    sy = float(Cells[2].strip())
                    E = float(Cells[3].strip())
                    self.truss.material = Material(uts=sut, ys=sy, modulus=E)
                elif Cells[0].lower().find('static') >= 0:
                    sf = float(Cells[1].strip())
                    self.truss.material.staticFactor = sf
                elif Cells[0].lower().find('node') >= 0:
                    name = Cells[1].strip()
                    x = float(Cells[2].strip())
                    y = float(Cells[3].strip())
                    self.truss.nodes.append(Node(name=name, position=Position(x=x, y=y)))
                elif Cells[0].lower().find('link') >= 0:
                    name = Cells[1].strip()
                    n1 = Cells[2].strip()
                    n2 = Cells[3].strip()
                    width = float(Cells[4].strip()) if len(Cells) > 4 else 1.0
                    thickness = float(Cells[5].strip()) if len(Cells) > 5 else 0.5
                    material = Cells[6].strip() if len(Cells) > 6 else "Steel"
                    self.truss.links.append(Link(name=name, node1=n1, node2=n2, width=width, thickness=thickness, material=material))
        self.calcLinkVals()
        self.displayReport()
        self.drawTruss()

    def hasNode(self, name):
        for n in self.truss.nodes:
            if n.name == name:
                return True
        return False

    def addNode(self, node):
        self.truss.nodes.append(node)

    def getNode(self, name):
        for n in self.truss.nodes:
            if n.name == name:
                return n

    def addLink(self, link):
        self.truss.links.append(link)

    def calcLinkVals(self):
        for l in self.truss.links:
            n1 = None
            n2 = None
            if self.hasNode(l.node1_Name):
                n1 = self.getNode(l.node1_Name)
            if self.hasNode(l.node2_Name):
                n2 = self.getNode(l.node2_Name)
            if n1 is not None and n2 is not None:
                r = n2.position - n1.position
                l.length = r.mag()
                l.angleRad = r.getAngleRad()

    def setDisplayWidgets(self, args):
        self.view.setDisplayWidgets(args)

    def displayReport(self):
        self.view.displayReport(truss=self.truss)

    def drawTruss(self):
        self.truss.compute_link_weights()
        self.truss.compute_support_loads()
        self.view.buildScene(truss=self.truss)

    def install_event_filter(self, widget):
        self.view.scene.installEventFilter(widget)

    def get_item_at(self, scene_pos, transform):
        return self.view.scene.itemAt(scene_pos, transform)

    def get_items_at(self, scene_pos):
        return self.view.scene.items(scene_pos)

    def update_mouse_position(self, text):
        self.view.te_Report.parent().lbl_MousePos.setText(text)
#endregion