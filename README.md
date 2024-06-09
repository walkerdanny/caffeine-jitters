# Caffeine Jitters app
## A companion app for the Club Mate Hexpansion

#### I told you I'd write the software some day

If you got an assembled version of the Club Mate Hexpansion from me at EMF Camp 2024, this is an app that makes it actually do something!

It's based mostly on the [Adafruit DRV2605 CircuitPython Library](https://github.com/adafruit/Adafruit_CircuitPython_DRV2605) and I take absolutely no credit for any of their great work.

Because it's based on the Adafruit library, the [Adafruit Docs](https://docs.circuitpython.org/projects/drv2605/en/latest/) can be used to build your own apps rather than me having to actually do docs! Yay!

As is often the way with these things, it's not 100% reliable - the badge doesn't always detect the Hexpansion properly etc. This will improve as the badge firmware improves.

## Note:

In order to make the app work, the EEPROM on the badge needs to be provisioned first. This wasn't done before I was handing them out because the software was borked, so you'll have to do it yourself. Don't worry, I trust you.

To provision the EEPROM, follow **steps 1-5** in the [hexpansion documentation](https://tildagon.badge.emfcamp.org/hexpansions/eeprom/), but for step 4, use the following header information:
```
header = HexpansionHeader(
    manifest_version="2024",
    fs_offset=32,
    eeprom_page_size=32,
    eeprom_total_size=256*32,
    vid=0xCAFE,
    pid=0xCAFF,
    unique_id=0x0,
    friendly_name="Caffeine!",
)
```

Then you should be all good to go!

## Building on this

Feel free to build your own apps for the hexpansion based on this - this is only a proof of concept to show how it can be done. There are hundreds of effects on the DRV2605 chip, and they can be chained together to make sequences if you want. If you do build something for it, let me know, I'd love to see it!
