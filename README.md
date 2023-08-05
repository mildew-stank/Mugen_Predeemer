<img align="left" height="420" src="https://i.imgur.com/LYtxyMV.jpg">

# Usage
This can create a channel point reward that may be redeemed to send an AI vs AI fight request back to the program. It will recieve a list of requests and you will be given the option to launch Mugen straight into the fight or issue a channel point refund. A prediction will be created before the fight begins, by default, but the result must be chosen manually.

# Setup
Authorize Predeemer [here](https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=ah4yv3x5c0h7ma514krs9von6xwgm7&redirect_uri=http://localhost&scope=channel%3Amanage%3Aredemptions+channel%3Amanage%3Apredictions), then copy your access_token from the URL bar after being redirected to an invalid web page.

Run mugen_twitch_integration.pyw and enter the access_token along with your mugen directory and desired motif/screenpack to begin.

Your viewers will need to know what characters can be requested, and for that you can go to *Options* > *Export fighter names*. A list of all display names available to the motif will be generated in *cache/fighters.txt*. How that gets to the viewers is up to you, but I suggest using [Pastebin](https://pastebin.com/).

# Build
Download [Python](https://www.python.org/) and run "pip install -r requirements.txt" in a terminal from the project directory, or run "pip install pyqt5" and "pip install requests" from any directory.

# Known issues
Twitch rewards and predictions are only available to partnered streamers, not developers. I have no way to properly test this program, so keep an eye on the status bar at the bottom for errors. A detailed error log will be generated in the *cache* folder. The worst that can happen is you'll end up having to managing the rewards and predictions on your own.
