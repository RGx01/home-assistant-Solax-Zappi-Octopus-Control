# Solax-Zappi-Octopus-Control

* [Introduction](#introduction)
* [Revision Log](#revision-log)
* [Screenshots](#screenshots-of-dashboards)
* [Credits and Acknowledgments](#credits-and-acknowledgments)
* [INSTALL INSTRUCTIONS](#install-instructions)
	* [Prerequisite Integrations](#prerequisite-integrations)
	* [Mandatory Manual Adjustments to Config Yaml & Dashboard Yaml](#mandatory-manual-adjustments-to-config-yaml--dashboard-yaml)
	* [Adding the Dashboards](#adding-the-dashboards)
* [Automation Function Summary](#automation-function-summary)
	* [5001 - Solax Zappi Octopus Control](#5001---solax-zappi-octopus-control)
	* [5002 - Solax Reset Mode After Manual Discharge](#5002---solax-reset-mode-after-manual-discharge)
	* [5003 - Solax Set UI Options](#5003---solax-set-ui-options)
	* [5004 - Solax Reload Settings](#5004---solax-reload-settings)
	* [5005 - Solax Zappi Octopus Control - Notifier](#5005---solax-zappi-octopus-control---notifier)
	* [6001 - Octopus - Free Electric Automation](#6001---octopus---free-electric-automation)
	* [6002 - Octopus - Saving Sessions Automation](#6002---octopus---saving-sessions-automation)
* [User Requirements](#user-requirements)
* [Future Dev Work](#future-dev-work)
* [Problems Found During Development](#problems-found-during-development)
* [Equipment Used During Development](#equipment-used-during-development)
  
## Introduction
This started out as a Home Assistant project to create a UI to control my Solax inverter locally. It's now a project to automate the contol of the my Solax inverter, Zappi EV charger and Octopus Energy interactions including Octoplus Saving Sessions and Free Electric sessions. The idea isn't entirely new (see credits below) but the project now goes beyond my original idea and now provides the opportunity to automatically contol for scenarios (decribed in the requirements below). 

The project is split into 3 parts:
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

## Revision Log
| Version | Date | Files updated |Description |
|:-----|:--------:|:------|:------|
| v3.0.3 | **11/3/25** |automations_5001-6002.yaml| 5001 - Added When Condition to ensure inverter mode is reset to default mode when it's time to start charging the solax battery.|
| v3.0.2 | **6/3/25**| All | Added "Zappi always in ECO+ Mode (when connected)" to allow for EV charging from excess solar |
| v3.0.0 | **9/2/25** | All | Primarily this release is aimed at large capacity EV users that also want to export Solax battery on a daily basis. <br /> The feature will be most used in the summer where solar export is higher leaving less hours to charge EV and reducing window over night to discharge and recharge the Solax battery.
| v2.1.4 | **29/1/25** | packages/octopus_saving_sessions/input_boolean.yaml <br/> packages/solax_zappi_octopus/templates.yaml <br/> All automations <br/> Octopus Saving Sessions.yaml (Dashboard)| 1. Added new controls to Saving Sessions Dashboard to attempt to get a dispatch during battery prep and also attempt to get a dispatch straight after session. <br /> 2. Updated EV Start Time logic <br /> 3. Renamed all automations
| v2.1.4 | **28/1/25** | packages/solax/templates.yaml | Improved resilience to sensors reporting defaults/template warnings in logs due to invalid/empty rest responses.
| v2.1.3 | **23/1/25** | packages/octopus_saving_sessions/input_datetime.yaml <br />packages/octopus_saving_sessions/input_number.yaml <br /> packages/octopus_saving_sessions/templates.yaml <br /> packages/solax/templates.yaml <br />  packages/solax_zappi_octopus/templates.yaml <br /> automation 600x.yaml removed <br /> automation 6001.yaml added <br /> automation 6002.yaml added <br /> dashboard/Solax & Octopus Settings.yaml added <br /> dashboard/Octopus Saving Sessions.yaml  |1. Fixed bug with free electric <br /> 2. Fixed bug with battery in from solar calcs <br /> 3. Enhanced Octopus Saving Session Options with prep time and prep SoC with checks to stop charging when the target SoC is reached <br /> 4. Tidier Notifications <br /> |
| v2.1.1 | **19/1/25** | packages/solax_zappi_octopus/templates.yaml |1. Fixed bug with tariff select|
| v2.1  | **19/1/25** | All |1. Revised Dashboards <br /> 2. Added Battery Warming controls <br /> 3. Added Mobile Notifications <br /> 4. New template sensors to switch utility meter tariffs peak/offpeak <br /> 5. General bug fixes in template sensors|

## Screenshots of Dashboards
![solaxzappioctopus](https://github.com/user-attachments/assets/ed80306d-c862-40f7-ad16-47ee9838e429)
<img width="1207" alt="Screenshot 2025-03-06 at 20 11 55" src="https://github.com/user-attachments/assets/44013fc3-7c7b-41c9-ab21-6778dde9abfe" />

<img width="1383" alt="Screenshot 2025-01-28 at 00 06 56" src="https://github.com/user-attachments/assets/ceebc259-8b7b-4d51-866f-246c647efdd2" />
<img width="1182" alt="Screenshot 2025-03-06 at 20 12 22" src="https://github.com/user-attachments/assets/23123dff-883c-4e59-9e33-f15392cab157" />
<img width="525" alt="Screenshot 2025-01-29 at 17 01 42" src="https://github.com/user-attachments/assets/4413fdbe-e1ce-46bd-a021-929edd766c1f" />



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
* HACS
* Octopus Energy (by bottlecapdave) v13.5.0 
* Myenergi
* Uptime
* Powercalc

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

## User Requirements
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




