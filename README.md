# Solax-Zappi-Octopus-Control
Written specifically for IOG Zappi and Solax X1-G4 Inverter
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
* Octopus Energy (by bottlecapdave) https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/
    - must be configured
    - must have the free electric entity enabled (not done by default, manual process)
* Myenergi https://github.com/CJNE/ha-myenergi
    - must be configured
* Uptime https://www.home-assistant.io/integrations/uptime/
* Powercalc https://docs.powercalc.nl/quick-start/
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
4. .\config\packages\solax_realtime\secrets.yaml
     - Find and replace YYYYYYYYYY with your registration number (found on the devices page on the solax cloud)
     - Find http://192.168.xxx.xxx and replace with http://192.168.1.fixed_ip
5. .\config\packages\solax_control\secrets.yaml
     - Find and replace YYYYYYYYYY with your registration number (found on the devices page on the solax cloud)
     - Find http://192.168.xxx.xxx and replace with http://192.168.1.fixed_ip
6. .\config\packages\octopus_renamed_entities\template.yaml
     - Find and replace all octopus account number z_ZZZZZZZZ with your own i.e. a_42036969
7. .\config\packages\solax_zappi_octopus\utility_meters.yaml
    - Find ev_charging_daily_vehicle and replace the vehicle names and set them as you wish
    - Find ev_charging_monthly_vehicle and replace the vehicle names and set them as you wish
8. .\config\packages\octoplus_sessions\template.yaml
    - Find and replace all octopus account number z_ZZZZZZZZ with your own i.e. a_42036969
9. .\config\packages\zappi_renamed_entities\template.yaml
    - Find and replace all zappi serial numbers zappi_XXXXXXXX with your own i.e. zappi_12345678
10. Copy the contents of automations_5001-6001.yaml to the bottom of .\config automations.yaml
11. Edit your configuration.yaml to pick up the new packages.

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
    - under 'Pre-emptive Battery Exports' set: 
        - Solax Battery SoH Stored initial value to 100 (it will recalucate each time a full charge cycle)
    - forced discharge limit for both 'prior to ev charging' and 'nightly discharge'.
    - select Octopus schedule type
    - EV registered battery size
    - EV ready time
    - EV charge %
16. Done.

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
| v5.6.1|**20/09/25**|octopus_renamed_entities\templates <br>solax_zappi_octopus\templates.yaml | BUG Fix with clamping of pre emptive and sensor thrashing of octopus mirror sensors|
| v5.6.0|**20/09/25**|octopus_renamed_entities\templates <br>solax_zappi_octopus\templates.yaml <br>solax_zappi_octopus\utilitymeter.yam| Duplicting attributes for octopus dispatch sensor so easier to install, also removed dependancy on zappi serial number in utility meter |
| v5.5.0|**20/09/25**|automations_5001-6001.yaml <br>solax_zappi_octopus\templates.yaml| Improved pre emptive discharges|
| v5.4.1|**18/09/25**|automations_5001-6001.yaml <br>solax_zappi_octopus\templates.yaml| bug fixes missing from previous release|
| v5.4.0|**18/09/25** |automations_5001-6001.yaml <br> octoplus_sessions\templates.yaml <br> solax_zappi_octopus\input_boolean.yaml <br> solax_zappi_octopus\input_datetime.yaml <br> solax_zappi_octopus\input_number.yaml <br> solax_zappi_octopus\templates.yaml <br> Solax & Octopus Settings.yaml (the dashboard)| Added Daily Exporting for when EV is disconnected. Supports pre-emptive discharge so you can aim for a SoC to reach at a specific time|
| v5.3.0| **17/09/25** | automations_5001-6001.yaml <br> solax_zappi_octopus\templates.yaml <br> solax_zappi_octopus\input_number.yaml <br> Solax & Octopus Settings.yaml (the dashboard) | Introducing safe switching of octopus_intelligent_smart_charge. Sometimes the API fails when kraken endpoits are unreachable. This is an attempt to trap and notify if this happens. <br> Fixed bug with solax_local_battery_in_from_solar sensor <br> Added  Battery true capacity based on grid stored/theoretical stored = Capacity SoH. This refines predictions of time to discharge before charging EV and discharging battery before 23:30. To get the calculation to work you must charge from 10 -100% periodicallly <br> Dashboard tweak|
| v5.2.0| **15/09/25** | automations_5001-6001.yaml <br> octoplus_sessions\templates.yaml| Corrected Typo in octoplus sessions that may effect end time not being used correctly <br> Ajusted 6001 to end 2 min charging early to make sure dispatch qits on time|
| v5.1.1| **14/09/25** | automations_5001-6001.yaml|Fixed bug in Free Electric notification where end time was announced as start time|
| v5.1.0| **13/09/25**| solax_additions deleted <br> solax_realtime added <br> solax_zappi_octopus has new files | solax_additions deleted and replaced with solax_realtime <br> anything that was in solax additions that wasn't to do with realtime data is moved to solax_zappi_octopus|
| v5.0.1| **12/09/25**| solax_zappi_octopus\input_number.yaml <br>solax_zappi_octopus\templates.yaml <br> Solax & Octopus Settings.yaml (the dashboard)|  Added a configurable export margin delta for when preemptive discharges under estimate<br> Fixed an issue where an EV may not get fully charged if it's plugged in after the pre export battery time |
| v5.0  | **12/09/25**| All | Major refactor |

# Known Issues
- fixed ~~in Automation 5001 Option 3, there is a known issue which I plan to fix soon where if the EV is connected after the predicted EV start time and the option is set to discharge the house battery you may not get the full EV charge.~~
