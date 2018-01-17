<h1> IP Location Finder </h1>

This is a Python + Javascript application that shows where IP addresses and hostnames are located on a Google Maps page. 

This app uses the API from freegeoip.net to find the geographic location of IP addresses.

The App also utilizes the following libraries:
<ul>
    <li>Tornado as a WebSocket server</li>
    <li>Bulma for simple CSS</li>
    <li>Zepto.js as a minimal substitute for jQuery </li>
    <li>Lodash as a JavaScript utility </li>
</ul>

App Features
<ul>
    <li>IP address validation</li>
    <li>'Find All' button for searching and locating multiple IP addresses asynchronously</li>
    <li>In memory cache to limit number of requests to the API</li>
    <li>Displays icons associated with IP instead of simple markers</li>
</ul>

Building Instructions:
<ol>
    <li>For Linux and MacOS bootsrap the environment by using following commands:
        ```$ ./bootstrap.sh
           $ source .env/bin/activate
        ```
    </li>
    <li>Start the server by using: 
        ```$ python mapthingy/server.py```
    </li>
    <li> Point the browser to http://localhost:8888
    </li>
</ol>
