# Solax-Zappi-Octopus-Control
## Version 10.0.0 is here. Big Changes to Dashboard

Written specifically for IOG Zappi and Solax X1-G4 Inverter and TP3.0 Battery - MAY NOT BE COMPATIBLE WITH YOUR SYSTEM
If unsure if your inverter can be controlled try using https://github.com/RGx01/Solax-Local-Control-Using-REST if successful control can be established then proceed with companion https://github.com/RGx01/Solax-Local-Realtime-Using-REST. This repo bundles those but in the future they will become pre requiste. (Ideally if others contribute with other inverters.)
Main features:
1. Control inverter settings locally with REST. No need to be connected to Solax Cloud for any reason besides any firmware updates.
2. Read realtime inverter data locally.
3. Option - Daily discharge to a Reserve SoC based on your typical usage (Battery Budget enhancements from 7.0.0)
4. Option - Just in Time discharge to 10% by 23:30
5. Option - Discharge between gaps in Octopus Dispatch (aim for Target SoC based on typical usage)
6. Handling of CT clamps in different positions on the Henley block.
7. Create statistics.
8. User notifications to mobile devices.
9. Handles Free Electric Sessions from Octoplus. 
10. ~~Handles Saving Sessions~~. Removed
11. Calculates $Capacity\ Factor = \frac{\text{Grid Stored}}{\text{Theoretical Capacity}}$ on each full recharge.
12. Sets Octopus Intelligent Charge Target based on EV SoC and based on 6hr charge limit rules coming in Jan 2026


<img alt="Screenshot 2025-12-30 at 09 04 41" src="https://github.com/user-attachments/assets/667bde96-4197-423d-80dc-707538df08fd" width="20%"/></img> 
<img alt="Screenshot 2025-12-30 at 09 01 58" src="https://github.com/user-attachments/assets/69bbc5ed-a7f7-4f5c-b3d4-c5e5f8cdc695" width="20%"/></img> 
<img alt="Screenshot 2025-12-30 at 09 02 29" src="https://github.com/user-attachments/assets/e46dfd25-989f-44eb-937b-92c627203b4d" width="20%"/></img> 
<img alt="Screenshot 2025-12-30 at 09 02 44" src="https://github.com/user-attachments/assets/33eac03f-5043-4d3a-b03a-c3dcb83ec57a" width="20%"/></img> 
<img alt="Screenshot 2025-12-30 at 09 03 10" src="https://github.com/user-attachments/assets/1faeac4e-87f8-4d0b-9ac9-e73e70322156" width="20%"/></img> 
<img alt="Screenshot 2025-12-30 at 09 03 33" src="https://github.com/user-attachments/assets/0516234f-c96b-42e2-9c68-e09d14042687" width="20%"/></img> 
<img alt="Screenshot 2025-12-30 at 09 03 54" src="https://github.com/user-attachments/assets/a7d1648e-7376-4695-99e5-1a2116d4dd85" width="20%"/></img> 
<img alt="Screenshot 2025-12-30 at 09 16 33" src="https://github.com/user-attachments/assets/b4878f1d-dc1b-444b-b4b1-3f88eb8f5a4c" width="20%"/></img> 
<img alt="Screenshot 2025-12-30 at 09 04 10" src="https://github.com/user-attachments/assets/53f83fb9-cc26-4c5b-addf-06eed23cf150" width="20%"/></img> 




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
7. 
8. .\config\packages\solax_loads\utility_meters.yaml
    - Find and set the billing period offsets you require
9. .\config\packages\zappi_loads\utility_meters.yaml
    - Find and set the billing period offsets you require
10. .\config\packages\connected_ev_tracking\utility_meters.yaml
    - Find ev_charging_daily_vehicle and replace the vehicle names and set them as you wish
    - Find ev_charging_monthly_vehicle and replace the vehicle names and set them as you wish
11. .\config\packages\connected_ev_tracking\template_ev_mapper.yaml
    - Modify connected_ev_battery_size to match the utility meter tariffs in connected_ev_tracking\utility_meters.yaml
    - Create a binary_sensors representing the EV('s) connected status and a sensor representing the battery level in the format: 
        - binary_sensor.'EV1'_plugged_in e.g. binary_sensor.tesla_model_3_plugged_in
        - sensor.'EV1'_battery_level e.g. sensor.tesla_model_3_battery_level
        - Examples
```yaml
template:
  - sensor:
    - name: Tesla Model 3 Battery Level
      unique_id: tesla_model_3_battery_level
      state: >-
        {# represent you battery level here #}
        {{ states('sensor.tesla_battery_level') }} 
      unit_of_measurement: "%"
      device_class: battery
  - binary_sensor:
    - name: Tesla Model 3 Plugged In
      unique_id: tesla_model_3_plugged_in
      state: >-
        {# represent you plugged in status here #}
        {{ states('binary_sensor.tesla_plugged_in') }}
      device_class: connectivity
```

12. 
13. Copy the contents of automations_5000-5005.yaml to the bottom of .\config automations.yaml
14. Edit your configuration.yaml to pick up the new packages.

Rather than putting all the config in the single '\config\configuration.yaml file, to keep things clean and tidy and more manageable, the package files can referenced like this in the configuration.yaml:
In the example below see the use of the homeassistant: tag. The directory referenced under homeassistant: tag is the packages directory where we've already stored all the new config. You must also add the script directory. if you already have a scripts.yaml that should be moved to the scripts directory.

```yaml
homeassistant:
  packages: !include_dir_merge_named packages
script: !include_dir_merge_named scripts  
automation: !include automations.yaml
```
15. Check all the steps above have been done.
16. Restart Home Assistant.
17. Adding the dashboad.
    - Create a new Dashboard by
        - Settings > Dasboards > Add Dashboard
        - New Dashboard From Scratch
        - Title > Home Energy
        - Create
    - Select the new Home Energy Dashboard
    - Click Pencil Icon ✏️ in top right corner
    - Select the ⋮ in top right corner
    - Select {} raw configuation editor
    - ctrl + A to select all
    - paste the contents of Solax & Octopus Settings.yaml into the raw configuration editor
    - Click Save
    - Click Done
# Configuring
18. On the dashboard press <img width="106" height="34" alt="Screenshot 2025-12-28 at 15 34 28" src="https://github.com/user-attachments/assets/58a3f4c7-9bf1-4750-8fe2-ccad9702c8b8" />
    - **Note the "Battery Start Charge Time". To get the best Capacity Factor results the battery must be left to settle (the longer the better) after a discharging.**
    - Recommended settings are as follows:
    <img width="444" height="727" alt="Screenshot 2025-11-30 at 06 47 43" src="https://github.com/user-attachments/assets/421e3e4e-7efd-4c64-8856-8ad51fadab7c" />
19. - set:
    	- solax battery size,
    	- solax inverter size,
    	- default inverter mode.
    	- default charge to level
    	- default min_soc
    	- Solax Battery Capacity Factor Stored initial value to 100 (it will recalucate each time a full charge cycle 10-100%)
<img width="468" height="477" alt="Screenshot 2025-11-21 at 13 01 20" src="https://github.com/user-attachments/assets/18159443-f912-4622-ae40-0ed0ebff5422" />  

20. EV Charging <img width="89" height="28" alt="Screenshot 2025-12-28 at 16 03 58" src="https://github.com/user-attachments/assets/e3eee962-2738-4ce4-9a07-0607d24e7229" />

    - select Octopus schedule type
    - EV ready time
    - EV charge %
<img width="461" height="555" alt="Screenshot 2025-11-21 at 13 03 47" src="https://github.com/user-attachments/assets/4d88a31e-6d0c-492d-9390-cf3526036ce4" />

21. # Configuring IOG 6hr Charge Limit
    - <img width="391" height="321" alt="Screenshot 2025-12-28 at 17 20 49" src="https://github.com/user-attachments/assets/71f4055f-6668-4a5f-a347-fa4a40018342" /><img width="386" height="489" alt="Screenshot 2025-12-28 at 17 21 09" src="https://github.com/user-attachments/assets/a10e9ca5-e4b6-4954-b7f8-d54aaf6bee07" />


    - Set an approximate limit of 42kWh. Set Charging Loss Factor to something like 8% to account for AC to DC losses for your EV and Charger (set it to whatever you want, remember that 42kWh would be the batterys charge target but Octopus will dispatch more to account for AC to DC losses and other factors.). There is a fall back that will turn off charging at 6hr's. If you don't care about paying more for exceeding then turn the switch to on to ignore the limiting.
    - **WARNING - if you do not configure the plugged_in or battery_level sensor required to drive the Charge Target you must set the Charge Target manually in the Octopus App or in the area of this dashboard.** see step 11
    
22. Battery Reserves <img width="108" height="31" alt="Screenshot 2025-12-28 at 16 05 42" src="https://github.com/user-attachments/assets/78926f42-b6c3-4212-bc87-3d378510f97b" />

    - In the Battery Reserve Section of the dashboard select:
       - Start Slot (time you start using your battery - e.g. 05:30)
       - End Slot (time you stop using your battery - e.g. 23:30)
       - Interval (15 min interval are possible in short term statistics table)
    - Set how much addition reserve you want in % and/or set how many hours of extra running you'd like to reserve
      - This is used for the limit on where automatic discharges (GAP and Daily) will discharge too at any point in the day.
      - Note that nightly discharges don't use this limit, they discharge to the default min soc.
    <img width="398" height="1498" alt="Screenshot 2025-11-21 at 13 06 12" src="https://github.com/user-attachments/assets/19f806c5-19a9-41b2-9553-3e14339c1598" />
 	<img width="1222" height="741" alt="Screenshot 2025-11-21 at 13 12 26" src="https://github.com/user-attachments/assets/3e2f5a50-50a0-4b70-ba92-8437021f772d" />
	<img width="1223" height="742" alt="Screenshot 2025-11-21 at 13 20 49" src="https://github.com/user-attachments/assets/aaae398c-23a8-4de2-8192-109c38fa3309" />





24. Done.

# Notification Management

<ol start=1>
	<li>Notifications - Turn this on in the Dashboard to receive notifications both in HA and any mobile device selected.</li>
	<li>Notify Mobile device - A dropdown list of all mobile devices with the Home Assistant companion app installed. Select one or more devices to receive notifications generated by the automations. Reselecting a device will remove it from receiving notifications.</li>
	<li>Reset Device List - pressing this button will remove all devices selected to receive notifications. </li>
	<li>Notifications to Exclude - A complete list of notifications. Selecting notifications in the list will disable them from being notified. </li>
	<li>Reset Notification Exclusions - After pressing this, all notifications will notified on.</li>
	<li>Summary of which devices and which notifications are excluded.</li>
</ol>
<img width="394" height="581" alt="Screenshot 2025-11-21 at 13 08 21" src="https://github.com/user-attachments/assets/7e0df8f8-097f-43db-af13-be29a8f1aa31" />

# Equipment Used During Development
<ol>
<li>Solax X1-G4 Inverter</li>
<li>Solax 9kWh Battery TP3.0</li>
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
| v10.1.5|**30/12/25**| Solax & Octopus Settings.yaml (dashboard) | Changes to dashboard|
| v10.1.4|**29/12/25**| Solax & Octopus Settings.yaml (dashboard) | Changes to dashboard|
| v10.1.0|**28/12/25**| Solax & Octopus Settings.yaml (dashboard) <br>  automations_5000-5005.yaml <br> packages\octopus_dispatches\input_boolean.yaml| Change to 6hr limit input_boolean|
| v10.0.0|**28/12/25**| Solax & Octopus Settings.yaml (dashboard) <br>  automations_5000-5005.yaml <br> packages\octopus_dispatches\input_number.yaml<br> packages\octopus_dispatches\template_octopus_dispatch.yaml<br> packages\octopus_renamed_entities\templates.yaml<br> packages\solax_export\input_boolean.yaml<br> packages\solax_export\input_number.yaml<br> packages\solax_export\template_discharge_magic.yaml<br> packages\solax_zappi_octopus\input_boolean.yaml| New Dashboard and bug fixes|
| v9.5.0|**22/12/26**| Solax & Octopus Settings.yaml (dashboard) <br> automations_5000-5005.yaml <br> packages\octopus_renamed_entities\templates.yaml<br> packages\octopus_renamed_entities\templates.yaml<br>packages\octopus_dispatches\input_number.yaml | Renamed entities for Zappi and Octopus are now guessed so no need to modify templates <br> Added charging losses for estimating octopus dispatch|
| v9.4.0|**22/12/26**| Solax & Octopus Settings.yaml (dashboard) <br> automations_5000-5005.yaml <br> packages\octopus_renamed_entities\templates.yaml<br> packages\solax_loads\*| More template and automation hardening <br> renamed the SoH calculations as Capacity Indicator as it's not really a true SoH. I've left the underlying entitity identifiers alone for now|
| v9.3.0|**16/12/26**| automations_5000-5005.yaml <br> packages\octopus_dispatches\template_octopus_dispatch.yaml <br> packages\octopus_renamed_entities\templates.yaml| Hardening for when Octopus api becomes flakey |
| v9.0.0|**10/12/25**| All | Dashboard and template updates to support changes to IOG to limit total charge time to 6hr + a host of bug fixes and tweeks<br> Automation and template hardening <br> Allocator improvements (HA restart required) <br> Fixed bug with template_get_octopus_schedule |
| v8.1.0|**01/12/25**| Solax & Octopus Settings.yaml (dashboard) <br> packages\octopus_dispatches\template_octopus_dispatch.yaml| Dashboard refinement around octopus dispatches |
| v8.0.0|**01/12/25**| ALL | Attempt to work around tiny dispatches and pauses in 5001 <br> Removed dependancy on free electric events sensor.<br> Better dispatch gap calculation logic <br> Better logic for calculating the 'get schedule' <br> Fixed small bug in tariff sensor created after removing free electric dependancy <br> Tiny adjustments to discharge magic and a bug fix to exportable allowence <br> Fixed small bug in the battery budget allocator pyscript <br> Improved battery_budget_schedule pyscript to prevent charge windows impinging on dynamic slots. |
| v7.3.2|**24/11/25**| automations_5000-5005.yaml <br> packages\solax_exports\template_discharge_magic.yaml |Improved logic|
| v7.3.1|**23/11/25**| packages\octopus_dispatches\template_get_octopus_schedule.yaml| Improved logic|
| v7.3.0|**23/11/25**|Solax & Octopus Settings.yaml (dashboard) | filter relevant Settings for the Work Mode selected|
| v7.2.0|**23/11/25**|Solax & Octopus Settings.yaml (dashboard) <br> automations_5000-5005.yaml<br>packages\solax_zappi_octopus_ui\input_button.yaml<br>packages\solax_loads\template_battery_soh.yaml| Removed automation 5003 and replaced with a button on dashboard to apply settings, 5001 was updated to perform the apply setting.|
| v7.1.1|**22/11/25**|packages\octopus_dispatches\template_get_octopus_schedule.yaml| bug fix to anytime not latching properly|
| v7.1.0|**21/11/25**|packages\solax_exports\template_discharge_magic.yaml| Added new trigger for JIT Nightly exports |
| v7.0.0|**20/11/25**|All| New Feature Battery Budget Reserve |
| v6.4.1|**15/11/25**|All templates<br>automations_5000-5005.yaml| Bug Fixes|
| v6.4.0|**15/11/25**|All templates<br>automations_5000-5005.yaml| Bug Fixes and HA2026.5 template compliance requires automations in templates require a domain sensor so I've moved them into automation 5000|
| v6.3.0|**13/11/25**|script\solax_set_mode_and_settings.yaml<br>solax_exports\template_discharge_magic.yaml<br>solax_control\sensor.yaml<br>automations_5000-5005.yaml| Efficency updates and automation improvements|
| v6.2.4|**06/11/25**|script\solax_set_mode_and_settings.yaml<br>solax_loads\template_solax_extras.yaml| Critical Bug fix - solax_set_mode_and_settings forgot a namespace wich causes settings to be ignored when no mode is changed|
| v6.2.3|**05/11/25**|All| Bug fix - solax_grid_stored_at_first_max_soc<br>Updated Dashboard <br> Automation 5001 updated with new trigger to try and detect/protect from out of sync issues with the invertere<br> fixed latching issue with manual discharge<br>improved script efficiency for solax_set_mode_and_settings|
| v6.2.2|**02/11/25**|All| Bug fix - error handling in trigger for solax_grid_stored_at_first_max_soc<br>Updated Dashboard <br> Automation 5001 updated with a differet trigger to detect Peak rate|
| v6.2.1|**02/11/25**|All| Bug fix - incorrect export template for myenergi ct clamp <br> Bug fix - incorrect export template for myenergi ct clamp <br>Updated Dashboard <br> New entity for solax_grid_stored_at_first_max_soc with attributes to record max SoC and time of max SoC. This helps get a better read on SoH if charge windows ar large and battery heating is on <br> Automation 5001 updated with a new message title for when EV is paused <br> Ehancments to target SoC calculation|
| v6.2.0|**31/10/25**|All| Bug fixes <br> Updated Dashboard <br> Added protection for if inverter is left in manual mode for 5 minutes and not doing anything|
| v6.1.0|**30/10/25**|All| bug fixes and restructured yaml packages <br> new feature that calculates typical kW based on user input Days to Use and Start and End Time periods to average over. This enabales user to set the Target SoC (used by automatic GAPS and Daily Discharge) around their highest typical usage times. Uses pyscript.|
| v6.0.2|**29/10/25**|All| bug fixes and restructured yaml packages|
| v6.0.0|**21/10/25**|All| new architecture - ident-potent inverter/zappi control|

# Known Issues
1. None at this time
