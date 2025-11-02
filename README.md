# Solax-Zappi-Octopus-Control
Written specifically for IOG Zappi and Solax X1-G4 Inverter
Main features:
1. Control Inverter settings locally with REST.
2. Option - Daily discharge to a Target SoC based on typical usage
3. Option - Just in Time discharge to 10% by 23:30
4. Option - Discharge between gaps in Octopus Dispatch (aim for Target SoC based on typical usage)
5. Handling of CT clamps in different positions on the Henley block.
6. User notifications to mobile devices.
7. Handles Free Electric Sessions from Octoplus.
8. ~~Handles Saving Sessions~~. Removed
9. Calculates Capacity SoH on each full recharge.

![delme](https://github.com/user-attachments/assets/c2eb91f9-8c83-4f31-8a76-75df950f1d05)


* [INSTALL INSTRUCTIONS](#install-instructions)
	* [Prerequisite Integrations](#prerequisite-integrations)
	* [Steps](#steps)
* [Notification Management](#notification-management)
* [Equipment Used During Development](#equipment-used-during-development)
* [Credits and Acknowledgments](#credits-and-acknowledgments)
* [Revision Log](#revision-log)
* [Known Issues](#known-issues)
 
# INSTALL INSTRUCTIONS

### Prerequisite Integrations
* HACS https://hacs.xyz/docs/use/
* Electricity Maps https://www.home-assistant.io/integrations/co2signal/
    - must be configured
* Octopus Energy (by bottlecapdave) V17 https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/
    - must be configured
    - must have the free electric entity enabled (not done by default, manual process)
* Myenergi https://github.com/CJNE/ha-myenergi
    - must be configured
* Uptime https://www.home-assistant.io/integrations/uptime/
* Powercalc https://docs.powercalc.nl/quick-start/
* Pyscript Python scripting https://github.com/custom-components/pyscript/wiki 
* Power Flow Card Plus https://github.com/flixlix/power-flow-card-plus/releases/tag/v0.2.0
* Solcast https://github.com/BJReplay/ha-solcast-solar?tab=readme-ov-file#configuration
    - must be configured

## Steps
First back up your Home Assistant. Make sure you are familar with Developer Tools and the Check Configuration button. There shouldn't be any issues but backup's are handy.

### Configuration yaml and Packages

1. Navigate to the home assistant config directory where configuration.yaml resides, create a two new directories
   - packages
   - scripts
2. Copy repo 'package' directory contents to your package directory (6 new directories each with yaml files)
3. Copy repo 'script' contents to your script directory (two yaml files)
4. Copy repo 'pyscript' contents to your pyscript directory (pyscript must be added first via HACS and added as an integration first)
5. .\config\packages\solax_realtime\secrets.yaml
     - Find and replace YYYYYYYYYY with your registration number (found on the devices page on the solax cloud)
     - Find http://192.168.xxx.xxx and replace with http://192.168.1.fixed_ip
6. .\config\packages\solax_control\secrets.yaml
     - Find and replace YYYYYYYYYY with your registration number (found on the devices page on the solax cloud)
     - Find http://192.168.xxx.xxx and replace with http://192.168.1.fixed_ip
7. .\config\packages\octopus_renamed_entities\template.yaml
     - Find and replace all METER_MPAN with your own
     - Find and replace all L_O_N_G_ZAPPIID with your own
8. .\config\packages\solax_loads\utility_meters.yaml
    - Find and set the billing period offsets you require
9. .\config\packages\zappi_loads\utility_meters.yaml
    - Find and set the billing period offsets you require
    - Find ev_charging_daily_vehicle and replace the vehicle names and set them as you wish
    - Find ev_charging_monthly_vehicle and replace the vehicle names and set them as you wish
10. .\config\packages\octoplus_sessions\template.yaml
    - Find and replace all octopus account number z_ZZZZZZZZ with your own i.e. a_42036969
11. .\config\packages\zappi_renamed_entities\template.yaml
    - Find and replace all zappi serial numbers zappi_XXXXXXXX with your own i.e. zappi_12345678
12. Copy the contents of automations_5000-5005.yaml to the bottom of .\config automations.yaml
13. Edit your configuration.yaml to pick up the new packages.

Rather than putting all the config in the single '\config\configuration.yaml file, to keep things clean and tidy and more manageable, the package files can referenced like this in the configuration.yaml:
In the example below see the use of the homeassistant: tag. The directory referenced under homeassistant: tag is the packages directory where we've already stored all the new config. You must also add the script directory. if you already have a scripts.yaml that should be moved to the scripts directory.

```yaml
default_config:

logger:
  default: info
  logs:
    homeassistant.components.rest: info

frontend:
  themes: !include_dir_merge_named themes

homeassistant:
  packages: !include_dir_merge_named packages
script: !include_dir_merge_named scripts  
automation: !include automations.yaml
```
12. Check all the steps above have been done.
13. Restart Home Assistant.
14. Adding the dashboad.
    - Copy the contents of Solax & Octopus Settings.yaml in the repo
    - Open Home Assistant
    - Open Overview dashboard
    - Click Pencil icon in top left
    - Click + to add a new dashboard
    - New window opens, click the 3 dots in top left corner
    - Select Edit in Yaml
    - Replace the contents with your prepared yaml
    - Click Save
    - Click Done
15. On the dashboard select/set:
    - solax battery size,
    - solax inverter size,
    - default inverter mode.
    - default charge to level
    - default min_soc
    - Solax Battery SoH Stored initial value to 100 (it will recalucate each time a full charge cycle 10-100%)
    - select Octopus schedule type
    - EV registered battery size 
    - EV ready time
    - EV charge %
16. Battery Reserves
    - Set your initial typical average power in kW (eg 0.300)
    - Set how much reserve you want in % and/or set how many hours of extra running you'd like to reserve
      - This is used for the limit on where automatic discharges (GAP and Daily) will discharge too at any point in the day.
      - Note that nightly discharges don't use this limit, they discharge to the default min soc. 
17. Done.

# Notification Management

<ol start=1>
	<li>Notifications - Turn this on in the Dashboard to receive notifications both in HA and any mobile device selected.</li>
	<li>Notify Mobile device - A dropdown list of all mobile devices with the Home Assistant companion app installed. Select one or more devices to receive notifications generated by the automations. Reselecting a device will remove it from receiving notifications.</li>
	<li>Reset Device List - pressing this button will remove all devices selected to receive notifications. </li>
	<li>Notifications to Exclude - A complete list of notifications. Selecting notifications in the list will disable them from being notified. </li>
	<li>Reset Notification Exclusions - After pressing this, all notifications will notified on.</li>
	<li>Summary of which devices and which notifications are excluded.</li>
</ol>

# Equipment Used During Development
<ol>
<li>Solax X1-G4 Inverter</li>
<li>Solax 9kWh Battery</li>
<li>Wired LAN Connection to Inverter</li>
<li>Wired LAN to Zappi</li>
</ol>

# Credits and Acknowledgments
The Solax interactions are possible due to work published by @Colin Robbins and @Kamil Baczkowicz. I've tried to simplify things by putting their work into a package. Essentially it becomes a building block for my automations and dashboards. Suggested reading: 
<ol>
<li>https://community.home-assistant.io/t/solax-x1-hybrid-g4-worked-example/499362
</li>
<li>https://community.home-assistant.io/t/automated-octopus-saving-sessions-with-solax-x1-hybrid-g4/654502
</li>
<li>https://community.home-assistant.io/t/solax-x1-hybrid-g4-local-cloud-api/506172
</li>
</ol>

# Revision Log
| Version | Date | Files updated |Description |
|:------|:--------:|:------|:------|
| v6.2.1|**02/11/25**|All| Bug fix - incorrect export template for myenergi ct clamp <br> Bug fix - incorrect export template for myenergi ct clamp <br>Updated Dashboard <br> New entity for solax_grid_stored_at_first_max_soc with attributes to record max SoC and time of max SoC. This helps get a better read on SoH if charge windows ar large and battery heating is on 
<br> Automation 5001 updated with a new message title for when EV is paused
<br> Ehancments to target SoC calculation|
| v6.2.0|**31/10/25**|All| Bug fixes <br> Updated Dashboard <br> Added protection for if inverter is left in manual mode for 5 minutes and not doing anything|
| v6.1.0|**30/10/25**|All| bug fixes and restructured yaml packages <br> new feature that calculates typical kW based on user input Days to Use and Start and End Time periods to average over. This enabales user to set the Target SoC (used by automatic GAPS and Daily Discharge) around their highest typical usage times. Uses pyscript.|
| v6.0.2|**29/10/25**|All| bug fixes and restructured yaml packages|
| v6.0.0|**21/10/25**|All| new architecture - ident-potent inverter/zappi control|

# Known Issues
1. Latest release of Octopus Energy (by bottlecapdave) V17 has a deprication notice for the free electric entities in May 2026
    - This means new development required so that users can Prep the SoC for the upcoming session.
