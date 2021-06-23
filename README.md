# Prusa Connect integration for Home Assistant
[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

This integration allows you to get current state of your printer via Prusa Connect API.
It should be mostly compatible with the official 
[OctoPrint integration](https://www.home-assistant.io/integrations/octoprint/)
allowing you to use existing custom cards, for example 
[threedy](https://github.com/dangreco/threedy).

If a custom card or something else intended for OctoPrint does not work, please report 
it as a bug.


## Installation
---

### HACS

1. Open _HACS_ and navigate to _Integrations_ Section
2. Open the Overflow Menu (⋮) in the top right corner and click on _Custom repositories_
3. Paste `https://github.com/landmaj/prusa_connect` into the input field and select `Integration` from the dropdown
4. Click the Install Button on the highlighted Card titled _Prusa Connect_
5. Add entry in `configuration.yaml`
6. Restart Home Assistant

### Manual

1. Download the repository as a ZIP package and extract it
2. Copy `custom_components` directory to your `config` directory (this is where your `configuration.yaml` lives)
3. Add entry in `configuration.yaml`
4. Restart Home Assistant


## Configuration
---
Add this to `configuration.yaml`:
```yaml
prusa_connect:
  - host: 192.168.1.2
    name: Prusa Mini
    sensors:  # optional
      monitored_conditions:  # optional, defaults to ALL
        - "Current State"
        - "Job Percentage"
        - "Nozzle Temperature"
        - "Bed Temperature"
        - "Time Elapsed"
        - "Time Remaining"
        - "Project Name"
        - "Material"
```

## Screenshots
---

### In combination with [threedy](https://github.com/dangreco/threedy)
![threedy](https://github.com/landmaj/prusa_connect/raw/master/threedy.png)
