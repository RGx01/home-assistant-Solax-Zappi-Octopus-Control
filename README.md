# Solax-Zappi-Octopus-Control

![test3](https://github.com/user-attachments/assets/b3d212c2-b009-4605-927f-539bd89c1e69)

* [Introduction](#introduction)
* [Screenshots and Descriptions](#screenshots-and-descriptions-of-dashboards)
* [Credits and Acknowledgments](#credits-and-acknowledgments)
* [INSTALL INSTRUCTIONS](#install-instructions)
	* [Prerequisite Integrations](#prerequisite-integrations)
	* [Mandatory Manual Adjustments to Config Yaml & Dashboard Yaml](#mandatory-manual-adjustments-to-config-yaml--dashboard-yaml)
	* [Adding the Dashboards](#adding-the-dashboards)
* [Revision Log](#revision-log)
* [Automation Function Summary](#automation-function-summary)
	* [5001 - Solax Zappi Octopus Control](#5001---solax-zappi-octopus-control)
	* [5002 - Solax Reset Mode After Manual Discharge](#5002---solax-reset-mode-after-manual-discharge)
	* [5003 - Solax Set UI Options](#5003---solax-set-ui-options)
	* [5004 - Solax Reload Settings](#5004---solax-reload-settings)
	* [5005 - Solax Zappi Octopus Control - Notifier](#5005---solax-zappi-octopus-control---notifier)
	* [6001 - Octopus - Free Electric Automation](#6001---octopus---free-electric-automation)
	* [6002 - Octopus - Saving Sessions Automation](#6002---octopus---saving-sessions-automation)
* [Initial User Requirements](#initial-user-requirements)
* [Future Dev Work](#future-dev-work)
* [Problems Found During Development](#problems-found-during-development)
* [Equipment Used During Development](#equipment-used-during-development)
  
## Introduction
Please note this is designed specifically for Intelligent Octopus Go using a Zappi registered with Octopus. Using any other timers and programs to contol your EV with this project may cause unexpected behaviours.
<br>This started out as a Home Assistant project to create a UI to control my Solax inverter locally. It's now a project to automate the contol of the my Solax inverter, Zappi EV charger and Octopus Energy interactions including Octoplus Saving Sessions and Free Electric sessions. The idea isn't entirely new (see credits below) but the project now goes beyond my original idea and now provides the opportunity to automatically contol for scenarios (decribed in the requirements below). 

The project is split into 3 parts:
<br> 
Part 1 can be used in it's own right and creates all the sensors and provides all the rest/restful local connections. This may be useful if you want to build your own interfaces/automations on top.
<br>
* The first part is to simplify previous efforts by Kamil Baczkowicz into a single Home Assistant Package (with some updated parts).
	* config/packages/solax.
* The second, is to create an interactive dashboard/ui to control how energy is used with Octopus Energy and Zappi EV charger.
	* config/packages/solax_zappi_octopus
 	* Automations 5001-5005
  	* Dashboard Solax & Octopus Settings.yaml	 
* The third part provides integration with Octoplus Saving Sessions and Free Electric Sessions.
	* config/packages/octopus_saving_sessions
 	* Automations 6001-6002
  	* Dashboard Octopus Saving Sessions.yaml

## Screenshots and Descriptions of Dashboards

## Solax Zappi Octopus Control Dashboard
![Screenshot 2025-03-24 at 17 35 44](https://github.com/user-attachments/assets/e0a79123-4eac-444e-b180-504541a8b951)
### Octopus Device Settings
<ol>
	<li>Octopus Will Provide Next Schedule At - This indicates when Octopus will provide the next schedule. The time is based on the two options below.</li>
	<li>Octopus Schedule at Anytime - When this is set to on, Octopus will provide a schedle as soon as you plug in or if you're EV is already connected switching it to on will get a schedule.</li>
	<li>Octopus Schedule after Sun Elevation Threshold - Switching this to on will maximise the amount of solar stored in the house battery before Octopus will provide a schedule. </li>
	<li>Sunset degrees above horizon - Sets a threshold to support the above option.</li>
	<li>Octopus Will Provide Next Schedule At - If "Schedule at Anytime" and "Schedule after Sun Elevation Threshold" are both off, the time set here is when Octopus will get the schedule.</li>
	<li>Intelligent Charge Target - This reflects what is set in the Octopus app.</li>
	<li>Inteligent Target Time - This reflects what is set in the Octopus app.</li>
	<li>Intelligent Smart Charge - This reflects what is set in the Octopus app. The Automation contols this, changing it manually can have unexpected results.</li>
	<li>Zappi always in ECO+ Mode (when connected) - Select this if you wish to use excess solar to charge EV. </li>
	<li>Minimum Green Level.</li>
	<li>Zappi Charge Mode - Automation sets this to "Stop" when EV is disconnected. Automation controls this, changing it manually can have unexpected results. </li>
</ol>

### Notification Management

<ol start=12>
	<li>Notifications - Turn this on to receive notifications both in HA and any mobile device selected.</li>
	<li>Notify Mobile device - A dropdown list of all mobile devices with the Home Assistant companion app installed. Select one or more devices to receive notifications generated by the automations. Reselecting a device will remove it from receiving notifications.</li>
	<li>Reset Device List - pressing this button will remove all devices selected to receive notifications. </li>
	<li>Notifications to Exclude - A complete list of notifications. Selecting notifications in the list will disable them from being notified. </li>
	<li>Reset Notification Exclusions - After pressing this, all notifications will notified on.</li>
	<li>Summary of which devices and which notifications are excluded.</li>
</ol>

### Solax Control

<ol start=20>
	<li>Inverter Off/On - Turns the invert on or off</li>
	<li>Work Mode - Changes the working mode of the inverter to either Self Use or Feed In.</li>
	<li>Use Grid During Dispatch - Selecting this option will set the min battery SoC to 100% when EV is following the schedule or when the tariff is off-peak. This can be advantageous as less energy needs to be imported and stored and more is therefore available for export.</li>
	<li>Prevent Zappi from Draining Battery - Depending on where the Solax CT clamp is positioned it may see Zappi loads. Selecting this option prevents the inverter dumping the battery into the EV by setting the Solax SoC to 100% when the EV starts to charge. </li>
	<li>Export Battery before charging EV - Selecting this option will discharge the Solax Battery to a defined SoC (below) before getting an Octopus schedule (if EV is connected). This is useful to load shifters and to users with large EV capacity that also want to export the house battery but also require the house battery to charge during the off peak.</li>
	<li>Discharge to SoC (before charging EV) - Set the SoC to discharge the house battery to prior to getting an Octopus Schedule. Setting this too low could leave you importing peak rate energy if Octopus doesn't schedule to start EV immeadiatley after. </li>
	<li>Daily Battery Export After EV Charge (23:30 - Battery Start Charge Time) - Select this option to export the Solax battery everyday between 23:30 and the start time of the solax battery charge. If the EV is charging the export will happen after the EV has finished but not before 23:30.</li>
	<li>Daily/Forced Discharge SoC - The SoC the automation will aim to hit when discharging daily. The same limit is used if the manual discharge option below is left unattended. Recommend setting this to 20% or higher.</li>
	<li>Default Mode After Discharge - The invert mode the automation returns to after a forced discharge. </li>
	<li>Default Min SoC - The default minimum SoC the inverter should return to after an operation (15% is standard and recommended to maintain life during normal house hold loads).</li>
	<li>Default Charge to SoC - Sets the default charge to limit after an operation. Setting this below 100% will not always give the desired results. When charging from grid the SoC always seems to go 5% higher. When charging from PV the limit may as well not be there.</li>
</ol>
<ol start=40>
	<li>Solax Force Discharge - Press this to discharge the battery. The discharge will stop automatically at the limit defined above in "Daily/Forced Discharge SoC" or if the button below is pressed.</li>
	<li>Solax Stop Discharge - Press this to stop the discharge and return to default operation as defined in "Default Mode After Discharge" above.</li>
</ol>

### Battery Heating

<ol start=50>
	<li>Battery Heating - Turn this on to enable battery heating schedule.</li>
	<li>Battery Heating Start time.</li>
	<li>Battery Heating End time.</li>
        <li>Battery Heating Start time 2.</li>
	<li>Battery Heating End time 2.</li>
</ol>

### Self Use Mode Settings
If the mode is changed in solax control then the settings for 'Feed in Mode' will be displayed.
These are the same setting that are displayed through the solax app or web ui but controlled locally rather than using the internet.
They are displayed but there is little reason to ever change them once set.

<ol start=60>
	<li>Self Use Min SoC - Sets the battery minimum SoC. If changed it will return to default levels (set in Solax Contol) after a forced discharge or any operation that causes the mode to change.</li>
	<li>Self Use Charge to SoC - Sets the charge to SoC. Same rules apply.</li>
	<li>Battery Start Discharge Time - shoiuld always be set to 00:00.</li>
        <li>Battery Stop Discharge Time - should always be set to 23:59.</li>
	<li>Self Use Enable Charge From Grid - If switched to on the battery can charge from grid during the following times.</li>
	<li>Battery Start Charge Time - recommend to set this to as close as possible to the stop time but leave enough time to fully charge. This leaves a bigger window of oppurtunity to export battery to grid if using the daily export function.</li>
	<li>Battery Stop Charge Time - recommend to set this to the end of off peak time.</li>
	<li>Charge Period 2 - This option is used by the 6001 and 6002 automations. If set manually it will turn back off after the stop 2 time.</li>
</ol>



## Saving Sessions and Free Electric Dashboard
![Screenshot 2025-03-24 at 21 22 53](https://github.com/user-attachments/assets/314d39ec-d72b-4739-909a-fedbfbe6eab9)
### Octopus Saving Sessions
This automation auto joins saving sessions that are announced via the Octopus API. Some Sessions are only notified by email so a manual method is provided. The automation handles stopping the EV from charging if it is charging prior to the session. 5001 also handles the charger starting to charging during a saving session should an EV be connected within the session. 6002 will also attempt to get an octopus schedule after the session has finished.
<ol start=70>
	<li>6002 - Octopus - Saving Sessions Automation - turns automation on/off.</li>
	<li>Preparation Time (minutes) - Only active if set to > 5 minutes. Preparation is only worth doing if the octopoints saved is greater than the peak rate used. However if the EV is charging during preparation window then it's still worth preparing.</li>
	<li>If preparing, the battery will stop charging at this SoC.</li>
	<li>Target Battery Discharge SoC - Once this SoC is hit during the saving session the inverter will return to default mode specified in Solax Control above.</li>
	<li>Try for a Dispatch During Prep - This probably only applies to large EV users where you can pretty much guarantee if you plug in you can get a dispatch.</li>
	<li>Try for a Dispatch After Session - Tries for an octopus schedule after the session ends.</li>
	<li>Saving Session Today - This is changed automatically, no need to adjust.</li>
	<li>Octopus Saving Session Start - This is changed automatically, no need to adjust unless there is an session only announced via email.</li>
	<li>Octopus Saving Session End - This is changed automatically, no need to adjust unless there is an session only announced via email.</li>
	<li>Saving Session Manual Program - If a saving session is announced via email, first change the above fields and then set this to on.</li>
</ol>

### Octopus Free Electricity (1hr Session)
On the free electric day the inverter will use Feed In priority to leave capacity to charge the battery. This will prevent solar engy filling the battery if the default mode is Self Use.
<ol start=80>
	<li>6001 - Octopus - Free Electric Automation - turns automation on/off.</li>
	<li>Octopus Free Electricity Start - set the time for free electric.</li>
	<li>Octopus Free Electric Stop - Time the 1hr session will finish.</li>
	<li>Use Target SoC as Charge to Soc - normally if you allow charge from grid (during periods set in 65 and 66 above) it will charge battery to the default level. Setting this option will charge the battery to the SoC level below. The idea is to leave capacity available to charge during the free electric session. However if this is left off, the below SoC will be achieved by a forced discharge at the time specified below.</li>
	<li>Target Battery SoC - Target to reach before Free Electric Session.</li>
	<li>Export Battery @Time to Target SoC - used if 83 above is off.</li>
	<li>Free Electricity Today - sensor to indicate if the Free Electric Session is today.</li>
</ol>


### Using the Inverter SoC Controls to Control When the Battery Discharges
<img width="525" alt="Screenshot 2025-01-29 at 17 01 42" src="https://github.com/user-attachments/assets/4413fdbe-e1ce-46bd-a021-929edd766c1f" />

### Automation 5001

![Screenshot 2025-03-24 at 17 28 50](https://github.com/user-attachments/assets/25001580-f290-4a80-9afc-b91043494663)


## Credits and Acknowledgments
The Solax interactions are possible due to work published by @Colin Robbins and @Kamil Baczkowicz. I've tried to simplify things by putting their work into a package. Essentially it becomes a building block for my automations and dashboards. Suggested reading: 
<ol>
<li>https://community.home-assistant.io/t/solax-x1-hybrid-g4-worked-example/499362
</li>
<li>https://community.home-assistant.io/t/automated-octopus-saving-sessions-with-solax-x1-hybrid-g4/654502
</li>
<li>https://community.home-assistant.io/t/solax-x1-hybrid-g4-local-cloud-api/506172
</li>
</ol>

# INSTALL INSTRUCTIONS
### Prerequisite Integrations
* Electricity Maps https://www.home-assistant.io/integrations/co2signal/
* HACS https://hacs.xyz/docs/use/
* Octopus Energy (by bottlecapdave) Min v13.5.0 https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/
* Myenergi https://github.com/CJNE/ha-myenergi
* Uptime https://www.home-assistant.io/integrations/uptime/
* Powercalc https://docs.powercalc.nl/quick-start/
* Power Flow Card Plus https://github.com/flixlix/power-flow-card-plus/releases/tag/v0.2.0

### Mandatory Manual Adjustments to Config Yaml & Dashboard Yaml
You must edit and replace instances of Zappi number, Solax registration number, Octopus account details & IP address :
* automations.yaml (automation files need to be cut and paste into your single automation.yaml)
* templates.yaml
* secrets.yaml
* Dashboards
	* Solax & Octopus Settings.yaml
	* Octopus Saving Sessions.yaml
If you have previous used similar Solax automations/config be aware that some rest_command names may have changed. Feed in priority options have been added. Also be aware that some entities have been added in templates.yaml
### Other Adjustments needed
* In the solax package templates.yaml you must adjust the battery size to your battery size and set a flag indicating where your solax CT clamp is. (notes are in the yaml)

### Adding the Dashboards
* Copy the contents of Solax & Octopus Settings.yaml
* Replace zappi_XXXXXXXX with your Zappi number
* Replace z_ZZZZZZZZ with your Octopus account number
* Open Home Assistant
* Open Overview dashboard
* Click Pencil icon in top left
* Click + to add a new dashboard
* New window opens, click the 3 dots in top left corner
* Select Edit in Yaml
* Replace the contents with your prepared yaml
* Click Save
* Click Done

## Revision Log
| Version | Date | Files updated |Description |
|:-----|:--------:|:------|:------|
| v3.1 | **18/03/25** | automations_5001-6002.yaml <br /> Solax & Octopus Settings.yaml  <br /> packages/solax_zappi_octopus |Better notification management & new dashboard additions & Solax System State Control
| v3.0.4 | **12/3/25** | automations_5001-6002.yaml <br /> Solax & Octopus Settings.yaml | 5001 Added a condition to prevent inverter reverting back to default if vehicle was charging prior to a saving session starting. <br /> Added a chart title to dashboard|
| v3.0.3 | **11/3/25** |automations_5001-6002.yaml| 5001 - Added When Condition to ensure inverter mode is reset to default mode when it's time to start charging the solax battery.|
| v3.0.2 | **6/3/25**| All | Added "Zappi always in ECO+ Mode (when connected)" to allow for EV charging from excess solar |
| v3.0.0 | **9/2/25** | All | Primarily this release is aimed at large capacity EV users that also want to export Solax battery on a daily basis. <br /> The feature will be most used in the summer where solar export is higher leaving less hours to charge EV and reducing window over night to discharge and recharge the Solax battery.
| v2.1.4 | **29/1/25** | packages/octopus_saving_sessions/input_boolean.yaml <br/> packages/solax_zappi_octopus/templates.yaml <br/> All automations <br/> Octopus Saving Sessions.yaml (Dashboard)| 1. Added new controls to Saving Sessions Dashboard to attempt to get a dispatch during battery prep and also attempt to get a dispatch straight after session. <br /> 2. Updated EV Start Time logic <br /> 3. Renamed all automations
| v2.1.4 | **28/1/25** | packages/solax/templates.yaml | Improved resilience to sensors reporting defaults/template warnings in logs due to invalid/empty rest responses.
| v2.1.3 | **23/1/25** | packages/octopus_saving_sessions/input_datetime.yaml <br />packages/octopus_saving_sessions/input_number.yaml <br /> packages/octopus_saving_sessions/templates.yaml <br /> packages/solax/templates.yaml <br />  packages/solax_zappi_octopus/templates.yaml <br /> automation 600x.yaml removed <br /> automation 6001.yaml added <br /> automation 6002.yaml added <br /> dashboard/Solax & Octopus Settings.yaml added <br /> dashboard/Octopus Saving Sessions.yaml  |1. Fixed bug with free electric <br /> 2. Fixed bug with battery in from solar calcs <br /> 3. Enhanced Octopus Saving Session Options with prep time and prep SoC with checks to stop charging when the target SoC is reached <br /> 4. Tidier Notifications <br /> |
| v2.1.1 | **19/1/25** | packages/solax_zappi_octopus/templates.yaml |1. Fixed bug with tariff select|
| v2.1  | **19/1/25** | All |1. Revised Dashboards <br /> 2. Added Battery Warming controls <br /> 3. Added Mobile Notifications <br /> 4. New template sensors to switch utility meter tariffs peak/offpeak <br /> 5. General bug fixes in template sensors|

## Automation Function Summary
Automations can take a long time to run. I wish it could be made to be more snappy but the rest_commands aren't reliable. The automations make use of an input_boolean.solax_automation_running set to true to indicate in the UI (and to other automations) that an automation is running. Please be patient and wait for the input_boolean to go off before assuming the automation failed. On the dashboard it should turn red whilst something is running.

### 5001 - Solax Zappi Octopus Control
* Manages the inverter behaviour when Zappi is plugged/unplugged/charging.
* Exports Solax battery on demand or daily during offpeak periods down to 20% SoC.
* Creates Events that can be notified with 5005.
* By selecting "Full Octopus Control" in the UI, as soon as an EV is plugged in Octopus should provide a schedule.
* By selecting "Solar Export Priority" in the UI, Zappi won't get an Octopus schedule until the sun is below a configurable elevation.
* If neither "Full Octopus Control" or "Solar Export Priority" is on then Octopus won't get a schedule until the configured time.
* Zappi always in ECO+ Mode (when connected). This allows excess solar to charge EV.
* "Intelligent Charge Target" amount of energy % of car battery size to be dispatched by Octopus.
* "Intelligent Target Time" target EV ready time.
* "Intelligent Smart Charge" Indicates if Octopus is in control of charging (leave alone and let automation work)
* "myenergi zappi-XXXXXXX Charge Mode" Zappi Mode - (leave alone and let automation work)  
* "Use Grid During Octopus Dispatch" Use this option to use the grid rather than battery when Octopus dispatching (this can be true in off peak hours).
* "Prevent Zappi Draining Battery" Use this option if the CT clamp is positioned in a place that sees Zappi load and consequently discharges the house battery into the EV.
* Solax defaults - set default work mode, Charge to SoC & Min Soc. These values are used to return inverter to some defaults after a battery discharge or EV charge session.
### 5002 - Solax Reset Mode After Manual Discharge
* Monitors the battery SoC and stops the discharge at target SoC
* Triggered whenever a force discharge is in progress
* Multiple target SoC can be set for different scenarios
	* Free electric preparation
	* Saving Sessions
	* Daily Exports
	* Manual Exports
### 5003 - Solax Set UI Options
* When user uses the UI to change a Solax setting rest_command is used to set that option on the inverter.
* Patience is key when changing options. Alter one at a time and wait for the red roboot to go off.
### 5004 - Solax Reload Settings
* Sets the UI options based on whats set on the inverter.
* Triggered whenever a change occurs on the inverter (whenever input_boolean.solax_automation_running changes to off).
* Triggered every 15 minutes.
### 5005 - Solax Zappi Octopus Control - Notifier
* Sends notifications based on Events created in automations.
* Can be turned off by using input_bool.solax_zappi_octopus_control_notifications.
### 6001 - Octopus - Free Electric Automation
* Use the UI to set the day and times of the free electric.
* Use the UI to set the target battery SoC.
* Use the UI to set when the battery should discharge (usually early in morning just in case it's sunny later).
* UI can be used to use the target battery SoC as the "charge to SoC" if you don't wish to export battery.
* The automation will set the Zappi to FAST during free electric period.
### 6002 - Octopus - Saving Sessions Automation
* Template Sensor is required for this to work - sensor.octopus_is_there_a_saving_session_today.
* Automatically joins a session.
* Allows for joining manually.
* Allows for setting a target battery discharge SoC.
* Allows for setting Prep charge to SoC
* Allows for setting of Prep time
* Checks if prep SoC is reached and stops charging
* Prepares the by charging the battery at peak rate or tries to get an Octopus dispatch if Zappi is connected and charges the battery.
* During saving session the zappi is stopped and battery is discharged.
* After saving session a dispatch is requested if Zappi is connected.

## Initial User Requirements
<ol>
<li>Control all Solax G4 Inverter settings locally.</li>
<li>Optionally Prevent Solax battery discharging when Zappi is charging EV.
<ol style="list-style-type: lower-alpha;">
<li>&nbsp;Option needed as depending on where the CT clamp is placed Zappi loads will be seen by inverter</li>
</ol>
</li>
<li>Optionally always use grid during Octopus Dispatch.
<ol style="list-style-type: lower-alpha;">
<li>Optional but suggest its always on if you intend to maximise Battery Export when tarrifs are favourable</li>
</ol>
</li>
<li>Optionally export Solax battery to grid on a daily basis somewhere in off-peak.
<ol style="list-style-type: lower-alpha;">
<li>EV cant be charging.</li>
<li>Solax battery cant be charging.</li>
</ol>
</li>
<li>Optionally maximise solar Export by not starting Zappi until the sun has set. Allows users to plug and forget and guarantee the car will charge after sundown.</li>
<li>Optionally prevent Zappi from starting before a time of day. Allows users a bit of planning to load shift without having to go outside and plug in.</li>
<li>Facilitate Octopus Free Electric Sessions by:
<ol style="list-style-type: lower-alpha;">
<li>Exporting the solax battery before sunrise to a level to reach the Session start.
<ol style="list-style-type: lower-roman;">
<li>User configurable start discharge time.</li>
<li>User configurable battery target SoC.</li>
</ol>
</li>
<li>Setting the inverter to Feed In Priority so the battery doesnt fill from solar.</li>
<li>Setting the start2 and stop2 period.</li>
<li>Enable second period charge option.</li>
<li>Set Zappi to Fast mode so EV starts charging.</li>
<li>Reset Inverter back to a default mode after session.</li>
<li>Reset Zappi to stopped state.</li>
</ol>
</li>
<li>Join Octopus Saving Sessions and manage Solax inverter and Zappi:
<ol style="list-style-type: lower-alpha;">
<li>Automatically or manually join the session:
<ol style="list-style-type: lower-roman;">
<li>Manual option is for when sessions are announced but not via API.</li>
<li>Manual option must still be joined via app/web site.</li>
<li>Manual option allows user to set the start and end manually.</li>
</ol>
</li>
<li>Before Session:
<ol style="list-style-type: lower-roman;">
<li>Charge the Solax battery just before session.</li>
<li>Start Zappi if possible.</li>
</ol>
</li>
<li>During Session:
<ol style="list-style-type: lower-roman;">
<li>Export the Solax battery during the session.</li>
<li>Stop Zappi during this time.</li>
<li>Stop Solax battery discharge if target min SoC is reached and return to default mode</li>
</ol>
</li>
<li>After Session:
<ol style="list-style-type: lower-roman;">
<li>Return inverter to default mode when session ends (if its still discharging).</li>
</ol>
</li>
</ol>
</li>
</ol>

## Future Dev Work
<ol>
<li>Add functionality to set the 'Charge to Target SoC' dynamically based on a solar forecast. Currently low priority as Octopus offer 15p export rate where import is 7p so it makes sense to dump the battery before charging.</li>
</ol>

## Problems Found During Development
<ol>
<li>Zappi relies on a connection to cloud and the API used is sketchy and often reports unknown or unavailable. This is an issue for the main automation which relies on transitions 'From' and 'To' states. To get around this a new sensor was defined for the 'plug status' that remains at the previous known state whilst the API recovers.</li>
<li>I've seen a Zappi plug status 'Fault' twice during the development. The first time it occurred the Zappi required physical interaction. Myenergi ignored my request of support but googling led me to conclude the fault was due to the connecter interface lead between the main board and the display wasn't properly connected. The second time it recovered and plug status went from 'Fault' to 'Charging'. Both instances occurred whilst attempting to start charging. Whilst I've attempted to account for these scenarios in the automations, no guarantees.</li>
<li>Solax rest commands are slow and somewhat unreliable, stacking them is tricky, methods to tackle this have already been demonstrated in https://community.home-assistant.io/t/solax-x1-hybrid-g4-local-cloud-api/506172<br />solax_local_settings_payload and solax_local_realtime_payload sometimes returns empty or 0's in the payload. Not sure how to overcome this but it can cause some unreliability in automations. Even with the loop retry methods employed, failures to correctly set the inverter can slip past the loop protection undetected. An attempt to protect from failures are the delays introduced in the top of the automation variables (saves searching through and adjusting every instance)</li>
<li>Reboots/restarts can trigger the main automation, I've used an integration called "uptime" to check if the last reboot was within last 80 seconds.</li>
<li>Battery Warming - Even through the official web ui I've seen issues/errors which won't allow the setting times or enabling/disabling the option. The first time I paniced and thought my rest command had broken the inverter so tried rebooting it. This didn't work. After leaving it alone for sometime (about 12 hours) everything was back to normal and settings could be adjusted again. Strange</li>
</ol>

## Equipment Used During Development
<ol>
<li>Solax X1-G4 Inverter</li>
<li>Solax 9kWh Battery</li>
<li>Wired LAN Connection to Inverter</li>
<li>Wired LAN to Zappi</li>
</ol>




