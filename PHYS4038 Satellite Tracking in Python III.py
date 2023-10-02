from skyfield.api import Loader, EarthSatellite
from skyfield.timelib import Time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import urllib.request 
from urllib.request import urlopen
from datetime import datetime as dt #To tidy up the date and time import for Celestrak
#The following are for the TEME Coordinates from TLE Data
from sgp4.api import Satrec
from sgp4.api import SGP4_ERRORS
from astropy.time import Time
from astropy.coordinates import TEME, CartesianDifferential, CartesianRepresentation
from astropy import units as u
from astropy.coordinates import ITRS
from astropy.coordinates import EarthLocation
import cartopy.crs as ccrs
import matplotlib.cm as mplcm
import matplotlib.colors as colours
from skyfield import api
from pytz import timezone
utc = timezone('UTC')

def axislimits(axis):
    """
    Generates the 3D axes in which the orbits are to be plotted in. Takes 
    the axes as the argument, which is defined when plotting. 
    
    """
    try:
        lims = axis.get_xlim(), axis.get_ylim(), axis.get_zlim()
    except AttributeError:
        pass
    try:
        centres = [0.5*sum(pair) for pair in lims] 
        widths  = [pair[1] - pair[0] for pair in lims]
        halfwidth = 0.5*max(widths)
        axis.set_xlim(centres[0] - halfwidth, centres[0] + halfwidth)
        axis.set_ylim(centres[1] - halfwidth, centres[1] + halfwidth)
        axis.set_zlim(centres[2] - halfwidth, centres[2] + halfwidth)
        return centres, halfwidth
    except UnboundLocalError:
        pass

def dataacquisition(url):
    """
    Takes data from the Celestrak webpage, which comes as Two Line Element
    (TLE) data, in which position, velocity and time are encoded. This function
    then decodes the TLE data into utf-8 from bytes, and then splits the 
    2 lines into 2 lists, ready for use later on. 
    
    """
    source = urllib.request.urlopen(url).readlines()
    source = [s.decode("utf-8") for s in source]
    source = [s.strip() for s in source]
    names = source[0::3]
    del source[0::3]
    L1list, L2list = source[0::2], source[1::2]
    L1list = [s.strip() for s in L1list]
    L2list = [s.strip() for s in L2list]
    length = len(names)
    return L1list, L2list, names, length

def earthMesh(ax, lonspace, latspace):
    """
    Plots a mesh sphere, of radius 6378 (km), using an array of latitude and 
    longitude lines. This sphere represents Earth, and will most likely be 
    replaced or covered by an image - currently testing plotly to plot Earth 
    on the surface.
    
    """
    theta = np.linspace(0, twopi, 201)
    cth, sth, zth = [f(theta) for f in (np.cos, np.sin, np.zeros_like)]
    lon0 = re*np.vstack((cth, zth, sth))
    lons = []
    lat0 = re*np.vstack((cth, sth, zth))
    lats = []
    for phi in rads*lonspace:
        cph, sph = [f(phi) for f in (np.cos, np.sin)]
        lon = np.vstack((lon0[0]*cph - lon0[1]*sph, lon0[1]*cph + lon0[0]*sph, lon0[2]))
        lons.append(lon)
    for phi in rads*latspace:
        cph, sph = [f(phi) for f in (np.cos, np.sin)]
        lat = re*np.vstack((cth*cph, sth*cph, zth+sph))
        lats.append(lat)
    for x, y, z in lons:
        ax.plot(x, y, z, '-k')
    for x, y, z in lats:
        ax.plot(x, y, z, '-k')
    return lons, lats

def GPS_orbit_plotter(ax, time, length):
    """
    Plots the orbits of the GPS satellites, using the decoded TLE data. The 
    Skyfield library handles these data and combines it with the time in order
    to calculate the orbits. A second scatter plot is overlaid on top of the 
    first, to provide the locations of the satellites at a given time. 
    
    """
    GPSL = []
    GPSPL = []
    GPSPL2 = []
    for i in range(length):
        GPS = EarthSatellite(L1list[i], L2list[i])
        GPSL.append(GPS)
#        print(GPS.epoch.tt)
        GPSpos = GPS.at(time).position.km
        GPSPL.append(GPSpos)
        GPSpos2 = GPS.at(time2).position.km
        GPSPL2.append(GPSpos2)
        print(GPSpos)
#        print(GPSpos.shape)
        if True:    
#            fig = plt.figure(figsize=[10, 8])  # [12, 10] for alternate size. 
#            ax  = fig.add_subplot(1, 1, 1, projection='3d') #These lines are here for individual plots of each orbit, should they be needed.
            x, y, z = GPSpos
            a, b, c = GPSpos2
#            markers_on = [a,b,c]
            ax.plot(x, y, z)#, markevery = markers_on, marker = "o")
            ax.scatter(a, b, c)
            ax.text(x[i],y[i],z[i], '%s' % (str(names[i])), size=10, zorder=1, color='k')            
        centres, halfwidth = axislimits(ax)
        #plt.legend(names, bbox_to_anchor=(1.05, 1))
#    plt.show()
    return GPS, GPSpos
    
def orbitalElementPlotter3D(time, length):
    """
    Plots the Earth mesh and the orbits in one single plot, and saves it to use
    in Streamlit. Unfortunately, saved plot cannot be interacted with, yet, in 
    the Streamlit environment.
    
    """
    fig1 = plt.figure(figsize=[10, 8])  # [12, 10]
    ax  = fig1.add_subplot(1, 1, 1, projection='3d')
    NUM_COLOURS = 31
    cm = plt.get_cmap('jet')
    cNorm  = colours.Normalize(vmin=0, vmax=NUM_COLOURS-1)
    scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)
    ax.set_prop_cycle(color=[scalarMap.to_rgba(i) for i in range(NUM_COLOURS)])
    earthMesh(ax, lonspace, latspace)
    GPS_orbit_plotter(ax, time, length)
    plt.show()
    return ax

def orbitalElementPlotter2D(time, length):
    """
    Plots the ground traces of the satellite orbits on the Plate Carree world
    map projection, along with a point to show the location of the satellite
    at the given time. 

    """
    fig2 = plt.figure(figsize=[12, 10])  # [12, 10]
    ax = fig2.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    NUM_COLOURS = 31
    cm = plt.get_cmap('jet') #gist_rainbow/rainbow
    cNorm  = colours.Normalize(vmin=0, vmax=NUM_COLOURS-1)
    scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)
    ax.set_prop_cycle(color=[scalarMap.to_rgba(i) for i in range(NUM_COLOURS)])
    ax.coastlines()
    for i in range(length):
        GPS = EarthSatellite(L1list[i], L2list[i])
        GPSgeocentric = GPS.at(time)
        GPSgeocentric2 = GPS.at(time2)
        subsat = GPSgeocentric.subpoint()
        subsat2 = GPSgeocentric2.subpoint()
        if True:
            plt.scatter(subsat.longitude.degrees, subsat.latitude.degrees, transform=ccrs.PlateCarree(), linewidth=1, s=0.6)
            plt.scatter(subsat2.longitude.degrees, subsat2.latitude.degrees)
#            ax.text(x[i],y[i], '%s' % (str(names[i])), size=10, zorder=1, color='k')        
            plt.legend(names, bbox_to_anchor=(1.05, 1))            
    plt.show()

def overhead_polar_plot(overhead_pass):
    """
    
    This is a proof of concept plot, that, given more time and better coding
    expertise, would show the traces of the satellites in the sky, looking
    upwards, given a location on Earth. Currently, only the first GPS satellite
    in the TLE data is used to plot the figure. The for loop would have been used
    to plot the rest, in a similar fashion as before, however it would result 
    in a very cluttered figure. This part of the code was modified from 
    https://rhodesmill.org/brandon/2018/tiangong/, which is part of the 
    Skyfield API. 
    
    """
    i, j = overhead_pass
    fig3 = plt.figure()
    ax = plt.subplot(111, projection="polar")
    ax.set_rlim([0, 90])
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    theta = az.radians
    r = 90 - alt.degrees
    ax.plot(theta, r, '--')
    for k in range(len(theta)):
        text = time[k].astimezone(utc).strftime('%H:%M')
    plt.show()
    
#%%
#SKYFIELD FOR TLE TO ORBITAL POSITION

url = "http://celestrak.org/NORAD/elements/gp.php?GROUP=gps-ops&FORMAT=tle"
L1list, L2list, names, length = dataacquisition(url)

halfpi, pi, twopi = [f*np.pi for f in (0.5, 1, 2)]
degs, rads = 180/pi, pi/180
lonspace = np.arange(0, 180, 15)
latspace = np.arange(-75, 105, 15)

#Loading in data from the Skyfield package 
load = Loader('~/Documents/fishing/SkyData')
data = load('de421.bsp')
ts   = load.timescale()
planets = load('de421.bsp')
earth   = planets['earth']
re = 6378.

hours = np.arange(0, 24, 0.01) #For a 24 hour period. Points on the 2D map are generated using hours = 0

time = ts.utc(2022, 12, 18, hours)
time2 = ts.utc(2022, 12, 18, 0)

# ax = orbitalElementPlotter3D(time)

# annotations = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
#                           bbox=dict(boxstyle="round", fc="w"),
#                           arrowprops=dict(arrowstyle="->"))
# annotations.set_visible(False)

# ax.canvas.mpl_connect("motion_notify_event", hover)

orbitalElementPlotter3D(time, length)
orbitalElementPlotter2D(time, length)

earthloc = api.Topos(latitude='52.9388 N', longitude='1.1981 W') #UoN location
for i in range(length):  
    GPS = EarthSatellite(L1list[0], L2list[0])
    orbitval = (GPS - earthloc).at(time)
    alt, az, distance = orbitval.altaz()
    above_horizon = alt.degrees > 0
    boundaries, = np.diff(above_horizon).nonzero()
    passes = boundaries.reshape(len(boundaries) // 2, 2)

overhead_polar_plot(passes[0])
