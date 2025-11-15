# WDR3 Concert Downloader

Downloads any live recording mp3 file encountered on a WDR3 concert player 
website. This feature is useful, if no mp3 file download button is 
dispositional to the audience and, moreover, the mp3 stream is available 
only for a limited re-listening period after its broadcast.

From the address bar of your web browser copy the url of the 
website, where the concert resides and execute the following command:

    $ python3 WDR3_concert_downloader/ [-h] [-o <file>.mp3] <url>

where e.g.
url = https://www1.wdr.de/radio/wdr3/programm/sendungen/wdr3-konzert/konzertplayer-klassik-tage-alter-musik-in-herne-concerto-romano-alessandro-quarta-100.html

If multiple mp3 media objects are available on the website provided,
all files will be downloaded in the order the objects are 
encountered in the html soup scan. The naming of the downloaded files follows 
the scheme file.mp3 and file_n.mp3, n being the consecutive number, starting 
at 1.

Note: this downloader is not supported by the WDR broadcasting organization, 
thus is inofficial! The current application supplements 
[Streamripper](https://streamripper.sourceforge.net/) 
that creates a native audio file from a broadcaster's mp3 livestream.

I found no way to downgrade the bitrate of the mp3 file to a smaller 
size without having to install **ffmpeg** or an add-on for **sox** locally. 
Hence, we created a mp3 downsize [script](https://github.com/Tamburasca/WDR3_concert_downloader/blob/master/src/mp3_downgrade.py)

    $ python3 mp3_downgrader/ -f <factor> -i <file>.mp3 [-h] [-o <file>.mp3]

where a factor is to be supplied in the range [0.1, 1.0[ 
that is multiplied with the bitrate of the 
input file. Simultaneously, the audio quality is downgraded. 
The output file name is optional.

Furthermore, in a first draft, we provide an Internet Radio on a 
web server based on FastAPI utilizing its *StreamingResponse*.
Running in a Docker container it streams mp3-files that are provided
in a directory as specified in *.env* - one after another, randomly selected.
Text as "metadata" is injected between the byte stream chunks, if the client
exhibits the attribute *icy-metadata* = '1' in its request header.
For the time being we utilize metadata of the mp3-files that 
comprise title, album and genre. We got two solutions, comprising both an 
asynchronous and a synchronous version of the streaming server.

The internetradio is invoked by addressing the following endpoint

    http://<your host ip>:5010/api/webradio

Owing to the nature of the web server another mp3 file is streamed after 
each call of above endpoint. 