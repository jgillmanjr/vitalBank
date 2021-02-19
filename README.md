vitalBank
=========

# U wot m8?
You're probably wondering why I made this garbage, given that there's already a way to make banks from within Vital, right?

Well, sure.

But maybe you don't want to manually select stuff. Or something.

Or maybe you are working on multiple banks.

Or maybe I just wanted an excuse to code.

Who knows, but this thing is here. And it's awful.

# Whatever, just show me how to use this thing.
Yeah, well, fine then.

## Config
So first thing is to make a config file. Just look at `config.json.example` as a reference.

Basically you're going to be setting the `base_preset_dir`, which is the directory where Vital installs Presets and LFOs and all the other stuff.

Then you specify the directory name (in relation to the `base_preset_dir`) where you want to output the vital bank(s).

Then you specify the delimiter. This is what separates the bank name from the preset name.

## Make content
Now, obviously you gotta make content.

When naming, regardless if it's a patch, LFO, or wavetable, do it in the format `bankname [delimiter] object name`.

So for example: `Garbage Pack: Part Deux $$ This Preset is Awful`.

## Run bankify
So.. I developed this against Python 3.8.

I'm guessing 3.7 should work and probably 3.6. But who knows.

Anyway so really all you need to do is run `python bankify.py` and then go look at your bank directory and, well there you are.

You should have your bank(s) all wrapped up.

# Things to know
For this initial release, the source files do not get deleted. Hell, there aren't any arguments you can pass in.

It's literally just the script for now. I'll probably change that later, but, proof of concept or something.