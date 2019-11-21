---
layout: default
title: Getting Started
nav_order: 2
---
### If you are coming from using GroundControl:

My recommendation is to import your groundcontrol.ini file before proceeding any further.

Go to Actions->Import groundcontrol.ini

If all goes well and the comport assignment is still the same, you should be able to communicate with the controller.

### If you are starting anew:

#### 1) Set ComPort

Go to Settings->Maslow Settings->COMPort and select the comport for the arduino controller.  Press the 'refresh' symbol to populate the list of available comports (give it a couple of seconds if you have a bluetooth enabled on the computer running webcontrol).  Don't forget to press submit.  If all goes well, you should see messages coming from the controller in the lower right portion of the screen (Controller Messages)

![Test](/assets/gettingStarted/comPort.png')

<figcaption class="figure-caption">COMPort Setting</figcaption>

</figure>

#### 2) Set Distance to Extend Chains

If you are using a top beam that's longer than 10 feet, go to Settings->Advanced Settings->Extend Chain Distance.  If using a 12-foot beam, change to 2032.  This is the amount of chain that will be extended to allow you to connect up the sled.  Too little and they won't meet and too much, the sled may be on the floor.  You don't have to use a value that perfectly equates to the center of the board, just make sure it's a multiple of 6.35 mm.

<figure class="figure">![]({{ url_for('static',filename='images/gettingStarted/extendChainDistance.png') }})

<figcaption class="figure-caption">Extend Chain Distance</figcaption>

</figure>

#### 3) Quick Configure

Go to Actions->Quick Configure and enter the requested information.  This lets the controller know enough about the setup to allow you to calibrate the machine.  Don't forget to press submit.

#### 4) Set Sprockets Vertical

Go to Actions->Set Sprockets Vertical:

4a) Get one tooth of each sprocket as precisely vertical as you can using the buttons.  When done, press 'Define Zero'.  This tells the controllers that the chain length is 0. 

<figure class="figure">![]({{ url_for('static',filename='images/gettingStarted/Sprocket at 12-00.png') }})

<figcaption class="figure-caption">Sprocket with Vertical Tooth</figcaption>

</figure>

4b) Install the chains on the sprocket such that the first link is resting on the top sprocket tooth. The placement depends on if you built the frame for "Chains Off Top" or "Chains Off Bottom" 

<figure class="figure">![]({{ url_for('static',filename='images/gettingStarted/chainOffSprocketsBottom.png') }})

<figcaption class="figure-caption">Chains Off Bottom</figcaption>

</figure>

<figure class="figure">![]({{ url_for('static',filename='images/gettingStarted/chainOffSprocketsTop.png') }})

<figcaption class="figure-caption">Chains Off Top</figcaption>

</figure>

4c) Extend left chain. Press 'Extend Left Chain to xxxx mm' where xxxx is the distance set in Step 2.  <span style="text-decoration: underline; color: #ff0000;">Warning: This is one spot where the chains can get wrapped around the sprocket.  Grab hold of the end of the chain and apply tension to it as it feeds off the sprocket so it doesn't wrap</span>.

4d) Extend right chain. Press 'Extend Right Chain to xxxx mm' where xxxx is the distance set in Step 2.  <span style="text-decoration: underline;"><span style="color: #ff0000; text-decoration: underline;">Warning: Same as above.</span></span>

4e) Connect Sled.  Connect up your sled to the extended chains.

4f) Mark chains.  Take a marker, nail polish, something, and mark the specific chain link that is on top of the top tooth.  If the 'Extend Chain Distance' is a multiple of 6.35 mm, there should be a tooth perfectly vertical after extending the chains.  Mark this because if you ever have to reset the chains, you need to know which link is this one.

#### 5) Calibrate

5a) If using stock firwmare, go to 'Actions->Triangular Calibration.'  If using holey calibration firmware, go to 'Actions->Holey Calibration'

5a) Press 'Cut Calibration Pattern' and wait for the sled to complete the cutting.

5b) Enter measurements as requested.

5c) Press 'Calculate'

5d) If all looks good, press 'Accept Results' (you may have to scroll down the screen to see it)

5e) Dance a jig.  You're calibrated.
