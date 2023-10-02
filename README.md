# Scientific Programming in Python – Submission 3

### Project title: Real-time GPS Satellite Tracking

### Student name: Davlesh Jodhun
### Course: MSc Machine Learning in Science
### University: University of Nottingham

## Background
There are 31 Global Positioning System satellites in Medium Earth Orbit (about 20,200km above Earth). Being in a precise location at a given time is of crucial importance to their use in navigation. In total, there are about 5,500 satellites in orbit, with a projceted number of 58,000 by 2030. The problem of satellite tracking is not novel, since the various governments have had to track them since their inception. Likewise, the problem of coding it within Python is not new either, having been done before. Skyfield is a package that can be used to faciliate the project. See https://github.com/xtai/Real-Time-Satellite-Tracking/blob/master/3d-refactor-2.py for an example done without Skyfield. 

This project will track the position of GPS satellites in orbit over Earth and visualise their paths over a 3D model of Earth. Then, (based on the feedback received from the previous submission) satellites will be plotted over a map using Cartopy, with a view to use Streamlit to select locations and see what satellites are overhead. Since Skyfield is being used, the project includes satellites that are in orbit, and the code allows for these different sets of satellites to be plotted. 

GPS TLE data will be taken from the website http://celestrak.org/NORAD/elements/gp.php?GROUP=gps-ops&FORMAT=tle and stored at reasonable intervals to have the data offline. The TLE data becomes unfit for predicting orbits 2 weeks either side of the date the data was gathered, so it is important that the data is refreshed regularly and for comparisons, the data is kept for later. The TLE data contains information such as the position, name, position and time, alongside other metrics beloning to the satellite, all encoded to two lines. Data for other satellites can be taken from this website as well.

## Outline 
#### List of modules to be used (initial): 
  - matplotlib: https://matplotlib.org/stable/index.html
  - scipy: https://scipy.org/
  - numpy: https://numpy.org/
  - pandas: https://pandas.pydata.org/
  - Cartopy: https://scitools.org.uk/cartopy/docs/latest/
  - Skyfield and sgp4: https://rhodesmill.org/skyfield/
  - Astropy: https://www.astropy.org/
  - Modules such as sched and time to keep taking data over time: https://docs.python.org/3/library/sched.html
  - Streamlit: https://streamlit.io/

#### Structure of code:
  - Defined functions and classes in a separate file, to be called elsewhere. 
  - Main file: setup of data and plotting the axes and the sphere, importing the other functions. 
  - Extra folder for 3D assets, if they are to be used and overlaid over the mesh sphere. 

#### Potentially several user defined functions:
  - One function to pull the data from the website and store it, updating at regular intervals that make sense, such as every 10-30 seconds.
  - One function to display the Earth/Mercator Projection Map (if there is no exisiting one that can do this) on a set of axes. Alternatively, just drawing a sphere in a set of axes can work if there is time trouble. 
  - One function to plot the paths of the satellites, plotting the past data as solid lines, and future data in dashed lines.
  - One function to find the patches of sky where there are the fewest satellites passing through in a given time period. 

## Code Snippets

Data Acquisition:

```
import urllib.request 
from urllib.request import urlopen
from skyfield.api import Loader, EarthSatellite

url = "http://celestrak.org/NORAD/elements/gp.php?GROUP=gps-ops&FORMAT=tle"

def dataacquisition(url):
    source = source = urllib.request.urlopen(url).readlines()
    source = [s.decode("utf-8") for s in source]
    source = [s.strip() for s in source]
    names = source[0::3]
    del source[0::3]
    L1list, L2list = source[0::2], source[1::2]
    L1list = [s.strip() for s in L1list]
    L2list = [s.strip() for s in L2list]
    return L1list, L2list, names

L1list, L2list, names = dataacquisition(url)            #This function takes the raw TLE data, decodes it, then separates it into name and the 2 lines of data

```
The dataacquisition function requires a method that means it can run at regular intervals to ensure that the TLE data is accurate for the time being. This will be done using sched or time, or a combination of both. 

## Pseudocode

```
##Plotting the Earth as a wire sphere:
#radiusE = 6378  #rE in km
#longitude_lines = [] #Need to choose a number of lines of longitude such that the sphere is visible - so fewer than 360
#latitude_lines = [] #There are 180 lines of latitude

#class Satellite:
#    def __init__(self, name, L1, L2)       #Reading the split TLE data - can be done in Skyfield with more ease. 
#    
#    3D position vector with parameters (x, y, z) relative to the radius of the Earth
#    
#    Define the Satellite as a square on the grid, that will draw out the orbit 

#Following the definition of the class of satellites, the following can be executed with Skyfield:
#
#L1List, L2List = TLE.load()      #This is not a necessary line of code, but can be used to get a handle on the TLE data. 
#
# for i in range(len(names)):
#     sat = names[i], L1list[i], L2list[i]
#     satpos = sat.at(time).position.km       #This loop can position the satellites in the right places, such that their orbits can be drawn.
#

```
Defining Satellite as a class will be the basis of creating all the satellites from the TLE data. For now, the plotting element has been kept to a function for each set of satellites, and might not require the use of classes. 

## Previous uncertainties, from submission 1: 
  - Not sure if this is particularly feasible for my level of programming. Finding the patches of sky that have minimal satellite coverage is going to be difficult, espcially if I am aiming for a graphical output. 
  - The Skyfield library (in particular the module sgp4) is used to carry out this kind of task. While the use of Skyfield might seem to trivialise the project, it presents its own challenges.
  
## Previous goals, from submission 2:
  - The code, as of right now, takes the data from Celestrak (only GPS data for now, might expand this later), and plots their orbits, along with a wire sphere representing Earth. Included is the current plot output from the TLE data in 3D space.
  - The next step will be to finish converting the coordinates into usable Cartesian coordinates to be plotted on a map of Earth, using Cartopy, to show the paths the satellites take. This should not take too much longer. I will also try and see if I can wrap the same map on to the sphere. 
  - Another small tweak would be to use datetime alongside skyfield such that the current date and time can be used. This should also not take too long. 
  - Creating a Streamlit dashboard (as per the feedback) is currently in the works, as I am getting to grips with how it works behind the scenes.
  - I will look to make the program more efficient in the final touches. 

## Final Submission
  - The code now takes data for several Celestrak pages, including GPS, GLONASS, Space Stations and Military (Miscellaneous). The orbits are plotted in 3D, with the same Earth mesh, and the ground tracks are plotted in 2D. The Polar plot, looking outwards from the coordinates for the University of Nottingham, shows the path traced by the first GPS satellite on the list. 
  - A Streamlit dashboard has been created. The line "streamlit run PHYS4038_Satellite_Tracking_in_Python_with_Streamlit.py" pasted into the anaconda navigator should bring up the dashboard, for now. I will put it on a public repository, if required. 
  - Final plots have been provided as images. These images use the most up to date Celestrak data (03:00 on 21/12/2022) to predict where the GPS satellites will be at 00:00 on 25/12/2022. 
 
## Further Improvements
  - Due to time constraints, the final plot - the Polar plot only shows the path of the first GPS satellite when looking outwards. 
  - If I had the time and expertise, I would use a for loop to plot all the possible versions of the plot, separately (this is fleshed out in the report). Additionally, wrapping the Earth mesh in a map was not completed, due to the same constraints, and issues with the PIL library. 
  - I will probably tweak parts of this project in my spare time (if I get any) next semester. 
