import cherrypy
import picamera
from pymavlink import mavutil
import math
from time import sleep

class Web(object):
    
    def __init__(self):
        # First get an instance of the API endpoint
        api = local_connect()
        # get our vehicle - when running with mavproxy it only knows about one vehicle (for now)
        self.v = api.get_vehicles()[0]
        #self.camera = picamera.PiCamera()
        #self.camera.vflip = True
        #self.camera.hflip = True
    
    
    #****WGCS Section*****************
    @cherrypy.expose
    def index(self, param = ""):
        if param == "ARM":
            self.v.armed = not self.v.armed
        if param == "Take Picture":
            self.takePicture()

        #configure flight mode
        mode = "%s" % self.v.mode
        mode = mode[12:]
        
        #configure the yaw, pitch, and roll values
        attitude = "%s" % self.v.attitude
        attitude = attitude[9:]
        attitudes = attitude.split(",")
        
        
        #configure gps
        #gps = "%s" % self.v.gps_0
        
        
        return """<html>
                    <head></head>
                        <body>
                            <h1>The Pi Drone's WEB GROUND CONTROL STATION (WGCS)</h1>
                            <p>
                                FLIGHT MODE: {0}<br>
                                Set to
                                <select>
                                    <option value="stabilize">STABILIZE</option>
                                    <option value="auto">AUTO</option>
                                    <option value="loiter">LOITER</option>
                                    <option value="althold">ALTHOLD</option>
                                </select><br><br>
                                {1} <br>
                                {2} <br>
                                {3} <br><br>
                                
                            </p>
                            <form method="post" action="arm">
                                <button type="submit" method = "post">{4}</button>
                            </form>
                            <img src="http://www.dji.com/wp-content/uploads/2012/11/features_icon_attractive.png" alt="some_text">
                        </body>
                </html>""".format(mode, attitudes[0], attitudes[1], attitudes[2],"arm/disarm")
            
    @cherrypy.expose
    def arm(self):
        self.v.armed = not self.v.armed
        raise cherrypy.HTTPRedirect("/")
    
    @cherrypy.expose
    def takePicture(self):
        #self.camera.capture('image.jpg')
        cherrypy.log("Picture Taken")
        raise cherrypy.HTTPRedirect("/")
    
    #******iOS Section *****
    
    #Change mode using /iChangeMode?=[mode]
    #specify mode in ALL CAPS and use the mode command in mavproxy to discover availible modes
    @cherrypy.expose
    def iChangeMode(self, mode = 'STABILIZE'):
        cherrypy.log("Changing mode to " + mode)
        self.v.mode = VehicleMode(mode)
    
    @cherrypy.expose
    def iTakePicture(self):
            #self.camera.capture('image.jpg')
            cherrypy.log("*Picture Taken!*")

    @cherrypy.expose
    def iArm(self):
        self.v.armed = True

    @cherrypy.expose
    def iDisarm(self):
        self.v.armed = False

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def JSON(self):

        #configure flight mode
        mode = "%s" % self.v.mode
        mode = mode[12:]
        modedict = {"AUTO":0, "STABILIZE":1, "LOITER":2, "ALT_HOLD":3}
        mode = modedict[mode]

        #Configure attitude values
        pitch = float("{0:.2f}".format(math.degrees(self.v.attitude.pitch)))
        yaw = float("{0:.2f}".format(math.degrees(self.v.attitude.yaw)))
        roll = float("{0:.2f}".format(math.degrees(self.v.attitude.roll)))

        armed = int(self.v.armed)

        altitude = float("{0:.2f}".format(self.v.location.alt))
        lat = self.v.location.lat
        lon = self.v.location.lon

        groundspeed = self.v.groundspeed

        #Not sure what type GPSInfo is so I'll have to extrac the string out ...
        gpsstrings = ("%s"%self.v.gps_0).split(",")
        gpsfix = int(gpsstrings[0][12:])

        return {"mode": mode, "pitch": pitch, "yaw": yaw, "roll": roll, "armed":armed, "alt": altitude, "groundspeed":groundspeed, "gpsfix": gpsfix, "lat": lat, "lon": lon}


# Start web server
cherrypy.tree.mount(Web())
cherrypy.config.update({
                       'server.socket_port': 9090,
                       'server.socket_host': '0.0.0.0',
                       'log.screen': None
                       })

cherrypy.engine.start()
cherrypy.engine.block()




 