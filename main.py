import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.gui.OnscreenText import OnscreenText
import sys
defjump = 10
props = WindowProperties()
class FPS(object):
    """
        This is a very simple FPS like -
         a building block of any game i guess
    """
    def __init__(self):
        base.setFrameRateMeter(True)
        """ create a FPS type game """
        self.initCollision()
        self.loadLevel()
        self.initPlayer()
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        base.win.requestProperties(props)
        base.accept( "q" , sys.exit)
        base.disableMouse()
        
    def initCollision(self):
        """ create the collision system """
        base.cTrav = CollisionTraverser()
        base.pusher = CollisionHandlerPusher()
        
    def loadLevel(self):
        """ load the self.level 
            must have
            <Group> *something* { 
              <Collide> { Polyset keep descend } 
            in the egg file
        """
        self.level = loader.loadModel('level.egg')
        self.level.reparentTo(render)
        self.level.show()
        self.level.setTwoSided(True)
                
    def initPlayer(self):
        """ loads the player and creates all the controls for him"""
        self.node = Player() 
class Player(object):
    """
        Player is the main actor in the fps game
    """
    speed = 50
    FORWARD = Vec3(0,2.5,0)
    RUN = Vec3(0,4,0)
    BACK = Vec3(0,-1,0)
    LEFT = Vec3(-1,0,0)
    RIGHT = Vec3(1,0,0)
    STOP = Vec3(0)
    walk = STOP
    strafe = STOP
    FORWARD_X2 = Vec3(0,5,0)
    readyToJump = False
    jump = 0
    
    def __init__(self):
        """ inits the player """
        self.loadModel()
        self.setUpCamera()
        self.createCollisions()
        self.attachControls()
        # init mouse update task
        taskMgr.add(self.mouseUpdate, 'mouse-task')
        taskMgr.add(self.moveUpdate, 'move-task')
        taskMgr.add(self.jumpUpdate, 'jump-task')
        
    def loadModel(self):
        """ make the nodepath for player """
        self.node = NodePath('player')
        self.node.reparentTo(render)
        self.node.setPos(0,0,2)
        self.node.setScale(.05)
    
    def setUpCamera(self):
        """ puts camera at the players node """
        pl =  base.cam.node().getLens()
        pl.setFov(70)
        base.cam.node().setLens(pl)
        base.camera.reparentTo(self.node)
        base.camera.setZ(base.camera.getZ()+50)
        
    def createCollisions(self):
        """ create a collision solid and ray for the player """
        cn = CollisionNode('player')
        cn.addSolid(CollisionSphere(0,0,0,3))
        solid = self.node.attachNewNode(cn)
        base.cTrav.addCollider(solid,base.pusher)
        base.pusher.addCollider(solid,self.node, base.drive.node())
        # init players floor collisions
        ray = CollisionRay()
        ray.setOrigin(0,0,-.2)
        ray.setDirection(0,0,-1)
        cn = CollisionNode('playerRay')
        cn.addSolid(ray)
        cn.setFromCollideMask(BitMask32.bit(0))
        cn.setIntoCollideMask(BitMask32.allOff())
        solid = self.node.attachNewNode(cn)
        self.nodeGroundHandler = CollisionHandlerQueue()
        base.cTrav.addCollider(solid, self.nodeGroundHandler)
        
    def attachControls(self):
        """ attach key events """
        base.accept( "space" , self.__setattr__,["readyToJump",True])
        base.accept( "space-up" , self.__setattr__,["readyToJump",False])
        base.accept( "s" , self.__setattr__,["walk",self.STOP] )
        base.accept( "w" , self.__setattr__,["walk",self.FORWARD])
        base.accept( "s" , self.__setattr__,["walk",self.BACK] )
        base.accept( "s-up" , self.__setattr__,["walk",self.STOP] )
        base.accept( "w-up" , self.__setattr__,["walk",self.STOP] )
        base.accept( "a" , self.__setattr__,["strafe",self.LEFT])
        base.accept( "d" , self.__setattr__,["strafe",self.RIGHT] )
        base.accept( "a-up" , self.__setattr__,["strafe",self.STOP] )
        base.accept( "d-up" , self.__setattr__,["strafe",self.STOP] )
        
    def mouseUpdate(self,task):
        """ this task updates the mouse """
        md = base.win.getPointer(0)
        props.setCursorHidden(True)
        x = md.getX()
        y = md.getY()
        if base.win.movePointer(0, int(base.win.getXSize()/2), int(base.win.getYSize()/2)):
            self.node.setH(self.node.getH() -  (x - base.win.getXSize()/2)*0.1)
            
            base.camera.setP(base.camera.getP() - (y - base.win.getYSize()/2)*0.1)
            if base.camera.getP() > 90:
                base.camera.setP(89.9)
            elif base.camera.getP() < -90:
                base.camera.setP(-89.9)
        return task.cont
    
    def moveUpdate(self,task): 
        """ this task makes the player move """
        # move where the keys set it
        self.node.setPos(self.node,self.walk*globalClock.getDt()*self.speed)
        self.node.setPos(self.node,self.strafe*globalClock.getDt()*self.speed)
        
        if self.node.getZ() < -10:
            self.node.setPos(0,0,2)

        return task.cont
    def jumpUpdate(self,task):
        """ this task simulates gravity and makes the player jump """
        # get the highest Z from the down casting ray
        highestZ = -100
        for i in range(self.nodeGroundHandler.getNumEntries()):
            entry = self.nodeGroundHandler.getEntry(i)
            z = entry.getSurfacePoint(render).getZ()
            if z > highestZ and entry.getIntoNode().getName() == "Cube":
                highestZ = z
        # gravity effects and jumps
        self.node.setZ(self.node.getZ()+self.jump*globalClock.getDt())
        self.jump -= 20*globalClock.getDt()
        if highestZ > self.node.getZ()-.3:
            self.jump = 0
            self.node.setZ(highestZ+.3)
            if self.readyToJump:
                self.jump = 10
        return task.cont
       
FPS()
base.run() 